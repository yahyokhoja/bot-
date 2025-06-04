import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()
cursor.execute("SELECT * FROM orders")
print(cursor.fetchall())
conn.close()
