# -*- coding: utf-8 -*-

from selenium import webdriver # if not installed, do pip install selenium

def generateProxies():
	
    # Get list of US-based proxy IPs and ports using selenium

    IPurl = "https://www.us-proxy.org/" # <-- the robots.txt file for this site allows full access for all user-agents

    # Specify incognito options for Chrome
    option = webdriver.ChromeOptions()
    option.add_argument("--incognito")
    option.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Create new Chrome instance
    browser = webdriver.Chrome(options=option)

    # Minimize window
    browser.minimize_window()

    # Go to desired website
    IPurl = "https://www.us-proxy.org/" # <-- the robots.txt file for this site allows full access for all user-agents
    browser.get(IPurl)

    # Filter by https only
    https_button = browser.find_elements_by_xpath("//*[@id='proxylisttable']/tfoot/tr/th[7]/select/option[3]")[0]
    https_button.click()

    # Set to 80 results
    maxnum_button = browser.find_elements_by_xpath("//*[@id='proxylisttable_length']/label/select/option[3]")[0]
    maxnum_button.click()

    # Grab IP's and Ports from the resulting table
    rows = browser.find_elements_by_xpath("//*[@id='proxylisttable']/tbody/tr")

    proxies = set() # using a set ensures there aren't duplicates
    for row in rows:
        row = row.text.split(' ')

        if row[3].strip().lower() != 'transparent': # don't want to include our real proxy when navigating KSL
            proxies.add(''.join(['http://', ':'.join([row[0].strip(), row[1].strip()])]))

    # Close browser when done
    browser.close()

    return proxies