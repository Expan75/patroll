import json
import os
import numpy as np
import requests as reqs
import pandas as pd
from bs4 import BeautifulSoup

# directories consts
DATA_DIR = "data/raw"
HTML_DIR = os.path.join(DATA_DIR, "en_20200101_html")

# test load of html to extract JSON
file = os.path.join(HTML_DIR, "A01B.htm")

with open(file) as f:
    soup = BeautifulSoup(markup=f, features="lxml")

data = soup.find_all("script", attrs={"type": "text/javascript"})