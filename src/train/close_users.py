import os
import json
import pickle
import traceback
from datetime import datetime, date, timedelta

import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.neighbors import KDTree
from google.cloud import storage
from google.oauth2 import service_account

from ..settings import db, ML_MODEL_DIR, BUCKET_NAME, storage_client
from ..utils import set_start_date_end_date


def fetch_user_post_voted_list_from_db(start_date, end_date):
  """
  date: '2021-06'
  fetch data from the first day of the month to yesterday

  e.g. TODAY = 2021-06-22
  use data between
  start_day = 2021-06-01
  yesterday = 2021-06-21
  """

  start_date = datetime.strptime(start_date, '%Y-%m-%d')
  end_date = datetime.strptime(end_date, '%Y-%m-%d')

  try:
    """
    Large? How many rows do we get here.
    """
    cur = db.cursor()
    cur.execute(
      f"""
      SELECT user_info_id, post_id
      FROM user_info_post_voted
      WHERE
      created_at BETWEEN '{start_date}'::timestamp and '{end_date}'::timestamp
      """
      )
    rows = cur.fetchall()

    data = pd.DataFrame()
    data["user_info_id"] = [row[0] for row in rows]
    data["post_id"] = [row[1] for row in rows]

    print("Fetched data from the db correctly")
    print(f"length of data: {len(data)}")
    # db.close()

  except:
    print("Failed to load data from the db")
    # db.close()
    raise Exception

  return data



def get_groupby_list(user_post_id):
  print("-"*100 + "\n" + "-"*100)
  data = dict(user_post_id.groupby("user_info_id")["post_id"].apply(list))
  return data

def create_user_info_id_to_post_id_list(data):
  print("-"*100 + "\n" + "-"*100)
  user_info_id_to_post_id_list = [{"user_info_id":key, "post_id_list": value} for key, value in data.items()]
  return user_info_id_to_post_id_list

def drop_users_who_voted_less_than_k(data, k=0):
  print("-"*100 + "\n" + "-"*100)
  print(f"original size: {len(data)}")
  data = [da for da in data if len(da["post_id_list"]) > k-1]
  print(f"dropped size: {len(data)}")
  return data


def one_hot_encode(data):
  print("-"*100 + "\n" + "-"*100)
  print("start one hot encode")

  all_post_id_list = [da["post_id_list"] for da in data]
  mlb = MultiLabelBinarizer(sparse_output=False)
  categorical_post_id_list = mlb.fit_transform(all_post_id_list)

  user_info_id_to_post_id_list = [{"user_info_id": da["user_info_id"], "post_id_list": da["post_id_list"], "onehot_post_id_list": cat} for da, cat in zip(data, categorical_post_id_list)]
  X = categorical_post_id_list
  print(f"X size {X.shape}")

  return user_info_id_to_post_id_list, X, mlb

def train_KDTree(X):
  print("-"*100 + "\n" + "-"*100)
  print("train KDTree")
  tree = KDTree(X)
  return tree


def save_data_to_GCS(data, destination_blob_name):
  """Uploads a file to the bucket."""
  # The ID of your GCS bucket
  # bucket_name = "your-bucket-name"
  # The path to your file to upload
  # source_file_name = "local/path/to/file"
  # The ID of your GCS object
  # destination_blob_name = "storage-object-name"


  try:
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(data)

    print("File uploaded to {}.".format(destination_blob_name))
  except:
    traceback.print_exc()

  return



def main(today):
  """
  preprocess
  1: drop unnessesary columns
  2: create user_id to post_id_list
  3: drop users who voted less than ten
  """
  start_date, end_date = set_start_date_end_date(today, mode="train")
  print(f"{start_date=}")
  print(f"{end_date=}")

  data = fetch_user_post_voted_list_from_db(start_date, end_date)
  data = get_groupby_list(data)
  data = create_user_info_id_to_post_id_list(data)
  data = drop_users_who_voted_less_than_k(data, 1)

  """
  1: post_id to one hot vector and prepare train X matrix
  2: train KDTree
  3: compute closest users from the tree
  """
  user_info_id_to_post_id_list, X, mlb = one_hot_encode(data)
  tree = train_KDTree(X)
  user_info_id_list = [data["user_info_id"] for data in user_info_id_to_post_id_list]

  """
  save trained data to Google Cloud Storage
  """
  gcs_savedata_name = f'close_users/{start_date}_{end_date}.pickle'
  data = pickle.dumps((tree, mlb, user_info_id_list))
  save_data_to_GCS(data, gcs_savedata_name)
  """
  save trained data to Local (dont have to do though)
  """
  with open(f'{ML_MODEL_DIR}{start_date}_{end_date}.pickle', 'wb') as f:
      pickle.dump((tree, mlb, user_info_id_list), f)
  return


"""
main
"""
main(date.today())


"""
for bulk create trained models
"""
# import time
# for i in range(1, 8):
#   for j in range(1, 32):
#     # today = date.today()
#     print("date:", 2021, i, j)
    
#     try:
#       today = date(2021, i, j)
#       main(today)
#     except:
#       pass
#     time.sleep(1)
      