# ====================== Importing Packeges & Read params ======================

import re
import sys
import json
import argparse
import warnings
import requests
import cloudscraper
import numpy             as np
import pandas            as pd
import seaborn           as sns
import matplotlib.pyplot as plt

from itertools                          import count
from bs4                                import BeautifulSoup
from selenium                           import webdriver
from google.cloud                       import bigquery
from urllib.request                     import urlopen
from selenium.webdriver.common.by       import By
from scrapy.utils.log                   import configure_logging
from selenium.webdriver.common.keys     import Keys
from IPython.display                    import set_matplotlib_formats
from selenium.webdriver.chrome.service  import Service
from selenium.webdriver.chrome.options  import Options
from selenium.webdriver.support.ui      import WebDriverWait
from webdriver_manager.chrome           import ChromeDriverManager
from selenium.webdriver.support         import expected_conditions as EC

# ==============================================================================


# ============================== Collecting data ===============================