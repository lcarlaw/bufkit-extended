"""
Set-up script to create a list of site IDs within a pre-defined lat/lon
"""

from concurrent.futures import ThreadPoolExecutor
import urllib.request as requests    
from urllib.error import HTTPError, URLError

def download(url):
    #url = f"http://www.meteo.psu.edu/bufkit/data/RAP/02/{name}"
    site = None
    try: 
        data = requests.urlopen(url, timeout=5).read(300)
        data = data.decode('utf-8')

        start = "SLAT = "
        end = "SLON = "
        idx_start = data.find(start)
        idx_end = data.find(end)
        lat = float(data[idx_start+len(start):idx_end])
        lon = float(data[idx_end+len(end):data.find("SELV")])
        
        sep = url.rfind('_')
        dot = url.rfind('.')
        name = url[sep+1:dot]
        
        if 39 < lat <= 46 and -93 < lon <= -82:
            site = name
    except (HTTPError, URLError) as e:
        pass
    
    return site

with open('html.txt', 'r') as f: data = f.readlines()

urls = []
for line in data:
    idx_start = line.find('href=')
    if idx_start > 0:
        subline = line[idx_start+6:]
        idx_end = subline.find('.buf')
        name = subline[0:idx_end+4]
        url = f"http://www.meteo.psu.edu/bufkit/data/RAP/02/{name}"
        urls.append(url)

ids = []
num_sites = len(urls)
for knt, site in enumerate(urls):
    print(knt, num_sites)
    ID = download(site)
    if ID is not None: ids.append(ID)

print(ids)


#with ThreadPoolExecutor(max_workers=20) as executor:
#    executor.map(download, urls)
#    executor.shutdown(wait=True)
