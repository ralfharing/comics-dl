from bs4 import BeautifulSoup
import requests
import os
import argparse

series = {'t' : 'tuki', 'b' : 'bone', 'r' : 'rasl'}
cover = {'t' : 'http://www.boneville.com/comic/tuki-season-one-cover',
         'b' : 'http://www.boneville.com/comic/bone-issue-one-cover-2',
         'r' : 'http://www.boneville.com/comic/rasl-issue-one-cover'}
pages = set()

# find and store the image on the current page
# then drill down to the next page if there is one
def findPages(url, page, series, pages):
    r = requests.get(url)
#    print r, r.ok
    if r.ok:
        soup = BeautifulSoup(r.content)
        div = soup.find(id='comic')
        image = div.img['src']
        pages.add((image, series + '-' + str(page)))
        # if the image is a link, keep going
        # otherwise this is last page and bump out
        if div.a is not None:
            findPages(div.a['href'], page + 1, series, pages)
    else:
        findPages(url, page, series, pages)

# try to get a random image from those previously stored
# and keep retrying until all are complete
def downloadPages(pages):
    while pages:
        image, name = pages.pop()
        ext = image.rsplit('.')[-1]
        # rename the file so they're easily sorted
        new_name = name + '.' + ext.lower()
        local_file = os.getcwd() + '\\' + new_name
        r = requests.get(image)
#        print r, r.ok
        if r.ok:
            with open(local_file, 'wb') as f:
                print 'downloading', image.rsplit('/')[-1] + ' -> ' + new_name
                f.write(r.content)
        else:
            pages.add((image, name))

def main(**kwargs):
    for code, name in series.iteritems():
        if kwargs[code]:
            print 'starting to find pages for', name
            findPages(cover[code], 1, name, pages)
#            print len(pages)
    downloadPages(pages)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', action='store_true', help='download Tuki')
    parser.add_argument('-b', action='store_true', help='download Bone')
    parser.add_argument('-r', action='store_true', help='download Rasl')
    args = vars(parser.parse_args())

    if not any(args.values()):
        parser.print_help()
    else:
        main(**args)