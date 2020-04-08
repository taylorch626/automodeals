# -*- coding: utf-8 -*-

'''Updates a cars_dataframe with 6 new columns (views, favorites, 
workingURL, view_rate, favorite_rate, fav_per_view).

Mostly copied from jupyter notebook of same name 3/28/20

REQUIRED INPUTS:
cars_df: data frame with information as pulled from carscraper()
VARIABLE INPUTS:
min_age: int specifying minimum age (days) listing must be before updating information. Default 1
min_last_pull: int specifying minimum time (days) since last pull for new information. Default 1
use_proxy: bool indicating to use a proxy. Default 0
proxy_dict: dictionary of proxy IPs and user agents'''

# Import libraries
import time
import random
import pandas as pd
import numpy as np
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import progressbar
from bs4 import BeautifulSoup
import datetime
from stem import Signal
from stem.control import Controller
import psutil
import os
import logging

# Create sub_functions
def get_tor_session():
    session = requests.session() # creates connection between each request made to a server, so cookies don't reset, one authentication, etc. 
    retry = Retry(connect=5, backoff_factor=0.2)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'} # for anonymization, sets Tor port
    return session

def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="KSLCars")
        controller.signal(Signal.NEWNYM)


def favorites_views_updater_tor_retry(cars_df, tor_location, **kwargs):
    '''Updates a cars_dataframe with 6 new columns (views, favorites, 
    workingURL, view_rate, favorite_rate, fav_per_view). 
    REQUIRED INPUTS:
    cars_df: data frame with information as pulled from carscraper()
    tor_location: location of tor.exe file
    VARIABLE INPUTS:
    min_age: int specifying minimum age (days) listing must be before updating information. Default 1
    min_last_pull: int specifying minimum time (days) since last pull for new information. Default 2
    use_proxy: bool indicating to use a proxy. Default 0
    proxy_dict: dictionary of proxy IPs and user agents'''
    
    # parse kwargs/set defaults
    if 'min_age' in kwargs.keys():
        if isinstance(kwargs['min_age'],int):
            min_age = kwargs['min_age']
        else:
            raise TypeError(f'Expected int for min_age but got {type(kwargs["min_age"])}.')
    else:
        min_age = 0 # days
        
    if 'min_last_pull' in kwargs.keys():
        if isinstance(kwargs['min_last_pull'],int):
            min_last_pull = kwargs['min_last_pull']
        else:
            raise TypeError(f'Expected int for min_last_pull but got {type(kwargs["min_last_pull"])}.')
    else:
        min_last_pull = 20 # days

    if 'refreshmin' in kwargs.keys():
        if isinstance(kwargs['refreshmin'],int) or isinstance(kwargs['refreshmin'],float):
            refreshmin = kwargs['refreshmin']
        else:
            refreshmin = 10
            print(f'Expected int or float for refreshmin but got {type(kwargs["refreshmin"])}. Set to default value of {refreshmin}.')
    else:
        refreshmin = 10
        print(f'No refreshmin found. Set to default value of {refreshmin}.')
        
    if 'use_tor' in kwargs.keys():
        if isinstance(kwargs['use_tor'],int) or isinstance(kwargs['use_tor'],bool):
            use_tor = kwargs['use_tor']
        else:
            use_tor = 1
            print(f'Expected int or float for use_tor but got {type(kwargs["use_tor"])}. Set to default value of {use_tor}.')
    else:
        use_tor = 1
        print(f'No "use_tor" found. Set to default value of {use_tor}.')

    if 'only_new' in kwargs.keys():
        if isinstance(kwargs['only_new'],int) or isinstance(kwargs['only_new'],bool):
            only_new = kwargs['only_new']
        else:
            only_new = 1
            print(f'Expected int or float for only_new but got {type(kwargs["only_new"])}. Set to default value of {only_new}.')
    else:
        only_new = 0
        print(f'No "only_new" found. Set to default value of {only_new}.')
                      
        
    # new columns to add if not already there
    if not 'views' in cars_df.columns:
        cars_df['views'] = np.NaN
    if not 'favorites' in cars_df.columns:
        cars_df['favorites'] = np.NaN
    if not 'workingURL' in cars_df.columns:
        cars_df['workingURL'] = 1
    if not 'view_rate' in cars_df.columns:
        cars_df['view_rate'] = np.NaN
    if not 'favorite_rate' in cars_df.columns:
        cars_df['favorite_rate'] = np.NaN
    if not 'fav_per_view' in cars_df.columns:
        cars_df['fav_per_view'] = np.NaN
        
    # set up log file
    logging.basicConfig(filename='../errors/tor_error_log.txt')
    
    # conversions to datetime
    orig_dates = cars_df['post_date']
    cars_df['post_date'] = pd.to_datetime(cars_df['post_date'])
    cars_df['lastpull_ts'] = pd.to_datetime(cars_df['lastpull_ts'], unit = 's')

    # find ads more than x days old (time.time() is in seconds)
    curr_time = pd.to_datetime(time.time(),unit='s')
    min_dt = pd.to_timedelta(min_age*60*60*24, unit='seconds') # time in seconds for use with datetime

    old_ads = cars_df['post_date'] < (curr_time - min_dt)

    # find ads that haven't been pulled for more than x days
    min_last_pull_dt = pd.to_timedelta(min_last_pull*60*60*24, unit='seconds') # time in seconds for use with datetime
    no_recent_update = cars_df['lastpull_ts'] < (curr_time - min_last_pull_dt)
    
    # find ads that have never been pulled
    never_pulled = cars_df['views'].isna()

    if only_new:
        cars_need_update = cars_df[never_pulled & cars_df['workingURL']]
    else:
        # subselect ads that need updating based on previous criteria and having a working URL last time it was checked
        cars_need_update = cars_df[old_ads & no_recent_update & cars_df['workingURL']]

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    
    # test if IP isn't blocked with generic cars.ksl.com
    if not use_tor:
        resp = requests.get('https://cars.ksl.com', headers = {'User-Agent': user_agent})
        if resp.status_code != 200: # blocked
            print('IP Blocked. Continuing with Tor')
            use_tor = 1
        
    # start tor executable if not running
    if "tor.exe" not in (p.name() for p in psutil.process_iter()):
        os.startfile(tor_location)
        time.sleep(15) # give some time for tor to get running
    
    # start new tor session
    tstart = time.time() # set a start time to use for refreshing tor
    session = get_tor_session()
    
    if cars_need_update.shape[0] != 0:
        # iterate through, pulling new information from each ad
        last_pull = []
        views = []
        favorites = []
        working_url = []
