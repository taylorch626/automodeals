# -*- coding: utf-8 -*-

'''AddNewerCarstoRepository loads the existing all_cars.csv and then checks cars.ksl.com
for any used cars that the .csv doesn't already have (based on the posting date).

This script was mostly copied from the jupyter notebook of the same name on 3/23/20'''

# Import section
# from bs4 import BeautifulSoup # if this isn't installed, use pip install beautifulsoup4
# import requests
# import re
import pandas as pd
import numpy as np
from datetime import datetime
# import time
# import progressbar # if this isn't installed, use pip install progressbar2
# import random
# from selenium import webdriver # if not installed, do pip install selenium
# from itertools import cycle

# Import subfunctions
from generateProxies import generateProxies
from carscraper import carscraper
from removeduplicates import removeduplicates


# Load dataframe
all_cars = pd.read_csv('data/all_cars_test_from_py.csv')

# Convert post_date back to datetime
all_cars['post_date'] = pd.to_datetime(all_cars['post_date'])

# get most recent timestamp from the dataframe
rep_ts = datetime.timestamp(all_cars['post_date'].max())


# Now scrape for more cars and check for timestamp

# determine whether or not to use proxy IPs. Can use boolean or int for this
use_proxy = False

# Define root url for KSL cars
rooturl = "https://cars.ksl.com"

lurl = "https://cars.ksl.com/search/newUsed/Used;Certified/perPage/96/page/"

count = 0
newer_cars = []
moreresults = 1
while moreresults:
	url = lurl + str(count)
    
	try:
		if use_proxy:
			curr_cars, moreresults, currproxy, proxydict = carscraper(url=url, rooturl=rooturl, maxts=rep_ts, use_proxy=use_proxy, currproxy=currproxy, refreshmin = 15, proxydict = proxydict)
		else:
			curr_cars, moreresults = carscraper(url=url, rooturl=rooturl, maxts=rep_ts, use_proxy=use_proxy)
	except:
		if use_proxy:
			curr_cars, moreresults, currproxy, proxydict = carscraper(url=url, rooturl=rooturl, maxts=0, use_proxy=use_proxy, refreshmin = 15)
		else:
			pass
    
	count += 1    
#     print(f'More results? {moreresults}')
	if type(curr_cars) is pd.core.frame.DataFrame: # make sure real data was returned
		try:
			newer_cars = pd.concat([newer_cars, curr_cars], ignore_index=True)
		except:
			newer_cars = curr_cars
	else:
		print('No newer car data found!')
	
	# TEMPORARY: add in hard stop after a couple of pages
	if count == 2:
		moreresults = 0
		print('HARD STOP added here by TCH on 3/23/20')
    
# add newer_cars
if type(newer_cars) is pd.core.frame.DataFrame:
	all_cars = pd.concat([newer_cars, all_cars], ignore_index=True)
	

# Remove any duplicate rows

all_cars = removeduplicates(all_cars)

# Save updated dataframe to csv


all_cars.to_csv('data/all_cars_test_from_py_UPDATED.csv', index=False)