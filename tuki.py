from bs4 import BeautifulSoup
import requests
import os
import argparse

# find and store the image on the current page
# then drill down to the next page if there is one.
# each member of the returned set 'pages' is a tuple in
# the format (image url, series name, page #)
def find_pages(url, page, series, pages):
    r = requests.get(url)
    if r.ok:
        soup = BeautifulSoup(r.content)
        div = soup.find(id='comic')
        image = div.img['src']
        pages.add((image, series, str(page)))
        # if the image is a link, keep going
        # otherwise this is last page and bump out
        if div.a is not None:
            find_pages(div.a['href'], page + 1, series, pages)
    else:
        print 'error1', r, url
        find_pages(url, page, series, pages)

# create dir path if it doesn't exist
def check_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

# pull out random pages and attempt to save them locally.
# if that fails, put them back in the pool and try again.
def download_pages(pages, image_dir):
    while pages:
        image, series, page = pages.pop()
        ext = image.split('.')[-1]
        # rename the files so they're easily sorted
        new_name = series + '-' + page + '.' + ext.lower()
        local_file = image_dir + '/' + series + '/' + new_name
        r = requests.get(image)
        if r.ok:
            with open(local_file, 'wb') as f:
                print 'downloading', image.split('/')[-1] + ' -> ' + new_name
                f.write(r.content)
        else:
            print 'error2', r, image
            pages.add((image, series, page))

def main(**kwargs):
    series = [('t', 'tuki', 'http://www.boneville.com/comic/tuki-season-one-cover'),
              ('b', 'bone', 'http://www.boneville.com/comic/bone-issue-one-cover-2'),
              ('r', 'rasl', 'http://www.boneville.com/comic/rasl-issue-one-cover')]
    pages = set()
    image_dir = os.getcwd()

    for flag, name, cover in series:
        if kwargs[flag]:
            print 'finding pages for', name
            find_pages(cover, 1, name, pages)
            check_dir(image_dir + '/' + name)
    download_pages(pages, image_dir)

if __name__ == '__main__':
    # call with -t, -b, -r, or any combination like -rt or -tbr
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', action='store_true', help='download Tuki')
    parser.add_argument('-b', action='store_true', help='download Bone')
    parser.add_argument('-r', action='store_true', help='download Rasl')
    args = vars(parser.parse_args())

    if not any(args.values()):
        # must choose at least one
        parser.print_help()
    else:
        main(**args)