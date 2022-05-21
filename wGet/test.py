import requests
import re
import os

content_Type = 'text/html'

patron = 'href=[\'"]?([^\'" >]+)'

def creaate_folder(URL):
    # create three of folders
    
    folder = URL.split('/')[3:-1]
    folder = '/'.join(folder)
    if not os.path.exists(folder):
        os.makedirs(folder)

URL = input("URL: ")

creaate_folder(URL)

r = requests.get(URL)
print (r.headers)
print("\nLos headers son: \n")
print (r.headers['content-type'])
#if content_Type == 'text/html':
#    print (r.text)
#urls = re.findall(patron, r.text)
#print(f"\nSe han encontrado {len(urls)} URL's:")
#print('\n'.join(map(str, urls)))