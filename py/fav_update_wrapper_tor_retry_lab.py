# -*- coding: utf-8 -*-

from merge_all_with_fav import merge_all_with_fav
from favorites_views_updater_tor_retry import favorites_views_updater_tor_retry

cars_path = '../data/all_cars.csv'
cars_fav_path = '../data/all_cars_view_fav_tor_lab.csv'

cars_df = merge_all_with_fav(cars_path,cars_fav_path)
cars_df = cars_df.reset_index()

# cars_df = cars_df.iloc[:5]
#cars_df = cars_df.iloc[-10:].reset_index()

#tor_location = r"C:\Users\Paskett\AppData\Roaming\tor\tor-win32-0.4.2.7\Tor\tor.exe"
tor_location = r"C:\Users\Michael Paskett\AppData\Roaming\tor\Tor\tor.exe"
updated_cars = favorites_views_updater_tor_retry(cars_df,tor_location,use_tor=1,only_new=1)

updated_cars.to_csv('../data/all_cars_view_fav_tor_lab_final.csv',index=False)
print(updated_cars.head())