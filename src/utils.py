from datetime import datetime, date, timedelta

def set_start_date_end_date(today):
  """
  return start_date and end_date for training data
  train data between start_date and end_date

  start_date: the first day of the month
  end_date: yesterday
  """
  start_date = today.strftime("%Y-%m-01")

  print("today.day", today.day)
  """
  if today is the 1st day of the month
  compute previous month's data 
  
  e.g. today: 2021-10-01 then compute

  start_date: 2021-09-01
  end_date: 2021-09-31
  """
  if today.day == 1:
    delta_one_day = timedelta(days=1)
    start_date = (today - delta_one_day).strftime("%Y-%m-01")
    end_date = (today - delta_one_day).strftime("%Y-%m-%d")
  else:
    delta_oneday = timedelta(days=1)
    end_date = (today - delta_oneday).strftime("%Y-%m-%d")
  return start_date, end_date
