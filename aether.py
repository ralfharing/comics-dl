from bs4 import BeautifulSoup
import urllib2
import urllib
import os
import time

page = urllib2.urlopen('http://www.ineffableaether.com/archive/')
soup = BeautifulSoup(page.read())
# multiple tables with this class. first one is desired.
table = soup.find('table', 'month-table')
links = set((x,0) for x in table('a'))

imageDir = os.getcwd() + '\\images\\'
os.mkdir(imageDir)

while len(links) > 0:
    link = links.pop()
    href = link[0]['href']
    # if link has failed before, sleep
    if link[1] > 0:
        print 'sleeping', link[1], 'seconds for', href
        time.sleep(link[1])

    try:
        comic_page = urllib2.urlopen(href)
        comic_soup = BeautifulSoup(comic_page.read())
        # possibly multiple images per page
        for image in comic_soup(id='comic')[0]('img'):
            source = image['src']
            # check if local copy of image file already exists
            path = imageDir + source.split('/')[-1]
            if not os.path.exists(path):
                print source
                urllib.urlretrieve(source, path)
    except:
        # increase time to sleep by 1 sec every failure
        links.add((link[0], link[1] + 1))