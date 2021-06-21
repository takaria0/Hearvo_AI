import pickle
from datetime import datetime, date, timedelta

from ..settings import db, ML_MODEL_DIR, BUCKET_NAME, storage_client
from ..utils import set_start_date_end_date




def open_target_tree_pickle(start_date, end_date):
  """
  start_date: '2021-06-01'
  end_date: '2021-06-17'
  get target month pickle
  """
  
  # filename = f'{ML_MODEL_DIR}{start_date}_{end_date}'
  # print('filename: ', filename)
  # with open(f'{ML_MODEL_DIR}{start_date}_{end_date}.pickle', 'rb') as f:
  #     (tree, mlb, user_info_id_list) = pickle.load(f)

  try:
    gcs_filename = f'close_users/{start_date}_{end_date}.pickle'
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(gcs_filename)
    (tree, mlb, user_info_id_list) = pickle.loads(blob.download_as_string())
  except:
    import traceback; traceback.print_exc()
    raise Exception

  if (not tree) or (not mlb):
    raise Exception
  
  return mlb, tree, user_info_id_list



def fetch_user_post_voted_list_from_db(user_info_id, start_date, end_date):
  """
  date: '2021-06'
  fetch data from the first day of the month to yesterday

  e.g. TODAY = 2021-06-22
  use data between
  start_day = 2021-06-01
  yesterday = 2021-06-21

  return data, a list of post_id

  e.g.
  data = [1, 50, 40, 55, 33, 22, ...]
  """

  start_date = datetime.strptime(start_date, '%Y-%m-%d')
  end_date = datetime.strptime(end_date, '%Y-%m-%d')


  try:
    cur = db.cursor()
    cur.execute(
      f"""
      SELECT user_info_id, post_id 
      FROM user_info_post_voted
      WHERE
      user_info_id = {user_info_id}
      AND
      created_at BETWEEN '{start_date}'::timestamp AND '{end_date}'::timestamp
      """
      )
    rows = cur.fetchall()
    data = [row[1] for row in rows]
    print(f"fetched data size: {len(data)}")

  except:
    raise Exception

  return data



def data_to_feature_vector(mlb, data):
  """
  """
  X = mlb.transform([data])
  return X


def get_k_nearest_users(tree, X, user_info_id, k=5, user_info_id_list=None):
  print("-"*100 + "\n" + "-"*100)
  print(f"compute nearest {k} users to user_info_id={user_info_id} from the tree")
  dist, ind = tree.query(X, k=k)
  ind = ind[0]

  print(f"{ind=}")
  close_users = [user_info_id_list[close_idx] for close_idx in ind]
  print(f"closest users to user_info_id={user_info_id} are: {close_users}") 
  return close_users





def predict_close_users(user_info_id, input_date, k):
  today = date.today()
  start_date, end_date = set_start_date_end_date(today)

  mlb, tree, user_info_id_list = open_target_tree_pickle(start_date, end_date)
  data = fetch_user_post_voted_list_from_db(user_info_id, start_date, end_date)
  X = data_to_feature_vector(mlb, data)

  close_user_info_id_list = get_k_nearest_users(tree, X, user_info_id, k=k, user_info_id_list=user_info_id_list)
  return close_user_info_id_list


