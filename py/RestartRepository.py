# -*- coding: utf-8 -*-

'''RestartRepository checks cars.ksl.com for any and all used cars on the entire website
and generates an exhaustive repository called all_cars.csv with various features
scraped from each listing page.

This script was mostly copied from the jupyter notebook of the same name on 3/23/20'''

# Import section
import pandas as pd
import numpy as np

# Import subfunctions
from generateProxies import generateProxies
from carscraper import carscraper
from removeduplicates import removeduplicates
from determinemaxpg import determinemaxpg

# Check to make sure user truly intends to restart data from scratch
choice = input("\nYou are about to restart the all_cars repository from scratch. Proceed? (y/n): ")
choice = choice.lower()

if choice == "y":
	print('Regenerating all_cars repository...')

	# Regenerate repository from scratch

	prev_links = set() # make a dummy set to check links against

	# determine whether or not to use proxy IPs. Can use boolean or int for this
	use_proxy = True

	# set cap for number of search pages to load (i.e. pages with up to 96 listings)
	maxpg = determinemaxpg() + 10 # add 10 as a buffer to account for newer cars added since start time
	maxpg = 2
	print(f'Maximum number of search pages to scrape: {maxpg}')

	# Define root url for KSL cars
	rooturl = "https://cars.ksl.com"

	# Note the url below specifies that we're looking for 96 per page and the default sort of newest to oldest posting
	# This note about newest to oldest is useful so that we can avoid scraping repeat listings based on their timestamps
	# Also note that this url does NOT have a page number associated with it. This is added in the while loop below
	lurl = "https://cars.ksl.com/search/newUsed/Used;Certified/perPage/96/page/"

	count = 0
	all_cars = []
	moreresults = 1
	while count < maxpg:
		url = lurl + str(count)
		print(f'Next page is {url}')
		try:
			if use_proxy:
				curr_cars, moreresults, currproxy, proxydict = carscraper(url=url, rooturl=rooturl, prev_links=prev_links, use_proxy=use_proxy, currproxy=currproxy, refreshmin = 15, proxydict = proxydict)
			else:
				curr_cars, moreresults = carscraper(url=url, rooturl=rooturl, maxts=0, use_proxy=False)
			
		except:
			if use_proxy:
				curr_cars, moreresults, currproxy, proxydict = carscraper(url=url, rooturl=rooturl, prev_links=prev_links, use_proxy=use_proxy, refreshmin = 15)
			else:
				pass
			
		
		count += 1    
	    # print(f'More results? {moreresults}')
		if type(curr_cars) is pd.core.frame.DataFrame: # make sure real data was returned
			try:
				all_cars = pd.concat([all_cars, curr_cars], ignore_index=True)
				
				# Remove any duplicate rows
				all_cars = removeduplicates(all_cars)

				# update prev_links
				prev_links = prev_links.union(set(all_cars['link']))
				print(f'Updated prev_links! There are now {len(prev_links)} to check against.')
			# except:
				all_cars = curr_cars
				
				# Remove any duplicate rows
				all_cars = removeduplicates(all_cars)

				# update prev_links
				prev_links = prev_links.union(set(all_cars['link']))
				print(f'Updated prev_links! There are now {len(prev_links)} to check against.')
		else:
			print('No car data found!')
			

	# Remove any duplicate rows

	all_cars = removeduplicates(all_cars)
	

	# Save dataframe to csv

	all_cars.to_csv('data/all_cars.csv', index=False)

else:
	print('Aborted!')