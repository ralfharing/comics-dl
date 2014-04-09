from bs4 import BeautifulSoup
import requests
import os

# each element of the returned list is a list containing
# all the links to the subpages for that chapter
def find_chapters(url):
    r = requests.get(url)
    chapters = []
    if r.ok:
        soup = BeautifulSoup(r.content)
        # the first match is the full series. throw it out and
        # keep the later matches which show chapters separately.
        chapter_tags = soup.find_all(class_='month-table')[1:]
        for c in chapter_tags:
            links = [x['href'] for x in c('a')]
            chapters.append(links)
    else:
        print 'error1', r, url
    return chapters

# each member of the returned set is a tuple in
# the format (image url, chapter #, page #)
def find_pages(chapters):
    pages = set()
    for i,chapter in enumerate(chapters):
        page_num = 1
        print 'checking chapter', i+1
        for page in chapter:
            r = requests.get(page)
            if r.ok:
                soup = BeautifulSoup(r.content)
                panels = soup.find_all(class_='comicpane')
                for panel in panels:
                    image = panel('img')[0]['src']
                    # save (img url, chapter #, page #)
                    pages.add((image, str(i+1), str(page_num)))
                    page_num += 1
            else:
                print 'error2', r, page
    return pages

# create dir path if it doesn't exist
def check_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

# pull out random pages and attempt to save them locally.
# if that fails, put them back in the pool and try again.
def download(pages):
    image_dir = os.getcwd() + '\\lady_sabre_and_the_pirates_of_the_ineffable_aether\\'
    check_dir(image_dir)
    while pages:
        image, chapter, page = pages.pop()
        ext = image.split('.')[-1]
        # rename the files so they're easily sorted
        new_name = 'chapter-' + chapter + '-page-' + page + '.' + ext.lower()
        local_file = image_dir + new_name
        r = requests.get(image)
        if r.ok:
            with open(local_file, 'wb') as f:
                print 'downloading', image.split('/')[-1] + ' -> ' + new_name
                f.write(r.content)
        else:
            print 'error3', r, image
            pages.add((image, chapter, page))

def main():
    archive = 'http://www.ineffableaether.com/archive'
    chapters = find_chapters(archive)
    pages = find_pages(chapters)
    download(pages)

if __name__ == '__main__':
    main()