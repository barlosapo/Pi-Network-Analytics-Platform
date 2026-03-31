import psycopg2
from dotenv import load_dotenv
import os
import random
from datetime import datetime, timedelta

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)
cursor = conn.cursor()

blocklists = [
    ("doubleclick.net", "Google Ads tracker"),
    ("googleadservices.com", "Google Ads"),
    ("facebook.com", "Social media tracker"),
    ("scorecardresearch.com", "Analytics tracker"),
    ("outbrain.com", "Ad network"),
    ("taboola.com", "Ad network"),
    ("ads.twitter.com", "Twitter Ads"),
    ("amazon-adsystem.com", "Amazon Ads"),
    ("moatads.com", "Ad tracker"),
    ("pubmatic.com", "Ad exchange"),
]

print("Inserting blocklists...")
for domain, reason in blocklists:
    cursor.execute("INSERT INTO blocklists (domain_name, reason) VALUES (%s, %s) ON CONFLICT (domain_name) DO NOTHING", (domain, reason))

clients = [
    ("iPhone - Carlos", "192.168.12.50"),
    ("MacBook Pro", "192.168.12.51"),
    ("iPad", "192.168.12.52"),
    ("Smart TV", "192.168.12.53"),
    ("Xbox", "192.168.12.54"),
]

print("Inserting clients...")
for name, ip in clients:
    cursor.execute("INSERT INTO clients (device_name, ip_address) VALUES (%s, %s) ON CONFLICT (ip_address) DO NOTHING", (name, ip))

conn.commit()

cursor.execute("SELECT id FROM clients")
client_ids = [r[0] for r in cursor.fetchall()]

cursor.execute("SELECT id, domain_name FROM blocklists")
blocked_domains = {r[1]: r[0] for r in cursor.fetchall()}

allowed_domains = [
    "google.com", "youtube.com", "netflix.com", "spotify.com",
    "github.com", "stackoverflow.com", "reddit.com", "espn.com",
    "apple.com", "amazon.com", "twitter.com", "instagram.com",
    "linkedin.com", "cnn.com", "weather.com", "nytimes.com",
    "twitch.tv", "discord.com", "slack.com", "zoom.us"
]

query_types = ["A", "AAAA", "CNAME", "MX", "PTR"]

print("Inserting 2000 DNS queries...")
now = datetime.now()
count = 0

for i in range(2000):
    minutes_ago = random.randint(0, 7 * 24 * 60)
    ts = now - timedelta(minutes=minutes_ago)
    client_id = random.choice(client_ids)
    query_type = random.choices(query_types, weights=[70, 10, 10, 5, 5])[0]
    if random.random() < 0.25:
        domain = random.choice(list(blocked_domains.keys()))
        status = "blocked"
        blocklist_id = blocked_domains[domain]
    else:
        domain = random.choice(allowed_domains)
        status = "allowed"
        blocklist_id = None
    cursor.execute("INSERT INTO dns_queries (client_id, domain_name, query_type, timestamp, status, blocklist_id) VALUES (%s, %s, %s, %s, %s, %s)", (client_id, domain, query_type, ts, status, blocklist_id))
    count += 1

conn.commit()
cursor.close()
conn.close()
print(f"Done — {count} DNS queries inserted.")
