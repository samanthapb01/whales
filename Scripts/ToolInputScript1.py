# Samantha Pasciullo Boychuck & Ally Finkbeiner
# slp87@duke.edu & amf145@duke.edu
# Duke University Nicholas School of the Environment
# December 3, 2024

# This script is meant to be attached to an ArcGIS Pro tool. It is our initial trial of making a tool script.
# It prompts the user to input a month, day, and year. This script only runs if year is inputted.
# Ideally, we wanted year to be optional. (We figure that out in ToolInputScriptFinal.py...)
# It prints a statement that tells the user if an observation occurred on that day.
# If an observation was recorded, it prints the associated coordinates, time, and SST.
# This tool script is comparable in function to our InputLoopScript.py.


# Import packages
import arcpy
import pandas as pd
from datetime import datetime, timedelta
from arcgis.gis import GIS
from arcgis.raster import Raster

# Get parameters from the user
day = arcpy.GetParameterAsText(0) 
month = arcpy.GetParameterAsText(1)  
year = arcpy.GetParameterAsText(2)  
whale_csv = arcpy.GetParameterAsText(3)  # Path to whale observation CSV

# Convert day, month, and year to a single date string
date_query = f"{int(month):02d}-{int(day):02d}"  # Format as "MM-DD"
if year:
    date_query = f"{int(year):04d}-{date_query}"  # Format as "YYYY-MM-DD"
target_date = datetime.strptime(date_query, "%Y-%m-%d")

# Load the whale observation CSV using pandas
df = pd.read_csv(whale_csv)

# Filter the DataFrame for the input date
whale_obs = df[df["date"] == date_query]

# Check if there are any observations for the input date
if whale_obs.empty:
    arcpy.AddMessage(f"No observations found for {date_query}.")
else:
     # Connect to GIS (assumes user is already logged in)
    gis = GIS("home")
    
    sst_layer = gis.content.get('100a26c4d15445ffadab0d04e536b9c1').layers[0]

    # Convert the SST layer to a multidimensional raster object
    sst_raster = Raster(sst_layer.url, is_multidimensional=True, gis = gis)

    # Check available time dimensions
    time_values = sst_raster.get_dimension_values(
        variable_name="sst", dimension_name="StdTime"
    )
    # Initialize an empty list to store SST values
    sst_values = []

    # Loop through the rows of the filtered whale observations
    for index, row in whale_obs.iterrows():
        the_point = {
        "x": float(row['longitude']), 
        "y": float(row['latitude']),  
        "spatialReference": {"wkid": 4326}  
    }

        # Set start and end time
        start_datetime_str = row['date_time'] 
        start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
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
                    arcpy.AddMessage(f"At the point ({the_point['x']}, {the_point['y']}) on {date_query} in {observation_year} at {observation_time} the SST was {the_sst} degrees Celsius.")
                except ValueError:
                    arcpy.AddMessage(f"Warning: Invalid SST value at point ({the_point['x']}, {the_point['y']}) on {row['date_time']}.")
                    sst_values.append(None)  # Optionally, append None for invalid data
            else:
                arcpy.AddMessage(f"No data available for point ({the_point['x']}, {the_point['y']}) on {row['date_time']}.")
                sst_values.append(None)  # Optionally, append None for NoData
        else:
            arcpy.AddMessage(f"Error: SST value missing for point ({the_point['x']}, {the_point['y']}) on {row['date_time']}.")
            sst_values.append(None)  # Optionally, append None for missing value