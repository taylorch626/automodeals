# -*- coding: utf-8 -*-
import requests

def get_tor_session():
    session = requests.session() # creates connection between each request made to a server. Cookies don't reset each time. Authenticates once
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'} # for anonymization, sets Tor port
    return session

# Make a request through the Tor connection
# IP visible through Tor
session = get_tor_session()
print(session.get("http://httpbin.org/ip").text)
# Above should print an IP different than your public IP

# Following prints your normal public IP
print(requests.get("http://httpbin.org/ip").text)

from stem import Signal
from stem.control import Controller

# signal TOR for a new connection
def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="koolKid23")
        controller.signal(Signal.NEWNYM)

renew_connection()
session = get_tor_session()
print(session.get("http://httpbin.org/ip").text)

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

for i in range(6):
    renew_connection()
    session = get_tor_session()
    print(session.get("http://httpbin.org/ip").text)
    response = session.get('https://cars.ksl.com/listing/6346585?ad_cid=', headers = {'User-Agent': user_agent}, timeout=31)
    print(response)