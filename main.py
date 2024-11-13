import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
def datas(x):
  city = str(x) #Ensure text is a string
  api_key = 'your token'
  url = f'https://api.waqi.info/feed/{city}/?token={api_key}' #Construct url from requested city and api key
  response = requests.get(url) #Send api request
  return response.json() #Return dict containing data
def forecast_data(data): #extract air quality forecast
  dates_list = []
  dates = (data['data']['forecast']['daily']['pm25'])[::] #list of dicts containing data for requested day starting on two day before current day
  for i in dates:
    dates_list.append((i['day'],i['max'],i['avg'],i['min'])) #turn dicts into lists
  return dates_list #return a list composing of date, max aqi, average aqi, and minimum aqi
def aqi(data): #extract current air quality
  aqi_datas = data['data']['aqi'] #retireve aqi data for today
  return aqi_datas #return aqi data
def example(data): #classify air quality into catagories
  aqi_data = data['data']['aqi']
  if int(aqi_data) <= 50:
    st = "Good"
  elif int(aqi_data) <= 100:
    st = "Moderate"
  elif int(aqi_data) <= 150:
    st = "Unhealthy for Sensitive Group"
  elif int(aqi_data) <= 200:
    st = "Unhealthy"
  elif int(aqi_data) <= 300:
    st = "Very Unhealthy"
  elif int(aqi_data) == 999:
    st = "Wut(You should NOT be alive lmao)"
  else:
    st = "Hazardous"
  return st #return severity of pollution
def graph(dates_list):
  plt.clf()
  day_vals = []
  max_vals = []
  avg_vals = []
  min_vals = []
  tdate = []
  for i in dates_list: #make list of dates, max aqis, average aqis, and minimum aqis from several list containing such data sorted by date
    day_vals.append(i[0][5::]) #remove year from dates
    max_vals.append(i[1])
    avg_vals.append(i[2])
    min_vals.append(i[3])
  ndays = np.arange(len(avg_vals))
  slope, y_intercept = np.polyfit(ndays, avg_vals, 1)
  trend = slope*ndays+y_intercept
  values = []
  for i in dates_list:
    values.append([i[1], i[2], i[3]])
  for i in range(len(values)):
    values[i].append(trend[i])
  df = pd.DataFrame(values, columns = ["max", "avg", "min", "trend"], index = day_vals)
  st.line_chart(df, color = ["#00FF00", "#FF0000", "#0000FF", "#EE00FF"])
  return
def colors(data):
  aqi_data = data["data"]["aqi"]
  if aqi_data <= 100:
    return "green"
  elif aqi_data <= 150:
    return "orange"
  else:
    return "red"
st.title("Welcome!")
st.header("Air quality of top 5 popular cities in Thailand")
topdata = {"city": [], "air quality": []}
topcities = ["Bangkok", "Chiang Mai", "Chiang Rai", "Chonburi", "Phuket"]
for topcity in topcities:
    try:
        topdata["city"].append(topcity)
        topdata["air quality"].append(example(datas(topcity)))
    except:
        pass
topdf = pd.DataFrame(topdata)
st.table(topdf)
st.divider()
st.subheader("For more details, type the name of any city in the world")
city = st.text_input("City name", placeholder = "City")
cont_button = st.button("Continue", type="primary")
if cont_button and city:
    try:
        data = datas(city)
        if data["data"] != "Unknown station": 
            if aqi(data) != "-":
              st.divider()
              st.header(city.title())
              st.subheader("Real-Time AQI:")
              color = colors(data)
              st.write(str(aqi(data)))
              st.write(f"**level:** :{color}[{example(data)}]")
              with st.expander("level evaluation criteria"):
                st.write('''Levels of the AQI values are determined with the following table.''')
                st.image("https://www.researchgate.net/publication/342389902/figure/fig1/AS:905570932498447@1592916343797/Air-Quality-Index-levels-of-health-concern-AQI-values-as-a-yardstick-that-runs-from-0.jpg")
              st.divider()
              st.subheader("Forecast & 2 days Historical data")
              graph(forecast_data(data)) 
              with st.expander("See Explanation"):
                st.write('''The graph above shows maximum, average, minimum, and trend of AQI value 
                from 2 days historical data up to 7 days ahead forecast,''')
            else:
              st.write("AQI data is unavaliable for this station") 
        else:
            st.write(":red[Data is unavlaiable for this city or this city doesn't exist]")
    except:
        st.write("An unexpected error occured")   
elif cont_button and not city:
  st.write(":red[Please enter a city name.]")
