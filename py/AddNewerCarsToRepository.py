# -*- coding: utf-8 -*-

'''AddNewerCarstoRepository loads the existing all_cars.csv and then checks cars.ksl.com
for any used cars that the .csv doesn't already have (based on the posting date).

This script was mostly copied from the jupyter notebook of the same name on 3/23/20'''

# Import section
import pandas as pd
import numpy as np
from datetime import datetime

# Import subfunctions
from generateProxies import generateProxies
from carscraper import carscraper
from removeduplicates import removeduplicates

def AddNewerCarsToRepository():


	# Load dataframe
	all_cars = pd.read_csv('data/all_cars.csv')

	# Convert post_date back to datetime
	all_cars['post_date'] = pd.to_datetime(all_cars['post_date'])
	
	# Load the exisiting repository's links
	
	prev_links = set(all_cars['link'])

	# Now scrape for more cars and check for new links

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
		print(f'The next search page is: {url}')
		
		try:
			if use_proxy:
				curr_cars, moreresults, currproxy, proxydict = carscraper(url=url, rooturl=rooturl, prev_links=prev_links, use_proxy=use_proxy, currproxy=currproxy, refreshmin = 20, proxydict = proxydict)
			else:
				curr_cars, moreresults = carscraper(url=url, rooturl=rooturl, prev_links=prev_links, use_proxy=use_proxy)
		except:
			if use_proxy:
				curr_cars, moreresults, currproxy, proxydict = carscraper(url=url, rooturl=rooturl, prev_links=prev_links, use_proxy=use_proxy, refreshmin = 20)
			else:
				pass
		
		count += 1    
	    # print(f'More results? {moreresults}')
		if type(curr_cars) is pd.core.frame.DataFrame: # make sure real data was returned
			try:
				newer_cars = pd.concat([newer_cars, curr_cars], ignore_index=True)
				
				# Remove any duplicate rows
				newer_cars = removeduplicates(newer_cars)

				# update prev_links
				prev_links = prev_links.union(set(newer_cars['link']))
				print(f'Updated prev_links! There are now {len(prev_links)} to check against.')
			except:
				newer_cars = curr_cars
				
				# Remove any duplicate rows
				newer_cars = removeduplicates(newer_cars)

				# update prev_links
				prev_links = prev_links.union(set(newer_cars['link']))
				print(f'Updated prev_links! There are now {len(prev_links)} to check against.')
		elif not moreresults:
			print('************ Found end of new data ************')
		else:
			print('No newer car data found!')
		
		# TEMPORARY: add in hard stop after a reasonable # of pages to expect in a single day
		if count == 100:
			moreresults = 0
			print(f'HARD STOP at {count} pages added here by TCH on 3/23/20')
		
	# add newer_cars
	if type(newer_cars) is pd.core.frame.DataFrame:
		all_cars = pd.concat([newer_cars, all_cars], ignore_index=True)
		

	# Remove any duplicate rows

	all_cars = removeduplicates(all_cars)
	
	
    # Save updated dataframe to csv
	try:
		dailynm = f'data/daily/all_cars_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
		all_cars.to_csv(dailynm, index=False)
	except:
		print()
		print("Couldn't save daily csv to data/daily directory")
	
	# Save updated dataframe to csv

	all_cars.to_csv('data/all_cars.csv', index=False)

	return all_cars.shape[0]