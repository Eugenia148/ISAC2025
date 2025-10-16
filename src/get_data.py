# ==========================================
# get_data.py
# Connection to the API and data download
# ==========================================

## Install packages
#pip install python-dotenv
#pip install os
#pip install pandas
#pip install numpy

## Packages
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from statsbombpy import sb
from mplsoccer.pitch import VerticalPitch
from matplotlib.colors import LinearSegmentedColormap
from dotenv import load_dotenv

# Import centralized configuration
from config import get_statsbomb_client, is_premium_access

# Get authenticated StatsBomb client
sb = get_statsbomb_client()

## Parameters
DATA_DIR = "../data"       # Carpeta donde se guardarán los datos
TEAM = "Manchester United" # Poner el nombre del equipo
COMP_ID = 2                # Competición (ejemplo: Premier League)
SEASON_ID = 281            # Temporada (ejemplo: 2023/2024)
