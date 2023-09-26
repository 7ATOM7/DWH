#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
import pandas as pd
import os
from sqlalchemy import create_engine, text
import random
from datetime import timedelta
import time


# In[3]:

# Data Integration to Landind Zone:-

JSONPLACEHOLDER_ENDPOINT = "https://jsonplaceholder.typicode.com/users"


# In[4]:


response = requests.get(JSONPLACEHOLDER_ENDPOINT)


# In[5]:


response.raise_for_status()


# In[6]:


users_data = response.json()


# In[7]:


users_df=pd.read_json(response.text)


# In[8]:

#Doing minimal data transformations like flattening
address_df = users_df['address'].apply(pd.Series)
geo_df = address_df['geo'].apply(pd.Series)
geo_df.columns = ['geo_' + col for col in geo_df.columns]  # Prefix columns with 'geo_'
users_df = pd.concat([users_df.drop(['address'], axis=1), address_df.drop(['geo'], axis=1), geo_df], axis=1)

# Flattening the 'company' column
company_df = users_df['company'].apply(pd.Series)
company_df.columns = ['company_' + col for col in company_df.columns]  # Prefix columns with 'company_'
users_df = pd.concat([users_df.drop(['company'], axis=1), company_df], axis=1)
sales_data_path = os.path.join('..', 'Data', 'sales_data.csv')
sales_df = pd.read_csv(sales_data_path)


# In[9]:

#Writing to the landing zone hosted on a postgresql database
# Connect to PostgreSQL
DATABASE_URL = "postgresql://username:password@postgres:5432/postgres"
engine = create_engine(DATABASE_URL)
print(type(engine))

# In[10]:

print(engine)
engine.execute('create schema landing;')


# In[11]:


users_df.to_sql("users_string", engine, if_exists='replace', index=False, schema='landing')


# In[12]:


sales_data_path = os.path.join('..', 'Data', 'sales_data.csv')


# In[13]:


sales_df = pd.read_csv(sales_data_path)
sales_df.to_sql("sales_string", engine, if_exists='replace', index=False, schema='landing')


# In[14]:


users_df = pd.read_sql('SELECT * FROM landing.users_string', engine)

users_df['latitude'] = pd.to_numeric(users_df['geo_lat'])

users_df['longitude'] = pd.to_numeric(users_df['geo_lng'])

sales_df = pd.read_sql('SELECT * FROM landing.sales_string', engine)


# In[15]:


coordinates_list = [
    (24.4539, 54.3773),  # Abu Dhabi
    (25.276987, 55.296249),  # Dubai
    (25.3463, 55.4209)  # Sharjah
]


# In[16]:


chosen_coordinates = random.choices(coordinates_list, k=len(sales_df))


# In[17]:


sales_df['latitude'] = [coord[0] for coord in chosen_coordinates]
sales_df['longitude'] = [coord[1] for coord in chosen_coordinates]


# In[18]:


def random_time_delta():
    hours = random.randint(9, 20)
    minutes = random.randint(0, 59)
    seconds = random.randint(0, 59)
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


# In[20]:


sales_df['order_date'] = pd.to_datetime(sales_df['order_date'])
sales_df['timestamp'] = sales_df['order_date'] + sales_df['order_date'].apply(lambda x: random_time_delta())
sales_df['timestamp_bigint'] = (sales_df['timestamp'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')


# In[21]:
#Added the correct datatypes for respective columns and inserting them into the foundation schema. 

# Modify data types for the specified columns
sales_df['order_id'] = sales_df['order_id'].astype('int64')  # or 'bigint' for PostgreSQL
sales_df['customer_id'] = sales_df['customer_id'].astype('int64')  # or 'bigint' for PostgreSQL
sales_df['product_id'] = sales_df['product_id'].astype('int64')  # or 'bigint' for PostgreSQL
sales_df['quantity'] = sales_df['quantity'].astype(int)
sales_df['price'] = sales_df['price'].astype(float)
sales_df['longitude'] = sales_df['longitude'].astype(float)
sales_df['latitude'] = sales_df['latitude'].astype(float)
sales_df['timestamp_bigint']= sales_df['timestamp_bigint'].astype(float)


# In[22]:


engine.execute('create schema foundation;')


# In[23]:


sales_df.to_sql("sales_fnd", engine, if_exists='replace', index=False, schema='foundation')


# In[24]:


users_df['id'] = users_df['id'].astype(int)
users_df['latitude'] = users_df['latitude'].astype(float)
users_df['longitude'] = users_df['longitude'].astype(float)


# In[25]:


users_df.to_sql("users_fnd", engine, if_exists='replace', index=False, schema='foundation')


# In[26]:

#Fetching the weather data
def fetch_weather_data(timestamp_bigint, latitude, longitude, session):
    BASE_URL = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
    url = f"{BASE_URL}?lat={latitude}&lon={longitude}&dt={int(timestamp_bigint)}&appid=c9a79ec429ab88c7a24d164ac2e66cb3"
    
    response = session.get(url)
    
    if response.status_code != 200:
        print(f"Error for timestamp {timestamp_bigint}: {response.status_code}")
        return pd.Series({'temp': None, 'humidity': None, 'description': None, 'wind_speed': None})
    
    data = response.json()['data'][0]
    return pd.Series({
        'temp': data['temp'],
        'humidity': data['humidity'],
        'description': data['weather'][0]['description'],
        'wind_speed': data['wind_speed']
    })


# In[27]:


with requests.Session() as session:
    weather_columns = sales_df.apply(
        lambda row: fetch_weather_data(row['timestamp_bigint'], row['latitude'], row['longitude'], session),
        axis=1
    )


# In[28]:


sales_df = pd.concat([sales_df, weather_columns], axis=1)


# In[29]:


engine.execute('create schema reporting;')


# In[30]:


#Convert temperature from Kelvin to Celsius
sales_df['temp_celsius'] = sales_df['temp'] - 273.15

#Create bins of size 3 degrees for the Celsius data
bins = list(range(int(sales_df['temp_celsius'].min()), int(sales_df['temp_celsius'].max()) + 4, 3))

#Use pd.cut() to categorize the Celsius values into these bins
sales_df['temp_bins'] = pd.cut(sales_df['temp_celsius'], bins, right=False)


# In[31]:


bins = list(range(0, 101, 10))
labels = [f"{i}-{i+9}" for i in range(0, 100, 10)]
sales_df['humidity_bin'] = pd.cut(sales_df['humidity'], bins=bins, labels=labels, right=False, include_lowest=True)


# In[32]:


sales_df['temp_bins'] = sales_df['temp_bins'].astype(str)


# In[33]:

#Creating the datamart in reporting schema and preparing the table for reporting.
sales_df['humidity_bin'] = sales_df['humidity_bin'].astype(str)


# In[34]:


dm_sales_user = sales_df.merge(users_df, left_on='customer_id', right_on='id', how='left')


# In[35]:


dm_sales_user.to_sql('dm_sales_reporting',engine,if_exists='replace',index=False, schema='reporting')

