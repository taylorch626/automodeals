# -*- coding: utf-8 -*-

'''This is automated code to add and commit the updated all_cars.csv file to GitHub'''

import subprocess as cmd
import datetime as datetime

def uploadRepository():
	try:
		cmd.run("git add data/all_cars_test_from_py_UPDATED.csv", check=True, shell=True)
		cont = 1
	except:
		print('Adding crashed!')
		cont = 0
		
	message = str(datetime.datetime.now()) + ' - Uploaded newer cars to all_cars_test_from_py_UPDATED.csv'

	if cont == 1:
		try:
			cmd.check_call(['git'] + ['commit', '-m', f'{message}'])
			cont = 1
		except:
			print('Committing crashed!')
			cont = 0

	if cont == 1:
		try:
			cmd.run("git pull project master", check=True, shell=True)
			cont = 1
		except:
			print('Pulling crashed!')
			cont = 0

	if cont == 1:
		try:
			cmd.run("git push project master", check=True, shell=True)
		except:
			print('Pushing crashed!')