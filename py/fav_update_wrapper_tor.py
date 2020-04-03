# -*- coding: utf-8 -*-

from merge_all_with_fav import merge_all_with_fav
from favorites_views_updater_tor import favorites_views_updater_tor

cars_path = '../data/all_cars.csv'
cars_fav_path = '../data/all_cars_view_fav.csv'

cars_df = merge_all_with_fav(cars_path,cars_fav_path)

# cars_df = cars_df.iloc[:5]
#cars_df = cars_df.iloc[-5:]

tor_location = r"C:\Users\Paskett\AppData\Roaming\tor\tor-win32-0.4.2.7\Tor\tor.exe"
updated_cars = favorites_views_updater_tor(cars_df,tor_location)

updated_cars.to_csv('data/all_cars_view_fav_tor.csv',index=False)
print(updated_cars.head())