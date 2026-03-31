# Pi-Network Analytics Platform

An end-to-end data pipeline that captures, stores, and visualizes network-level DNS query data from a Pi-hole ad blocker.

## Project Goals
- Deploy Pi-hole on a Raspberry Pi running Linux as a network-wide DNS filter
- Build a Python ETL pipeline to extract, clean, and load query data into PostgreSQL
- Design a normalized database schema to store DNS query and client data
- Deliver a live dashboard visualizing key network metrics

## Tech Stack
- **Hardware:** Raspberry Pi 3 Model B
- **OS:** Raspberry Pi OS Lite (Linux)
- **Dev Environment:** Ubuntu 24.04 LTS (UTM VM)
- **Pipeline:** Python (pandas, psycopg2)
- **Database:** PostgreSQL (Supabase)
- **Dashboard:** TBD

## Metrics Tracked
- Total queries vs blocked queries — block rate %
- Top 10 blocked domains
- Query volume by hour
- 7-day block rate trend
- Top requesting clients by device
- Breakdown by category — ads, trackers, malware, social media

## Project Structure
- `etl_pipeline.py` — Extract, Transform, Load script
- `sql/schema.sql` — Database schema
- `requirements.txt` — Python dependencies
- `.env` — Environment variables (not committed to GitHub)

## Setup
Coming soon
