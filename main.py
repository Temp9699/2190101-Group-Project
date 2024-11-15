#import required libraries
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests

#functions

#request information about "x" city from the api
def datas(x): #Return
  city = str(x) #Ensure text is a string
  api_key = '8f241a22c0906922d8ea84aef5c119e0978791b8'#insert your api token here
  url = f'https://api.waqi.info/feed/{city}/?token={api_key}' #Construct url from requested city and api key
  response = requests.get(url) #Send api request
  return response.json() #Return dict containing data

#extract date, min aqi, average aqi, and  max aqi from data which is in json format
def forecast_data(data): #extract air quality forecast
  dates_list = []
  dates = (data['data']['forecast']['daily']['pm25'])[::] #list of dicts containing data for requested day starting on two day before current day
  for i in dates:
    dates_list.append((i['day'],i['max'],i['avg'],i['min'])) #turn dicts into lists
  return dates_list #return a list composing of date, max aqi, average aqi, and minimum aqi

#extract live aqi value from data which is in json format
def aqi(data): #extract current air quality
  aqi_datas = data['data']['aqi'] #retireve aqi data for today
  return aqi_datas #return aqi data

#classify air quality into catagories
def example(data): 
  aqi_data = data['data']['aqi']
  #conditions for each categories
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
  else:
    st = "Hazardous"
  return st #return severity of pollution

#plot graphs of 2 days historical data and 7 day forecast
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

  #calculate trend
  ndays = np.arange(len(avg_vals))
  slope, y_intercept = np.polyfit(ndays, avg_vals, 1)
  trend = slope*ndays+y_intercept

  #Format data into pandas Dataframe for plotting onto graph
  values = []
  for i in dates_list:
    values.append([i[1], i[2], i[3]])
  for i in range(len(values)):
    values[i].append(trend[i])
  df = pd.DataFrame(values, columns = ["max", "avg", "min", "trend"], index = day_vals)
  
  #graph a streamlit line chart
  st.line_chart(df, color = ["#00FF00", "#FF0000", "#0000FF", "#EE00FF"])

#make a table of 2 days historical data and 7 day forecast
def table_forecast(dates_list):
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

  #calculate trend
  ndays = np.arange(len(avg_vals))
  slope, y_intercept = np.polyfit(ndays, avg_vals, 1)
  trend = slope*ndays+y_intercept
  
  #Format data into pandas Dataframe for plotting onto table
  values = []
  for i in dates_list:
    values.append([i[1], i[2], i[3]])
  for i in range(len(values)):
    values[i].append(trend[i])
  df = pd.DataFrame(values, columns = ["max", "avg", "min", "trend"], index = day_vals)

  #graph a streamlit table
  st.table(df)

#assign colors to display air quality levels
def colors(data):
  aqi_data = data["data"]["aqi"]
  #conditions for assigning each colors
  if aqi_data <= 100:
    return "green"
  elif aqi_data <= 150:
    return "orange"
  else:
    return "red"

#UI
st.title("Welcome!")

#This section shows a table of 5 cities in Thailand: "Bangkok", "Chiang Mai", "Chiang Rai", "Chonburi", and "Phuket"
st.header("Air quality of top 5 popular cities in Thailand")
#Formatting into pandas Dataframe
topdata = {"city": [], "air quality": []}
topcities = ["Bangkok", "Chiang Mai", "Chiang Rai", "Chonburi", "Phuket"]
for topcity in topcities:
    try:
        #Dataframes contain 2 rows: "city" and "air quality"
        #Insert each city and get the city's air quality level from the api
        topdata["city"].append(topcity)
        topdata["air quality"].append(example(datas(topcity)))
    except:
        pass
topdf = pd.DataFrame(topdata)
#Display as a table
st.table(topdf)

#This section accepts user input of what city do they want a detailed data
st.divider()
st.subheader("For more details, type the name of any city in the world")
city = st.text_input("City name", placeholder = "City")
cont_button = st.button("Continue", type="primary")

#display informations if user have filled in the text input and clicked the continue button
if cont_button and city:
    try:
        #getting information about the input city
        data = datas(city)
        #Validate user input
        if data["data"] != "Unknown station": 
            #Check if the API has an information of this city
            if aqi(data) != "-":
              #Display detailed aqi information of the city
              st.divider()
              st.header(city.title())
              #Display aqi at the time
              st.subheader("Real-Time AQI:")
              color = colors(data)
              st.write(str(aqi(data)))
              #Display the categorized aqi level and determine the color of the text
              st.write(f"**level:** :{color}[{example(data)}]")
              #Information to the user on how the aqi is categorized
              with st.expander("level evaluation criteria"):
                st.write('''Levels of the AQI values are determined with the following table.''')
                st.image("https://www.researchgate.net/publication/342389902/figure/fig1/AS:905570932498447@1592916343797/Air-Quality-Index-levels-of-health-concern-AQI-values-as-a-yardstick-that-runs-from-0.jpg")
              st.divider()

              #plot a graph of 7 days forecast data and 2 days historical data
              st.subheader("Forecast & 2 days Historical data")
              #Disclaimer: Some version of python has trouble plotting streamlit graph
              try: #try plotting graph
                graph(forecast_data(data)) 
                #explain the graph
                with st.expander("See Explanation"):
                  st.write('''The graph above shows maximum, average, minimum, and trend of AQI value 
                  from 2 days historical data up to 7 days ahead forecast,''')
              except:#create a teble instead if there's error plotting graph
                table_forecast(forecast_data(data))
            #If aqi information is unavaliable for this city
            else:
              st.write("AQI data is unavaliable for this station") 
        #If the input city doesn't exist
        else:
            st.write(":red[Data is unavlaiable for this city or this city doesn't exist]")
    #In case of having any error
    except Exception as e:  
        st.write(e)
#if the user press continue without typing a city name
elif cont_button and not city:
  st.write(":red[Please enter a city name.]")
