import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

#Functions
def datas(x):
  city = str(x) #Ensure text is a string [Note: make a rejection system]
  api_key = 'PASTE API KEY' #Get Token
  url = f'https://api.waqi.info/feed/{city}/?token={api_key}' #Receive AQI data from desired city using token
  response = requests.get(url) #open url
  return response.json()

def forecast_data(data):
  dates_list = []
  dates = (data['data']['forecast']['daily']['pm25'])[2::]
  for i in dates:
    dates_list.append((i['day'],i['max'],i['avg'],i['min']))
  return dates_list

def aqi(data):
  aqi_datas = data['data']['aqi'] #retireve aqi data
  return aqi_datas

def example(data):
  aqi_data = data['data']['aqi']
  if int(aqi_data) <= 50: # print air quality
    st = "Good"
  elif int(aqi_data) <= 100:
    st = "Decent"
  elif int(aqi_data) <= 150:
    st = "Bad for Sensitive Group"
  elif int(aqi_data) <= 200:
    st = "Bad"
  elif int(aqi_data) <= 300:
    st = "Extremely Bad"
  elif int(aqi_data) == 999:
    st = "Wut"
  else:
    st = "Hazardous"
  return st

def graph(dates_list):
  plt.clf()
  day_vals = []
  values = []
  for i in dates_list:
    day_vals.append(i[0][5::])
    values.append([i[1], i[2], i[3]])
  df = pd.DataFrame(values, columns = ["max", "avg", "min"], index = day_vals)
  st.line_chart(df, color = ["#00FF00", "#FF0000", "#0000FF"])  # Display the plot
  return

#Displays
city = st.selectbox(
    "Province", 
    ("Bangkok", "Chiang Mai", "Chiang Rai", "Chonburi",
    "Kamphaeng Phet", "Kanchanaburi", "Khon Kaen", "Krabi",
    "Lampang", "Lamphun", "Loei", "Nakhon Pathom", "Nakhon Phanom", "Nakhon Ratchasima",
    "Nakhon Sawan", "Nakhon Si Thammarat", "Nan", "Narathiwat",
    "Nong Khai", "Nonthaburi", "Pathum Thani", "Pattani",
    "Phatthalung", "Phayao", "Phitsanulok",
    "Phra Nakhon Si Ayutthaya", "Phrae", "Phuket", "Prachuap Khiri Khan",
    "Ratchaburi", "Rayong", "Sakon Nakhon", "Samut Prakan",
    "Samut Sakhon", "Samut Songkhram", "Saraburi", "Satun", "Suphan Buri", "Surat Thani", "Tak", "Trang",
    "Trat", "Ubon Ratchathani", "Udon Thani", "Uthai Thani", "Uttaradit", "Yala"),
    index = None,
    placeholder = "Choose any of the avaliable provinces"
    )
try:
    data = datas(city)
    if data is not None:
        st.write(aqi(data))
        st.write(example(data))
        graph(forecast_data(data))
except:
  st.write("Choose a province for air quality information")