#        import pdb; pdb.set_trace()
        with progressbar.ProgressBar(max_value=len(cars_need_update.index)) as bar:
            count = 0
            for i, ad in cars_need_update.iterrows():
                # get file, first attempt without tor
                if not use_tor:
                    time.sleep(random.random()) # avoid bans
                    ad_response = requests.get(ad['link'], headers = {'User-Agent': user_agent})
                    if ad_response.status_code != 200: # get new IP
                        print(f'IP probably blocked. Running with tor')
                        use_tor = 1
                if use_tor:
                    # find how long session has been active
                    tor_ip_attempts = 0
                    if time.time() - tstart > refreshmin * 60:
                        print(f'Renewing Tor session. Exceeded refreshmin = {refreshmin} minutes')
                        renew_connection()
                        tstart = time.time()
                    while True:
                        # time.sleep(random.random()) # avoid bans
                        try:
                            ad_response = session.get(ad['link'], headers = {'User-Agent': user_agent})
                        except Exception as tor_exception:
                            print(tor_exception)
                            currTime = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(time.time()))
                            logging.error(f'{currTime}: {tor_exception}')
                        if ad_response.status_code == 200:
                            break
                        if ad_response.status_code == 404:
                            break
                        tor_ip_attempts += 1
                        if tor_ip_attempts == 5: # tor doesn't like constantly getting new connection requests
                            renew_connection() # get a new IP
                
                # Parse html
                pull_ts = pd.to_datetime(time.time(), unit='s')
                last_pull.append(pull_ts)
                ad_soup = BeautifulSoup(ad_response.content,features="lxml")
    
                # Check if link is still good (i.e. listing is still active)
                if ad_soup.title.text.strip().lower() == 'not found':
                    working_url.append(0)
                    views.append(None)
                    favorites.append(None)
                else:
                    working_url.append(1)
    
                    # get views
                    viewcount = int(ad_soup.select('span.vdp-info-value')[1].text.split()[0])
                    views.append(viewcount)
    
                    # get favorites
                    favoritecount = int(ad_soup.select('span.vdp-info-value')[2].text.split()[0])
                    favorites.append(favoritecount)
                    
                count += 1
                try:
                    bar.update(count)
                except:
                    pass
        print('Finished pulling articles. Merging new data.')
        cars_updated = cars_need_update
        cars_updated['views'] = views
        cars_updated['favorites'] = favorites
        cars_updated['lastpull_ts'] = last_pull
        cars_updated['workingURL'] = working_url
        cars_updated['fav_per_view'] = cars_updated['favorites'] / cars_updated['views']
        # rates calculated per day
        cars_updated['view_rate'] = cars_updated['views'] / ((cars_updated['lastpull_ts'] - cars_updated['post_date']).dt.total_seconds()*60*60*24)
        cars_updated['favorite_rate'] = cars_updated['favorites'] / ((cars_updated['lastpull_ts'] - cars_updated['post_date']).dt.total_seconds()*60*60*24)
    
        cars_df.update(cars_updated)
    else:
        print(f'No cars to update based on min_age = {min_age} day(s) and min_last_pull = {min_last_pull} day(s).')
    
    # update timestamps to replicate original state
    cars_df['lastpull_ts'] = (cars_df['lastpull_ts'] - datetime.datetime(1970,1,1)).dt.total_seconds().astype(int)
    cars_df['post_date'] = orig_dates
    
    # lastly, kill tor
    os.system(r"taskkill /im tor.exe")
    
    return cars_df