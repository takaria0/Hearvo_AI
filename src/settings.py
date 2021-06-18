import os
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL", None)

try:
  db = psycopg2.connect(DATABASE_URL)
  print("Database opened successfully")
except:
  print("Failed to connect database")



ML_MODEL_DIR = os.environ.get("ML_MODEL_DIR", './ml_models/close_users/')