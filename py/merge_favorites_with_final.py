# -*- coding: utf-8 -*-

import pandas as pd


# load files
cars_path = '../cars.pkl'
cars_fav_path = '../data/all_cars_final.csv'
cars_df = pd.read_pickle(cars_path)
cars_fav_df = pd.read_csv(cars_fav_path)
all_idx = cars_df.columns.union(cars_fav_df.columns,sort=False)


# index by URL before trying to merge
cars_link = cars_df.reindex(columns=all_idx).set_index('link')
cars_fav_link = cars_fav_df.set_index('link')

# merge with new data from favorites csv
cars_merged = cars_link.combine_first(cars_fav_link)

cars_merged = cars_merged.reset_index()
cars_merged = cars_merged[all_idx.tolist()]

cars_merged.to_csv('../data/all_cars.csv', index=False)