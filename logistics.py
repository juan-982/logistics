import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta

def is_order_late(pickup_date, first_delivery_date, second_delivery_date, sla):
  effective_sla = get_effective_sla(pickup_date, sla)

  days = get_day_difference(pickup_date, first_delivery_date)

  if days > effective_sla:
    return 1

  # No second delivery
  if second_delivery_date is None:
    return 0

  # Cannot be more than 3 days
  effective_sla = get_effective_sla(first_delivery_date, 3)

  days = get_day_difference(first_delivery_date, second_delivery_date)

  if days > effective_sla:
    return 1

  return 0

def get_sla(origin, destination):
  if "metro manila" in origin.lower():
    if "metro manila" in destination.lower():
      return 3
    elif "luzon" in destination.lower():
      return 5
  elif "luzon" in origin.lower():
    if "metro manila" in destination.lower() or "luzon" in destination.lower():
      return 5

  return 7

def get_effective_sla(start_date, sla):
  rest_days = [
    "2020-03-01",
    "2020-03-08",
    "2020-03-15",
    "2020-03-22",
    "2020-03-25",
    "2020-03-29",
    "2020-03-30",
    "2020-03-31",
    "2020-04-05",
    "2020-04-12",
    "2020-04-19",
    "2020-04-26",
  ]

  end_date = start_date + timedelta(days=sla)

  effective_sla = sla

  for rest_day in rest_days:
    day = datetime.strptime(rest_day, "%Y-%m-%d").date()

    if day < start_date:
      continue
    elif day > end_date:
      break
    else:
      # If time period contains Sunday or public holiday, extend SLA
      effective_sla += 1
      end_date = end_date + timedelta(days=1)

  return effective_sla

def get_day_difference(start_date, end_date):
  delta = end_date - start_date
  return delta.days


def get_date_from_epoch(epoch):
  return datetime.fromtimestamp(float(epoch)).date()

df = pd.read_csv("open-shopee-code-league-logistic/delivery_orders_march.csv")

orderids = []
is_late = []

for index, row in df.iterrows():
  pickup_date = get_date_from_epoch(row["pick"])
  first_delivery_date = get_date_from_epoch(row["1st_deliver_attempt"])
  second_delivery_date = None if np.isnan(row["2nd_deliver_attempt"]) else get_date_from_epoch(row["2nd_deliver_attempt"])

  origin = row["selleraddress"]
  destination = row["buyeraddress"]

  sla = get_sla(origin, destination)

  orderids.append(row["orderid"])

  is_late.append(is_order_late(pickup_date, first_delivery_date, second_delivery_date, sla))

  if index % 1000 == 0:
    print(index)

#export to csv
orders = {
  "orderid" : orderids,
  "is_late" : is_late,
}

pd.DataFrame(orders, columns=["orderid", "is_late"]).to_csv('result.csv', index = False)

