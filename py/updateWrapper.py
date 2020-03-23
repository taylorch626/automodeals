# -*- coding: utf-8 -*-

'''This script is used to automate updating of the all_cars.csv repository and should be used in tandem with a task scheduler.'''

import subprocess as cmd
import datetime as datetime

# cmd.run("echo 'Test of auto print function'", check=True, shell=True)

try:
	cmd.run("git add data\all_cars_test_from_py_UPDATED.csv", check=True, shell=True)
except:
	print('Adding crashed!')

try:
	cmd.run("git commit -m '{datetime.datetime.now()} - Uploaded newer cars to all_cars_from_py_UPDATED.csv'", check=True, shell=True)
except:
	print('Committing crashed!')
	
try:
	cmd.run("git pull project master", check=True, shell=True)
except:
	print('Pulling crashed!')

try:
	cmd.run("git push project master", check=True, shell=True)
except:
	print('Pushing crashed!')