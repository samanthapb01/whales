# Samantha Pasciullo Boychuck & Ally Finkbeiner
# slp87@duke.edu & amf145@duke.edu
# Duke University Nicholas School of the Environment
# November 22, 2024

# This script prompts the user to input only a month and day. This is how it differs from InputLoopScript.py.
# It prints a statement that tells the user if an observation occurred on that day.
# If an observation was recorded, it prints the associated coordinates, time, SST, and year.
# We thought this could be interesting so users could compare coordinates and temperatures for the same date across the years to note any changes.
# This Python script is comparable in function to our ToolInputScriptFinal.py.


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

# Format date time column and split
gdf_whales_filtered['date_time'] = pd.to_datetime(gdf_whales_filtered['date_time'])
gdf_whales_filtered['date'] = gdf_whales_filtered['date_time'].dt.date
gdf_whales_filtered['time'] = gdf_whales_filtered['date_time'].dt.time
gdf_whales_filtered['date_string'] = gdf_whales_filtered['date'].astype(str)
gdf_whales_filtered['year'] = gdf_whales_filtered['date_string'].str[:4]
gdf_whales_filtered['month_day'] = gdf_whales_filtered['date_string'].str[-5:]

# Save updated file as csv
gdf_whales_filtered.to_csv('U:\\whales\\Data\\updated_gdf_whales_filtered.csv', index=False)

# Access SST layer
sst_layer = gis.content.get('100a26c4d15445ffadab0d04e536b9c1').layers[0]

# Convert the SST layer to a multidimensional raster object
sst_raster = Raster(sst_layer.url, is_multidimensional=True)

# Prompt user for a date input
input_date_str = input("Please enter the date (MM-DD) to search for observations: ")

# Filter the data for observations that match the input date
filtered_gdf = gdf_whales_filtered[gdf_whales_filtered['month_day'] == input_date_str]

# Check if there are any observations for the input date
if filtered_gdf.empty:
    print(f"No observations found for {input_date_str}.")
else:
    # Initialize an empty list to store SST values
    sst_values = []

    # Loop through the rows of the filtered whale observations
    for index, row in filtered_gdf.iterrows():
        # Create a point for the current row
        the_point = Point({
            'x': row['longitude'],
            'y': row['latitude'],
            'spatialReference': {'wkid': 4326}  # WGS84 Spatial Reference
        })

        # Convert input_date to datetime.datetime object at midnight
        start_datetime = row['date_time'] # Combine date with midnight time
        end_datetime = start_datetime + timedelta(hours=1)  # Add one hour to define the end time

        # Use the input date for the time_extent (same start and end time)
        sst_result = sst_layer.identify(
            geometry=the_point,
            time_extent=[start_datetime, end_datetime],  # Use input date for time
            process_as_multidimensional=True,
        )
        
        # Check if 'value' is present and valid
        if 'value' in sst_result:
            if sst_result['value'] != 'NoData':  # Check if the result is 'NoData'
                try:
                    the_sst = float(sst_result['value'])  # Convert to float
                    sst_values.append(the_sst)  # Store the value

                     # Extract the observation time from the 'time' column
                    observation_time = row['time']
                    observation_year = row['year']
                    
                    # Report the SST value
                    print(f'At the point ({the_point.x}, {the_point.y}) on {input_date_str} in {observation_year} at {observation_time} the SST was {the_sst} degrees Celsius.')
                except ValueError:
                    print(f"Warning: Invalid SST value at point ({the_point.x}, {the_point.y}) on {row['date_time']}.")
                    sst_values.append(None)  # Optionally, append None for invalid data
            else:
                print(f"No data available for point ({the_point.x}, {the_point.y}) on {row['date_time']}.")
                sst_values.append(None)  # Optionally, append None for NoData
        else:
            print(f"Error: SST value missing for point ({the_point.x}, {the_point.y}) on {row['date_time']}.")
            sst_values.append(None)  # Optionally, append None for missing value