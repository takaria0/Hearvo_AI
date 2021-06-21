import os
import json

import psycopg2
from google.cloud import storage
from google.oauth2 import service_account


DATABASE_URL = os.environ.get("DATABASE_URL", None)

BUCKET_NAME = os.environ.get("BUCKET_NAME", "hearvo-ai-dev")


try:
  db = psycopg2.connect(DATABASE_URL)
  print("Database opened successfully")
except:
  print("Failed to connect database")



ML_MODEL_DIR = os.environ.get("ML_MODEL_DIR", './ml_models/close_users/')



json_str = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
gcp_project = os.environ.get('GCP_PROJECT') 
json_data = json.loads(json_str)
json_data['private_key'] = json_data['private_key'].replace('\\n', '\n')
credentials = service_account.Credentials.from_service_account_info(json_data)
storage_client = storage.Client(project=gcp_project, credentials=credentials)