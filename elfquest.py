from bs4 import BeautifulSoup
import requests
import os

base = 'http://www.elfquest.com/gallery/OnlineComics/'
resp = requests.get(base)
soup = BeautifulSoup(resp.content)
#yes = ['ASH/', 'TS/']

ignore = ['Parent Directory']
def is_valid(entry):
    return entry not in ignore \
           and 'thumb' not in entry \
           and 'html' not in entry \
           and 'gif' not in entry \
           and 'tif' not in entry

links = set(x['href'] for x in soup('a') if is_valid(list(x.stripped_strings)[0]))
files = set(l for l in links if not l.endswith('/'))
dirs = links - files

image_dir = os.getcwd() + '\\images\\'
def check_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def download_files(local_dir, base_url, files):
    check_dir(local_dir)
    for file in files:
        r = requests.get(base_url + file)
        with open(local_dir + file.lower(), 'wb') as f:
            f.write(r.content)

#def download(local_dir, base_url, files, dirs, skip_check=False):
def download(local_dir, base_url, files, dirs):
    download_files(local_dir, base_url, files)
    for dir in dirs:
#        if dir in yes or skip_check:
        sub_local_dir = local_dir + dir.replace('/', '\\')
        check_dir(sub_local_dir)
        resp = requests.get(base_url + dir)
        soup = BeautifulSoup(resp.content)
        links = set(x['href'] for x in soup('a') if is_valid(list(x.stripped_strings)[0]))
        sub_files = set(l for l in links if not l.endswith('/'))
        sub_dirs = links - sub_files
#        download(sub_local_dir, base_url + dir, sub_files, sub_dirs, True)
        download(sub_local_dir, base_url + dir, sub_files, sub_dirs)

download(image_dir, base, files, dirs)