# -*- coding: utf-8 -*-

'''This script is used to automate updating of the all_cars.csv repository and should be used in tandem with a task scheduler. It should be run from just within the automodeals directory so that the subfunction dependencies work out properly. For example, in Windows cmd, cd to the automodeals directory and then run
>python3 py\\updateWrapper.py'''

from datetime import datetime

print(f'Start time is {datetime.now().strftime("%B %d, %Y %H:%M:%S")}')

from AddNewerCarsToRepository import AddNewerCarsToRepository as ANCTR
from uploadRepository import uploadRepository

# Scrape for the most recent cars
all_cars = ANCTR()

# Save updated dataframe to backup daily csv
try:
	dailynm = f'data/daily/all_cars_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
	all_cars.to_csv(dailynm, index=False)
except:
	dailynm = None
	print()
	print("Couldn't save backup daily csv to data/daily directory")

# commit and push to git
uploadRepository(all_cars.shape[0], dailynm=dailynm)