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
from itertools import cycle
import pandas as pd
import numpy as np
import requests
import progressbar
from bs4 import BeautifulSoup
import datetime

# Import functions
from generateProxies import generateProxies

def favorites_views_updater(cars_df, **kwargs):
    '''Updates a cars_dataframe with 6 new columns (views, favorites, 
    workingURL, view_rate, favorite_rate, fav_per_view). 
    REQUIRED INPUTS:
    cars_df: data frame with information as pulled from carscraper()
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
        min_age = 1 # days
        
    if 'min_last_pull' in kwargs.keys():
        if isinstance(kwargs['min_last_pull'],int):
            min_last_pull = kwargs['min_last_pull']
        else:
            raise TypeError(f'Expected int for min_last_pull but got {type(kwargs["min_last_pull"])}.')
    else:
        min_last_pull = 2 # days
        
    if 'use_proxy' in kwargs.keys():
        if isinstance(kwargs['use_proxy'],int) or isinstance(kwargs['use_proxy'],bool):
            use_proxy = kwargs['use_proxy']
        else:
            raise TypeError(f'Expected int or bool for use_proxy but got {type(kwargs["use_proxy"])}.')
    else:
        # default is to NOT use proxy
        use_proxy = False
    if 'random_delay' in kwargs.keys():
        if isinstance(kwargs['use_proxy'],int) or isinstance(kwargs['use_proxy'],bool):
            random_delay = kwargs['use_proxy']
        else:
            raise TypeError(f'Expected int or bool for random_delay but got {type(kwargs["use_proxy"])}.')
    else:
        # default is to have a random delay
        random_delay = True
    if 'max_wait' in kwargs.keys():
        if isinstance(kwargs['use_proxy'],int) or isinstance(kwargs['use_proxy'],bool):
            max_wait = kwargs['use_proxy']
        else:
            raise TypeError(f'Expected int or bool for max_wait but got {type(kwargs["use_proxy"])}.')
    else:
        # default is to wait up to 5 seconds
        max_wait = 5
        
    
    # the following were pulled manually on 3/12/20 from https://www.whatismybrowser.com/guides/the-latest-user-agent/
    user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/74.0',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/74.0',
                   'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/74.0',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36 Edg/80.0.361.62',
                   'Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko']
        
    if 'proxydict' in kwargs.keys():
        if isinstance(kwargs['proxydict'],dict):
            proxydict = kwargs['proxydict']
        else:
            print(f'Expected dict type for proxydict but got {type(kwargs["proxydict"])}. Generating new proxydict...')
            newproxies = generateProxies()
            proxydict = {i:random.choice(user_agents) for i in newproxies}
    else:
        print('No proxydict found. Generating...')
        newproxies = generateProxies()
        proxydict = {i:random.choice(user_agents) for i in newproxies}

    if 'refreshmin' in kwargs.keys():
        if isinstance(kwargs['refreshmin'],int) or isinstance(kwargs['refreshmin'],float):
            refreshmin = kwargs['refreshmin']
        else:
            refreshmin = 15
            print(f'Expected int or float for refreshmin but got {type(kwargs["refreshmin"])}. Set to default value of {refreshmin}.')
    else:
        refreshmin = 15
        print(f'No refreshmin found. Set to default value of {refreshmin}.')
                      
    tstart = time.time() # set a start time to use for refreshing proxy list (if needed)    

    if 'currproxy' in kwargs.keys():
        if isinstance(kwargs['currproxy'],str):
            currproxy = kwargs['currproxy']
        else:
            proxy_pool = cycle(proxydict) # make a pool of proxies 
            currproxy = next(proxy_pool) # grab the next proxy in cycle
    else:
        proxy_pool = cycle(proxydict) # make a pool of proxies 
        currproxy = next(proxy_pool) # grab the next proxy in cycle     

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

    # subselect ads that need updating based on previous criteria and having a working URL last time it was checked
    cars_need_update = cars_df[old_ads & no_recent_update & cars_df['workingURL']]

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    
    # test if IP isn't blocked with generic cars.ksl.com
    if not use_proxy:
        resp = requests.get('https://cars.ksl.com', headers = {'User-Agent': user_agent})
        if resp.status_code == 403: # blocked
            print('IP Blocked. Continuing with proxies')
            use_proxy = 1
    
#    import pdb; pdb.set_trace()
    if cars_need_update.shape[0] != 0:
        # iterate through, pulling new information from each ad
        last_pull = []
        views = []
        favorites = []
        working_url = []
        with progressbar.ProgressBar(max_value=len(cars_need_update.index)) as bar:
            for i, ad in cars_need_update.iterrows():
                if random_delay:
                    time.sleep(random.random()*max_wait) # wait up to max_wait seconds
                if use_proxy:
                    attempts = len(proxydict)
                    chkproxy = 1
                    while chkproxy:
                        if (time.time() - tstart) > 60*refreshmin: # check if it's been more than refreshmin minutes since proxy_pool updated
                            print('Refreshing proxy pool...')
                            tstart = time.time()
    
                            currproxies = set(proxydict.keys())
                            newproxies = generateProxies()
                            newproxies = newproxies.difference(currproxies)
    
                            if newproxies:
                                newdict = {i:random.choice(user_agents) for i in newproxies}
                                proxydict.update(newdict)
                                proxy_pool = cycle(proxydict)
                                currproxy = next(proxy_pool)
                                print('Proxy pool updated!')
    
                        try:
                            print(f'\nAttempting to get {ad["link"]} with proxy {currproxy}')
                            ad_response = requests.get(ad['link'],proxies={"http":currproxy, "https":currproxy},headers={'User-Agent': proxydict[currproxy]}, timeout=20)
                            print(f'\nProxy success for {currproxy}. Code: {ad_response.status_code}')
                            print()
                            chkproxy = 0
                            attempts += 1
                        except:
                            prevproxy = currproxy
                            currproxy = next(proxy_pool)
                            print(f'\nProxy error for {prevproxy}! Next up is {currproxy}')
                            attempts -= 1
                            print(f'Attempts remaining: {attempts}')
                else:
                    print(f'\nAttempting to get {ad["link"]} without proxy')
                    ad_response = requests.get(ad['link'], headers = {'User-Agent': user_agent})
                    print(f'\nSuccess, status code: {ad_response.status_code}')
                    if ad_response.status_code == 403:
                        print('IP was just blocked. Running with proxies')
                        use_proxy = 1
                        attempts = len(proxydict)
                        chkproxy = 1
                        while chkproxy:
                            if (time.time() - tstart) > 60*refreshmin: # check if it's been more than refreshmin minutes since proxy_pool updated
                                print('Refreshing proxy pool...')
                                tstart = time.time()
        
                                currproxies = set(proxydict.keys())
                                newproxies = generateProxies()
                                newproxies = newproxies.difference(currproxies)
        
                                if newproxies:
                                    newdict = {i:random.choice(user_agents) for i in newproxies}
                                    proxydict.update(newdict)
                                    proxy_pool = cycle(proxydict)
                                    currproxy = next(proxy_pool)
                                    print('Proxy pool updated!')
        
                            try:
                                print(f'\nAttempting to get {ad["link"]} with proxy {currproxy}')
                                ad_response = requests.get(ad['link'],proxies={"http":currproxy, "https":currproxy},headers={'User-Agent': proxydict[currproxy]}, timeout=20)
                                print(f'\nProxy success for {currproxy}. Code: {ad_response.status_code}')
                                print()
                                chkproxy = 0
                                attempts += 1
                            except:
                                prevproxy = currproxy
                                currproxy = next(proxy_pool)
                                print(f'Proxy error for {prevproxy}! Next up is {currproxy}')
                                attempts -= 1
                                print(f'Attempts remaining: {attempts}')     
                                
                pull_ts = pd.to_datetime(time.time(), unit='s')
                last_pull.append(pull_ts)
                ad_soup = BeautifulSoup(ad_response.content)
    
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
                bar.update(i)
                
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
    
    return cars_df