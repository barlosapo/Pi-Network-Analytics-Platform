import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Pi-Network Analytics", page_icon="🛡️", layout="wide")

@st.cache_resource
def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

conn = get_conn()

st.title("🛡️ Pi-Network Analytics Platform")
st.markdown("**Live DNS query analytics — Raspberry Pi + Python ETL + PostgreSQL**")
st.divider()

# Row 1 — KPI metrics
total = pd.read_sql("SELECT COUNT(*) AS total FROM dns_queries", conn).iloc[0,0]
blocked = pd.read_sql("SELECT COUNT(*) AS blocked FROM dns_queries WHERE status='blocked'", conn).iloc[0,0]
block_rate = round(100 * blocked / total, 2)
clients = pd.read_sql("SELECT COUNT(DISTINCT client_id) AS c FROM dns_queries", conn).iloc[0,0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Queries", f"{total:,}")
col2.metric("Blocked Queries", f"{blocked:,}")
col3.metric("Block Rate", f"{block_rate}%")
col4.metric("Active Devices", clients)

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top 10 Blocked Domains")
    df_top = pd.read_sql("""
        SELECT domain_name, COUNT(*) AS hits
        FROM dns_queries WHERE status='blocked'
        GROUP BY domain_name ORDER BY hits DESC LIMIT 10
    """, conn)
    fig1 = px.bar(df_top, x="hits", y="domain_name", orientation="h",
                  color="hits", color_continuous_scale="Reds")
    fig1.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("Query Volume by Hour")
    df_hour = pd.read_sql("""
        SELECT EXTRACT(HOUR FROM timestamp) AS hour, COUNT(*) AS queries
        FROM dns_queries GROUP BY hour ORDER BY hour
    """, conn)
    fig2 = px.line(df_hour, x="hour", y="queries", markers=True,
                   color_discrete_sequence=["#F5A623"])
    st.plotly_chart(fig2, use_container_width=True)

col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("7-Day Block Rate Trend")
    df_trend = pd.read_sql("""
        SELECT DATE(timestamp) AS day,
        ROUND(100.0 * SUM(CASE WHEN status='blocked' THEN 1 ELSE 0 END)/COUNT(*), 2) AS block_pct
        FROM dns_queries GROUP BY day ORDER BY day
    """, conn)
    fig3 = px.line(df_trend, x="day", y="block_pct", markers=True,
                   color_discrete_sequence=["#06D6A0"])
    st.plotly_chart(fig3, use_container_width=True)

with col_right2:
    st.subheader("Queries by Device")
    df_clients = pd.read_sql("""
        SELECT c.device_name, COUNT(*) AS queries
        FROM dns_queries q JOIN clients c ON q.client_id=c.id
        GROUP BY c.device_name ORDER BY queries DESC
    """, conn)
    fig4 = px.pie(df_clients, values="queries", names="device_name",
                  color_discrete_sequence=px.colors.sequential.Teal)
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.subheader("Category Breakdown")
df_cat = pd.read_sql("""
    SELECT b.reason, COUNT(*) AS blocked_count
    FROM dns_queries q JOIN blocklists b ON q.blocklist_id=b.id
    GROUP BY b.reason ORDER BY blocked_count DESC
""", conn)
fig5 = px.bar(df_cat, x="reason", y="blocked_count",
              color="blocked_count", color_continuous_scale="Oranges")
st.plotly_chart(fig5, use_container_width=True)
