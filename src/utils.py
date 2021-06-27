from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

def set_start_date_end_date(input_date, mode="train"):
  """
  e.g.
  input_date: "2021-06"
  
  return start_date and end_date for training data
  train data between start_date and end_date

  start_date: the first day of the month
  end_date: yesterday
  """

  """
  input_date = today
  """
  if mode == "train":
    try:
      input_date = datetime.strptime(input_date, "%Y-%m-%d")
    except:
      raise ValueError("Invalid date for training")
    
    
    start_date = input_date.strftime("%Y-%m-01")

    print("today.day", input_date.day)
    """
    if today is the 1st day of the month
    compute previous month's data 
    
    e.g. today: 2021-10-01 then compute

    start_date: 2021-09-01
    end_date: 2021-09-31
    """
    if input_date.day == 1:
      delta_one_day = timedelta(days=1)
      start_date = (input_date - delta_one_day).strftime("%Y-%m-01")
      end_date = (input_date - delta_one_day).strftime("%Y-%m-%d")
    else:
      delta_oneday = timedelta(days=1)
      end_date = (input_date - delta_oneday).strftime("%Y-%m-%d")
    return start_date, end_date



  if mode == "prediction":
    """
    predict close users of current month or in the past
    
    e.g. 
    today: 2021-06-20
    
    date: 2021-06
    prediction: 2021-06-01 to 2021-06-19
    
    date: 2021-04
    prediction: 2021-04-01 to 2021-04-31
    """
    
    try:
      input_date = datetime.strptime(input_date, "%Y-%m")
    except:
      raise ValueError("Invalid date for prediction")
    
    this_month = date.today().strftime("%Y-%m")
    
    if this_month == input_date.strftime("%Y-%m"):
      start_date = input_date.strftime("%Y-%m-01")
      next_month = input_date + relativedelta(months=1)
      end_date = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")
      
    else:
      start_date = input_date.strftime("%Y-%m-01")
      next_month = input_date + relativedelta(months=1)
      end_date = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")
    
    return start_date, end_date
    