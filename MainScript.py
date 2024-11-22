#Samantha Pasciullo Boychuck & Ally Finkbeiner
#slp87@duke.edu & amf145@duke.edu
#Duke University Nicholas School of the Environment
# November 22, 2024

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
