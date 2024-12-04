#Samantha Pasciullo Boychuck & Ally Finkbeiner
#slp87@duke.edu & amf145@duke.edu
#Duke University Nicholas School of the Environment
#November 22, 2024

#This script loops through every gray whale data entry and prints a statement stating the associated coordinates, time, and SST. 


# Import packages
from arcgis import GIS
from arcgis.raster import ImageryLayer, Raster
from arcgis.geometry import Point
from datetime import datetime, timedelta
import pandas as pd
import geopandas as gpd
import arcpy
import sys

# Connect to GIS via ArcGIS Pro
gis = GIS("home")

# Set default environment
arcpy.env.workspace = "U:\\whales"
arcpy.env.overwriteOutput = True

# Import csv
df_original = pd.read_csv('U:\\whales\\Data\\gray_whale_observations.csv')
df = df_original[['row_id', 'latitude', 'longitude', 'date_time', 'organism_id']]

# Create the geoseries from the X and Y columns
geom = gpd.points_from_xy(x=df['longitude'], y=df['latitude'])

# Convert to a geodataframe, setting the CRS to WGS 84 (wkid=4326)
gdf_whales = gpd.GeoDataFrame(df, geometry=geom, crs=4326)

# Remove points in Russia using masks
mask = (gdf_whales['longitude'] < 177) & (gdf_whales['longitude'] > -169)
gdf_whales_filtered = gdf_whales.loc[mask]

# Format data time column and split
gdf_whales_filtered['date_time'] = pd.to_datetime(gdf_whales_filtered['date_time'])
gdf_whales_filtered['date'] = gdf_whales_filtered['date_time'].dt.date
gdf_whales_filtered['time'] = gdf_whales_filtered['date_time'].dt.time

#Access SST layer
sst_layer = gis.content.get('100a26c4d15445ffadab0d04e536b9c1').layers[0]

# Convert the SST layer to a multidimensional raster object
sst_raster = Raster(sst_layer.url, is_multidimensional=True)

# Create a list to store the SST values 
sst_values = []  

# Loop through all rows in the filtered whale observations dataframe  
for index, row in gdf_whales_filtered.iterrows():  
    # Extract longitude, latitude, and date  
    longitude = row['longitude'] 
    latitude = row['latitude']  
    observation_time = row['date_time'] 
    
    # Ensure the point is in the correct format for the identify function
    the_point = Point({
        'x': longitude,
        'y': latitude,
        'spatialReference': {'wkid': 4326}  # WGS84 Spatial Reference
    })
    
    # Define the time extent for the query 
    start_date = observation_time  
    end_date = observation_time + timedelta(hours=1)  
    
    # Query the SST for the point
    sst_result = sst_layer.identify(
        geometry=the_point,
        time_extent=[start_date, end_date],
        process_as_multidimensional=True,
    )
    
     # Check if 'value' is present and valid
    if 'value' in sst_result:
        if sst_result['value'] != 'NoData':  # Check if the result is 'NoData'
            try:
                the_sst = float(sst_result['value'])  # Convert to float
                sst_values.append(the_sst)  # Store the value
                
                # Report the SST value
                print(f'At the point ({the_point.x}, {the_point.y}) on {start_date} the SST was {the_sst} degrees Celsius.')
            except ValueError:
                print(f"Warning: Invalid SST value at point ({the_point.x}, {the_point.y}) on {row['date_time']}.")
                sst_values.append(None)  
        else:
            print(f"No data available for point ({the_point.x}, {the_point.y}) on {row['date_time']}.")
            sst_values.append(None)
    else:
        print(f"Error: SST value missing for point ({the_point.x}, {the_point.y}) on {row['date_time']}.")
        sst_values.append(None) 

# Add the SST values as a new column to the dataframe 
gdf_whales_filtered['sst'] = sst_values  

# Save updated file as csv
gdf_whales_filtered.to_csv('U:\\whales\\Data\\updated_whales_filtered_with_sst.csv', index=False)
