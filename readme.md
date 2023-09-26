Project Documentation

Note:- Dashbard created on metabase cannot be transferred via the github due to the volume being managed. Its doable but cumbersome , refer the images in the folder for visualizations.
Sales data doesnt have timestamp value only date. we added the random timestamp value to make the visuals more engaging with the weather data.
We also added the coordinates of Abu Dhabi, Sharjah and Dubai randomly to all the sales information to make the data region specific and since the same wasnt provided.
Script will pull the data from different sources, create the different schema in the database write to them as well


Running the Platform
To run the platform, simply navigate to the project's root directory and use the following command:


   docker-compose up

This will start up all the services and containers defined in the docker-compose.yml file, setting up the environment as necessary.

ETL Script
Overview
The ETL (Extract, Transform, Load) process is a fundamental aspect of this platform. The script is designed with the principle of complete decoupling.

Decoupling Design
The ETL process is split into two main parts:

Integration to Landing Schema:

The primary intent here is to integrate all the source data into the landing schema in PostgreSQL.
For seamless and stress-free data import, all columns in the landing schema are designed to hold string data types. This ensures a smooth bulk import while reducing the potential strain on the source systems.
Foundation Schema Creation:

Once the data is in the landing schema, the next step involves modeling and creating the foundation schema.
In the foundation schema, the data undergoes transformations where necessary data type conversions are made from the generic string types used in the landing schema. This ensures the data is in the right format for further processing and analysis.
The ETL script responsible for these tasks is located in the Scripts folder.

Reporting Schema
Beyond the foundation schema, we also have the reporting schema. This schema is specially designed to contain data mart tables, which are primarily used for reporting purposes. This structured data is then fed to a reporting tool - Metabase, to facilitate the creation of insightful dashboards and reports.

All the integration and transformations logic is present in elt_script in the scripts folder.

Landing Schema:
sales:
['order_id', 'customer_id', 'product_id', 'quantity', 'price',
       'order_date', 'timestamp', 'latitude', 'longitude']
users:
['id', 'name', 'username', 'email', 'phone', 'website', 'street',
       'suite', 'city', 'zipcode', 'geo_lat', 'geo_lng', 'company_name',
       'company_catchPhrase', 'company_bs', 'latitude', 'longitude']
Foundation Layer:
(Note: This layer has data types corrected from the Landing layer and includes proper relationships)

sales:
['order_id', 'customer_id', 'product_id', 'quantity', 'price',
       'order_date', 'timestamp', 'latitude', 'longitude', 'timestamp_bigint',
       'temp', 'humidity', 'description', 'wind_speed', 'temp_celsius',
       'temp_bins', 'humidity_bin']
users:
['id', 'name', 'username', 'email', 'phone', 'website', 'street',
       'suite', 'city', 'zipcode', 'geo_lat', 'geo_lng', 'company_name',
       'company_catchPhrase', 'company_bs', 'latitude', 'longitude']

Foreign Key: customer_id references user_info.id
Relationship: Each sale is associated with one user (Many-to-One relation)
Relationship: Weather data is linked to sales data based on latitude and longitude (Potential Many-to-One relationship depending on granularity)
Reporting Layer:

datamart sales user is created and the table structure is
dm_sales_user 
['order_id', 'customer_id', 'product_id', 'quantity', 'price',
       'order_date', 'timestamp', 'latitude_x', 'longitude_x',
       'timestamp_bigint', 'temp', 'humidity', 'description', 'wind_speed',
       'temp_celsius', 'temp_bins', 'humidity_bin', 'id', 'name', 'username',
       'email', 'phone', 'website', 'street', 'suite', 'city', 'zipcode',
       'geo_lat', 'geo_lng', 'company_name', 'company_catchPhrase',
       'company_bs', 'latitude_y', 'longitude_y']

Contains data mart tables designed specifically for reporting purposes. It's intended to serve Metabase reporting needs, based on processed data from the Foundation layer.


Additional scope:-
1. In foundation layer, add scd-2 for customer information, upserts for sales data based on data volume and veracity.
2. If it's reasaonable add surrogate keys for dimensions , for faster joins. and histoty tracking
3. Add proper error handling for all of the etl operations.
4. Create seperate, aggregated tables for different reporting requirements. 
5. Schedules the jobs for the current scope using chron to start with, employ different tools like nifi or airflow upon expansion
6. Since the integration and data transformation are de-coupled, we can opt for lake storage in cloud or data center and we can deploy other execution engines like Tez, Spark, Mapreduce etc to scale 
7. Create a seperate analytical database for increased reporting requirements.
8. Tried to implement , maps based visual for UAE using GEOJson, but some rendering issue.
