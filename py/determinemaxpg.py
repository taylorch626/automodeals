# -*- coding: utf-8 -*-

def determinemaxpg():
	'''This is a function to determine how long to run RestartRepository'''
	url = "https://cars.ksl.com/search/newUsed/Used;Certified/perPage/96/page/0"
    
    # Need to spoof a user-agent in order to get past crawler block
	user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    
	resp = requests.get(url, headers = {'User-Agent': user_agent})
        
	html = resp.content
	pgsoup = BeautifulSoup(html)
    
    # Get last page of results (useful when restarting repository from scratch to know when to stop)
	return int(pgsoup.find(attrs={"title": "Go to last page"}).text.strip()) # Note that this is 1 more than number from href for this page