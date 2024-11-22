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
df = pd.read_csv('U:\\whales\\Data\\gray_whale_observations.csv')