#Tools used to read from Pi-hole and push to Supabase PostgreSQL database
import sqlite3 # For connecting to the Pi-hole SQLite database
import psycopg2 # For connecting to the Supabase PostgreSQL database
import pandas as pd # For data manipulation and analysis
from datetime import datetime # For handling date and time data
import os # For handling file paths and environment variables
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# DATABASE CONNECTIONS
# Pi-hole SQLite database path (on the Raspberry Pi)
PIHOLE_DB = "/etc/pihole/pihole-FTL.db"

# Supabase PostgreSQL connection - values stored in environment variables
# Pull credentials from environment variables for security rather than hardcoding them in the script
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

# Extract data from Pi-hole SQLite database
# Pulls new DNS queries since the last time the script ran, based on a timestamp
def extract_pihole_data(last_run_timestamp):
    conn = sqlite3.connect(PIHOLE_DB)
    query = """
        SELECT 
            timestamp,
            domain,
            client,
            type,
            status
        FROM queries
        WHERE timestamp > ?
        ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn, params=(last_run_timestamp,))
    conn.close()
    print(f"Extracted {len(df)} new queries from Pi-hole")
    return df

# Transform the raw data into a structured format suitable for PostgreSQL
# Cleans data, maps status codes to readable values, and converts timestamps to datetime format
def transform_data(df):
    df = df.dropna(subset=["timestamp", "domain", "client"])
    df = df.drop_duplicates()
    status_map = {
        0: "unknown",
        1: "blocked",
        2: "allowed",
        3: "allowed",
        4: "allowed",
        5: "blocked",
        6: "blocked",
    }
    df["status"] = df["status"].map(status_map).fillna("unknown")
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.rename(columns={
        "client": "client_ip",
        "type": "query_type"
    })
    print(f"Transformed {len(df)} records")
    return df

# Load the cleaned data into the Supabase PostgreSQL database
# Pushes the data into dns_queries with conflict handling to avoid duplicates
def load_data(df):
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO dns_queries 
                (timestamp, domain_name, client_ip, query_type, status)
            VALUES 
                (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            row["timestamp"],
            row["domain"],
            row["client_ip"],
            row["query_type"],
            row["status"]
        ))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Loaded {len(df)} records into PostgreSQL")

# Main function to run the ETL pipeline
def main():
    print(f"ETL pipeline started at {datetime.now()}")
    last_run = int((datetime.now().timestamp()) - 86400)
    raw_data = extract_pihole_data(last_run)
    if raw_data.empty:
        print("No new queries found - exiting")
        return
    clean_data = transform_data(raw_data)
    load_data(clean_data)
    print(f"ETL pipeline completed at {datetime.now()}")

if __name__ == "__main__":
    main()
