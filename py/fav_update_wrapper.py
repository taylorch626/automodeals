# -*- coding: utf-8 -*-

from merge_all_with_fav import merge_all_with_fav
from favorites_views_updater import favorites_views_updater


cars_path = 'data/all_cars.csv'
cars_fav_path = 'data/all_cars_view_fav.csv'

cars_df = merge_all_with_fav(cars_path,cars_fav_path)

#cars_df = cars_df.iloc[:5]
#cars_df = cars_df.iloc[-5:]

updated_cars = favorites_views_updater(cars_df)

updated_cars.to_csv('data/all_cars_view_fav.csv',index=False)
