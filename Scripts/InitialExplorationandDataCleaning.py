#Samantha Pasciullo Boychuck & Ally Finkbeiner
#slp87@duke.edu & amf145@duke.edu
#Duke University Nicholas School of the Environment
# November 22, 2024

#This script is an initial exploration of the data and includes some data organization and wrangling. 
#This is heavily based on John's demo script in ExtractDataToPoint_JohnsDemo.ipynb


#Import packages
from arcgis import GIS
from arcgis.raster import ImageryLayer, Raster
from arcgis.geometry import Point, filters
from datetime import datetime, timedelta
import pandas as pd
import geopandas as gpd
import arcpy
import sys

#Connect to GIS via ArcGIS Pro
gis = GIS("home")

#Set default environment
arcpy.env.workspace = "U:\\whales"
arcpy.env.overwriteOutput = True

#Import csv
df_original = pd.read_csv('U:\\whales\\Data\\gray_whale_observations.csv')
df = df_original[['row_id','latitude','longitude','date_time','organism_id']]

#Create the geoseries from the X and Y columns
geom = gpd.points_from_xy(x=df['longitude'],y=df['latitude'])

#Convert to a geodataframe, setting the CRS to WGS 84 (wkid=4326)
gdf_whales = gpd.GeoDataFrame(df,geometry=geom,crs=4326)

#Explore the data
gdf_whales.info()

#Plot the data
explore_plot = gdf_whales.plot(figsize=(20,15),alpha=0.6)

#Remove points in Russia using masks
mask = (gdf_whales['longitude'] < 177) & (gdf_whales['longitude'] > -169)
gdf_whales_filtered = gdf_whales.loc[mask]
gdf_whales_filtered.plot()

#Format data time column and split
gdf_whales_filtered['date_time'] = pd.to_datetime(gdf_whales_filtered['date_time'])
gdf_whales_filtered['date'] = gdf_whales_filtered['date_time'].dt.date
gdf_whales_filtered['time'] = gdf_whales_filtered['date_time'].dt.time
gdf_whales_filtered.info()

#Access SST layer
sst_layer = gis.content.get('100a26c4d15445ffadab0d04e536b9c1').layers[0]
type(sst_layer)

#Confirm the SST layer has multidimensions
sst_layer.properties.hasMultidimensions

#Convert the SST layer to a multidimensional raster object
sst_raster = Raster(sst_layer.url,is_multidimensional=True)

#Reveal the variables in the SST raster
sst_raster.variable_names

#Reveal the dimensions in the SST raster's 'sst' variable
sst_raster.get_dimension_names('sst')

#Get attributes for the 'StdTime' dimension in the SST raster
sst_raster.get_dimension_attributes(variable_name='sst', dimension_name='StdTime')

#Take a peek at the first 10 time values in the SST raster
time_values = sst_raster.get_dimension_values(variable_name='sst', dimension_name='StdTime')
print(len(time_values))
time_values[0:10]

# Ensure the point is in the correct format for the identify function (convert it to a dictionary if needed)
the_point = Point({
    'x': gdf_whales_filtered.loc[0,'longitude'],
    'y': gdf_whales_filtered.loc[0,'latitude'],
    'spatialReference': {'wkid': 4326}  # WGS84 Spatial Reference
    })

#Show the type of our point
type(the_point)

#Create datetime objects for the start and end dates
start_date = datetime(2009, 6, 22)
end_date = datetime(2009, 6, 23)

#Show the dates
print(start_date, end_date)

sst_result = sst_layer.identify(
    geometry=the_point,
    time_extent=[start_date, end_date],
    process_as_multidimensional=True,
)

#Reveal the result
sst_result

#Fetch the SST value at the point
the_sst = float(sst_result['value'])

#Report the SST value
print(f'At the point ({the_point.x}, {the_point.y}) on {start_date} the SST was {the_sst} degrees Celsius.')

#Save updated file as csv
gdf_whales_filtered.to_csv('U:\\whales\\Data\\updated_whales_filtered.csv', index=False)
