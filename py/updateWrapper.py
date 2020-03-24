# -*- coding: utf-8 -*-

'''This script is used to automate updating of the all_cars.csv repository and should be used in tandem with a task scheduler. It should be run from just within the automodeals directory so that the subfunction dependencies work out properly. For example, in Windows cmd, cd to the automodeals directory and then run
>python3 py\\updateWrapper.py'''

from AddNewerCarsToRepository import AddNewerCarsToRepository as ANCTR
from uploadRepository import uploadRepository

# Scrape for the most recent cars
newsz = ANCTR()

# commit and push to git
uploadRepository(newsz)