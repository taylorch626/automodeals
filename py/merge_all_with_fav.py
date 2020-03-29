# -*- coding: utf-8 -*-
'''
This function merges the original all_cars DataFrame with the all_cars_view_fav 
DataFrame that has additional columns. Rows are merged based on having 
identical URLs. Returns a DataFrame.

Example:
cars_path = '../data/all_cars.csv'
cars_fav_path = '../data/all_cars_view_fav.csv'
merged_df = merge_all_with_favorites(cars_path, cars_fav_path)
'''


# import libraries
import pandas as pd

def merge_all_with_favorites(cars_path, cars_fav_path):
    # load files
    cars_df = pd.read_csv(cars_path)
    cars_fav_df = pd.read_csv(cars_fav_path)
    
    # index by URL before trying to merge
    cars_link = cars_df.reindex(columns=cars_fav_df.columns).set_index('link')
    cars_fav_link = cars_fav_df.set_index('link')
    
    # merge with new data from favorites csv
    cars_merged = cars_link.combine_first(cars_fav_link)
    
    # assume cars that haven't been checked yet still have working url
    cars_merged['workingURL'] = cars_merged['workingURL'].fillna(1)
    
    cars_merged = cars_merged.reset_index()
    
    return cars_merged
