import requests
import re
import sys
import os
import time
import logging

from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.DEBUG, format='%(threadName)s: %(message)s')

# list for visited URLs
visited = []
# regular expression to find links
patron = 'href=[\'"]?([^\'" >]+)'
# content type of the link
cType = 'text/html;charset=ISO-8859-1'
# file extensions
extensions = ['.ppt', '.pptx', '.pdf', '.txt', '.docx', '.doc', '.html', '.htm', '.css', '.jpg', '.png', 
                '.x', '.c', '.java', '.form', '.zip', '.tar.gz', '.tgz']

"""# check if the URL is a file
def is_file(url):
    if url.endswith('.pdf') or url.endswith('.txt') or url.endswith('.docx') or url.endswith('.doc'):
        return True
    else:
        return False"""

def download_file(URL):
    # get the folder name to create localy
    #folder = URL.split('/')[-2]
    folder = URL.split('/')[3:-1]
    folder = '/'.join(folder)
    # create the folder if not exists
    if not os.path.exists(folder):
        os.makedirs(folder)
    # create the file in the folder
    fileName = folder + '/' + URL.split('/')[-1]
    # download the file
    local_filename = URL.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(URL, stream=True)
    print("\nEl URL de la página es: \n", r.url)
    with open(fileName, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush()
    return local_filename

def check_url(URL):
    if URL not in visited:
        visited.append(URL)
        download_file(URL)
        print(f"\n{URL} se ha descargado correctamente")
    else:
        print(f"\nLa direccion {URL} ya se ha descargado")

def not_visited(URL):
    if URL not in visited:
        return True
    else:
        return False

# look for more links in the page
def find_more_links(URL):
    r = requests.get(URL)
    visited.append(URL)
    urls = re.findall(patron, r.text)

    print(f"\nSe han encontrado {len(urls)} URL's:")
    print('\n'.join(map(str, urls)))

    # delete '/' of the elements
    for i in range(len(urls)):
        if urls[i].startswith('/'):
            urls[i] = urls[i][1:]

    print("\nLas nuevas URL's son: ")
    print('\n'.join(map(str, urls)))
####################################################
    for url in urls:
        # check if is in list of extensions
        if url.endswith(tuple(extensions)) or url.endswith('/'):
        #if url.endswith('/') or url.endswith('.ppt') or url.endswith('.pptx') or url.endswith('.pdf') or url.endswith('.txt') or url.endswith('.docx') or url.endswith('.doc'):
            # if starts with http, then it's a valid URL
            if url.startswith('http'):
                if not_visited(url):
                    print(f"\nLa URL {url} es válida")
                    # do the request to find more links
                    print("Se hara un request a: ", url)
                    urlR = requests.get(url)
                    if urlR.ok:
                        print(urlR.headers['content-type'])
                        # check if the content type is text/html
                        if urlR.headers['content-type'] == cType:
                            # if is text/html, then look for more links
                            print("\nLlamaremos a la funcion find_more_links para buscar mas links en: ", url)
                            find_more_links(url)
                            #executor.submit(find_more_links, url)
                        else:
                            # if not text/html, then download the file
                            print(f"\nEl link {url} corresponde a un archivo, se descargará . . .")
                            download_file(url)
                    else:
                        print("\nEl link no es válido")
                else:
                    print(f"\nLa URL {url} ya se ha visitado")

            # if not, then it's a relative URL
            else:
                if not_visited(URL + url):
                    print(f"\nLa URL no es valida, se usara el dominio base {URL}")
                    # do the request to find more links
                    print("\nSe hara un request a: ", URL + url)
                    urlR = requests.get(URL + url)
                    if urlR.ok:
                        # check if the content type is text/html
                        if urlR.headers['content-type'] == cType:
                            print(f"\nEl link {URL + url}  corresponde a una página web")
                            # if is text/html, then look for more links
                            print("Se buscaran mas links en: ", URL + url)
                            find_more_links(URL + url)
                        else:
                            # if not text/html, then download the file
                            print(f"\nEl link {URL + url} corresponde a un archivo, se descargará . . .")
                            download_file(URL + url)
                    else:
                        print("\nEl link no es válido")
                else:
                    print(f"\nLa URL {URL + url} ya se ha visitado")
        else:
            print(f"\nLa URL {url} no es valida")
            continue
####################################################

"""    for url in urls:
        urlRequest  = requests.get(url)
        if urlRequest.headers['content-type'] != cType:
            print(f"\nLa URL {url} no es una página HTML")
            if url.startswith('http'):
                print(f"La URL {url} empieza por http")
                check_url(url)
            else:
                print(f"La URL {URL + url} no empieza por http")
                check_url(URL + url)
        else:
            print(f"La URL {url} es una página HTML")
            if url.startswith('http'):
                print(f"La URL {url} se llamara para buscar mas links")
                find_more_links(url)
            else:
                print(f"La URL {URL + url} se llamara para buscar mas links")
                find_more_links(URL + url)"""

def main():
    # create the pool with two threads
    print('Creamos un pool  con 2 threads')
    executor = ThreadPoolExecutor(max_workers = 2)

    URL = input("Introduce la URL: ")
    executor.submit(find_more_links, URL)
    #find_more_links(URL)

"""
URL = input("Introduce la URL: ")
#visited.append(URL)
#find_more_links(URL)
#print(patron)
find_more_links(URL)

print('\nLas URLs visitadas son:\n'.join(map(str, visited)))
"""

main()