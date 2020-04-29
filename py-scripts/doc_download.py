import requests
from bs4 import BeautifulSoup as BSoup
import os
import re
from itertools import compress
import time
from pathlib import Path

# Defining functions
def get_urls(soup):
    """
    Retrieves url for list items within the same year.
    """
    
    sibling = soup.next_sibling
    sibling_class = sibling['class']
    
    urls = list()
    
    while 'portal_list_item' in sibling_class:
        urls.append(sibling.a.get('href'))
        sibling = sibling.next_sibling
        try:
            sibling_class = sibling['class']
        except:
            break
    
    return(urls)

def dl_file(href, filepath = "./data/", reset_cache = False):
    """
    For downloading document.
    """
    try:
        filename = re.findall(r'(?<=\d{5}\/).*?\.\w{2,5}', href)[0]
    except:
        return
    
    if reset_cache == False:
        existing_filepath = Path(filepath + filename)
        if existing_filepath.is_file():
            print("\tFile {} already downloaded".format(filename), end = '\n')
            return
        else:
            reset_cache = True
    
    if reset_cache == True:
        response = requests.get(href)
    
        if response.ok:
            with open(filepath + filename, 'wb') as f:
                f.write(response.content)
                time.sleep(0.6)

            #print("file {} downloaded".format(filename))
        else:
            print("could not download file {}".format(filename))

# Setting parameters
url = "https://projekter.aau.dk/projekter/da/studentthesis/search.html?search=" \
        "&advanced=true" \
        "&type=%2Fdk%2Fmasterthesis" \
        "&education=71383896" \
        "&ordering=studentProjectOrderByPublicationYear" \
        "&descending=true" \
        "&pageSize=500" \
        "&page=0"



datadir = "../data/" # CHANGE IF YOU WANT DATA STORED DIFFERENTLY!
if not os.path.exists(datadir):
    os.makedirs(datadir)  

# Retrieving html and downloading files
response = requests.get(url, stream = True)
if response.ok:
    
    source = response.text
    sourceSoup = BSoup(source, features = 'lxml')

    thesis_dict = dict()
    
    for soup in sourceSoup.find_all(class_="portal_list_item_group"):
        year = soup.get_text()

        thesis_dict[year] = get_urls(soup)

  

    for year in list(thesis_dict.keys()):
        yeardir = datadir + year + "/"

        if not os.path.exists(yeardir):
            os.makedirs(yeardir)

        print("Downloading documents for year {}".format(year), end = '\n')
        c = 0
        for c, href in enumerate(thesis_dict[year]):
            print('Completed: {:.2f}%'.format(100.0*c/len(thesis_dict[year])), end = '\r')

            dl_file(href, filepath = yeardir)


        print("All documents downloaded", end = '\r')
        
else:
    raise ValueError("Could not reach URL {}".format(url))