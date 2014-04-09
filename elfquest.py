from bs4 import BeautifulSoup
import requests
import os

lookup = {
'OQ/' : '1. The Original Quest',
'SABM/' : '2. Siege at Blue Mountain',
'KOBW/' : '3. Kings of the Broken Wheel',
'HY/' : '4. Hidden Years',
'SH/' : '5. Shards',
'NB/' : '6. New Blood',
'TC/' : '7. Blood of Ten Chiefs',
'KA/' : '8. Kahvi',
'TS/' : '9. Two-Spear',
'JK/' : '10. Jink',
'RB/' : '11. The Rebels',
'WD/' : '12. WaveDancers',
'MET/' : '13. Metamorphosis',
'EQ2/' : '14. ElfQuest volume 2 (by issue)',
'DT/' : '14. ElfQuest volume 2 (by story)/Dreamtime',
'DTC/' : '14. ElfQuest volume 2 (by story)/Dreamtime (color)',
'WH/' : '14. ElfQuest volume 2 (by story)/Wild Hunt',
'FE/' : '14. ElfQuest volume 2 (by story)/Fire-Eye',
'WDa/' : '14. ElfQuest volume 2 (by story)/WaveDancers',
'RC/' : '14. ElfQuest volume 2 (by story)/Rogue\'s Curse',
'FQ/' : '14. ElfQuest volume 2 (by story)/FutureQuest',
'WR/' : '14. ElfQuest volume 2 (by story)/Wolfrider!',
'MEN3/' : '14. ElfQuest volume 2 (by story)/Mender\'s Tale part 3',
'MEN4/' : '14. ElfQuest volume 2 (by story)/Mender\'s Tale part 4',
'MEN5/' : '14. ElfQuest volume 2 (by story)/Mender\'s Tale part 5',
'BS/' : '15. one shots/Bedtime Stories',
'FFJ/' : '15. one shots/The Jury',
'FFR/' : '15. one shots/Rogue\'s Curse',
'WP/' : '15. one shots/Worldpool',
'KC/' : '15. one shots/King\'s Cross',
'HS/' : '15. one shots/Homespun',
'WGA/' : '15. one shots/Courage, By Any Other Name',
'SS2WS/' : '16. Wolfshadow',
'SS2REC/' : '17. Recognition/Recognition (part 1)',
'SS2aREC/' : '17. Recognition/Recognition (parts 1 & 2)',
'IABB/' : '18. In All But Blood',
'SAS/' : '19. The Searcher and the Sword',
'DISC/' : '20. The Discovery',
'EQFQ/' : '21. Final Quest prologue',
'ESS/' : 'misc/Essential ElfQuest',
'WDX/' : 'misc/WaveDancers (lost chapters)',
'HYC/' : 'misc/Hidden Years (color)',
'KAC/' : 'misc/Kahvi (color)',
'SHC/' : 'misc/Shards (color)',
'ASH/' : 'misc/Hidden Years & Shards ashcan',
'GOHO/' : 'misc/A Gift of Her Own',
'PressWR94/' : 'misc/movie storyboards 1994',
'PressWR95/' : 'misc/movie storyboards 1995',
'XAN/' : 'misc/Xanth - Return to Centaur'
}

# exclude previous and thumbnail directories as well as misc other files
def is_valid(entry):
    ignore = ('Parent Directory', 'html', 'gif', 'tif', 'php', 'thumb/')
    return not entry.endswith(ignore)

# create dir path if it doesn't exist
def check_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

# each member of the returned set 'pages' is a tuple in
# the format (image url, full local file path)
def find_pages(local_dir, base_url, pages, is_root):
    r = requests.get(base_url)
    if r.ok:
        soup = BeautifulSoup(r.content)
        # filter out invalid entries in current dir
        links = set(x['href'] for x in soup('a') if is_valid(''.join(x.stripped_strings)))
        # separate into files and dirs
        files = set(l for l in links if not l.endswith('/'))
        dirs = links - files
        for f in files:
            pages.add((base_url + f, local_dir + f.lower()))
        for d in dirs:
            if is_root: print 'finding pages for', lookup[d].split('. ')[-1]
            # rename the first level dirs so they're easily sorted
            sub_dir = local_dir + lookup[d] + '/' if is_root else local_dir + d
            check_dir(sub_dir)
            find_pages(sub_dir, base_url + d, pages, False)
    else:
        print 'error1', r, base_url

# pull out random pages and attempt to save them locally.
# if that fails, put them back in the pool and try again.
def download_pages(pages):
    while pages:
        image, local_file = pages.pop()
        new_name = local_file.split('/')[-1]
        r = requests.get(image)
        if r.ok:
            with open(local_file, 'wb') as f:
                print 'downloading', image.split('/')[-1] + ' -> ' + new_name
                f.write(r.content)
        else:
            print 'error2', r, image
            pages.add((image, local_file))

def main():
    base_url = 'http://www.elfquest.com/gallery/OnlineComics/'
    image_dir = os.getcwd() + '/elfquest/'
    pages = set()
    find_pages(image_dir, base_url, pages, True)
    download_pages(pages)

if __name__ == '__main__':
    main()
