# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def removeduplicates(df):
	'''As the name implies, this is a function to remove duplicated dataframe rows (based on url link) before saving to .csv'''
    
	oldsize = df.shape[0]
	bool_series = df['link'].duplicated()
	if bool_series.any():
		df = df[~bool_series]
		newsize = df.shape[0]
		df = df.reset_index()
		del df['index']
		print(f'Removed {oldsize - newsize} duplicates before saving')
	return df