from bs4 import BeautifulSoup
import requests
import os
from progressbar import AnimatedProgressBar

lookup = {
'OQ/' : {'dir' : '1. The Original Quest', 'pb' : 'OQ'},
'SABM/' : {'dir' : '2. Siege at Blue Mountain', 'pb' : 'SABM'},
'KOBW/' : {'dir' : '3. Kings of the Broken Wheel', 'pb' : 'KOBW'},
'HY/' : {'dir' : '4. Hidden Years', 'pb' : 'HY'},
'SH/' : {'dir' : '5. Shards', 'pb' : 'SH'},
'NB/' : {'dir' : '6. New Blood', 'pb' : 'NB'},
'TC/' : {'dir' : '7. Blood of Ten Chiefs', 'pb' : 'TC'},
'KA/' : {'dir' : '8. Kahvi', 'pb' : 'KA'},
'TS/' : {'dir' : '9. Two-Spear', 'pb' : 'TS'},
'JK/' : {'dir' : '10. Jink', 'pb' : 'JK'},
'RB/' : {'dir' : '11. The Rebels', 'pb' : 'RB'},
'WD/' : {'dir' : '12. WaveDancers', 'pb' : 'WD'},
'MET/' : {'dir' : '13. Metamorphosis', 'pb' : 'MET'},
'EQ2/' : {'dir' : '14. ElfQuest volume 2 (by issue)', 'pb' : 'EQ2i'},
'DT/' : {'dir' : '14. ElfQuest volume 2 (by story)/Dreamtime', 'pb' : 'EQ2s'},
'DTC/' : {'dir' : '14. ElfQuest volume 2 (by story)/Dreamtime (color)', 'pb' : 'EQ2s'},
'WH/' : {'dir' : '14. ElfQuest volume 2 (by story)/Wild Hunt', 'pb' : 'EQ2s'},
'FE/' : {'dir' : '14. ElfQuest volume 2 (by story)/Fire-Eye', 'pb' : 'EQ2s'},
'WDa/' : {'dir' : '14. ElfQuest volume 2 (by story)/WaveDancers', 'pb' : 'EQ2s'},
'RC/' : {'dir' : '14. ElfQuest volume 2 (by story)/Rogue\'s Curse', 'pb' : 'EQ2s'},
'FQ/' : {'dir' : '14. ElfQuest volume 2 (by story)/FutureQuest', 'pb' : 'EQ2s'},
'WR/' : {'dir' : '14. ElfQuest volume 2 (by story)/Wolfrider!', 'pb' : 'EQ2s'},
'MEN3/' : {'dir' : '14. ElfQuest volume 2 (by story)/Mender\'s Tale part 3', 'pb' : 'EQ2s'},
'MEN4/' : {'dir' : '14. ElfQuest volume 2 (by story)/Mender\'s Tale part 4', 'pb' : 'EQ2s'},
'MEN5/' : {'dir' : '14. ElfQuest volume 2 (by story)/Mender\'s Tale part 5', 'pb' : 'EQ2s'},
'BS/' : {'dir' : '15. one shots/Bedtime Stories', 'pb' : 'os'},
'FFJ/' : {'dir' : '15. one shots/The Jury', 'pb' : 'os'},
'FFR/' : {'dir' : '15. one shots/Rogue\'s Curse', 'pb' : 'os'},
'WP/' : {'dir' : '15. one shots/Worldpool', 'pb' : 'os'},
'KC/' : {'dir' : '15. one shots/King\'s Cross', 'pb' : 'os'},
'HS/' : {'dir' : '15. one shots/Homespun', 'pb' : 'os'},
'WGA/' : {'dir' : '15. one shots/Courage, By Any Other Name', 'pb' : 'os'},
'SS2WS/' : {'dir' : '16. Wolfshadow', 'pb' : 'WS'},
'SS2REC/' : {'dir' : '17. Recognition/Recognition (part 1)', 'pb' : 'REC'},
'SS2aREC/' : {'dir' : '17. Recognition/Recognition (parts 1 & 2)', 'pb' : 'REC'},
'IABB/' : {'dir' : '18. In All But Blood', 'pb' : 'IABB'},
'SAS/' : {'dir' : '19. The Searcher and the Sword', 'pb' : 'SAS'},
'DISC/' : {'dir' : '20. The Discovery', 'pb' : 'DISC'},
'EQFQ/' : {'dir' : '21. Final Quest prologue', 'pb' : 'FQ'},
'ESS/' : {'dir' : 'misc/Essential ElfQuest', 'pb' : 'misc'},
'WDX/' : {'dir' : 'misc/WaveDancers (lost chapters)', 'pb' : 'misc'},
'HYC/' : {'dir' : 'misc/Hidden Years (color)', 'pb' : 'misc'},
'KAC/' : {'dir' : 'misc/Kahvi (color)', 'pb' : 'misc'},
'SHC/' : {'dir' : 'misc/Shards (color)', 'pb' : 'misc'},
'ASH/' : {'dir' : 'misc/Hidden Years & Shards ashcan', 'pb' : 'misc'},
'GOHO/' : {'dir' : 'misc/A Gift of Her Own', 'pb' : 'misc'},
'PressWR94/' : {'dir' : 'misc/movie storyboards 1994', 'pb' : 'misc'},
'PressWR95/' : {'dir' : 'misc/movie storyboards 1995', 'pb' : 'misc'},
'XAN/' : {'dir' : 'misc/Xanth - Return to Centaur', 'pb' : 'misc'}
}

progress_bar_names = {
'OQ' : 'Original Quest',
'SABM' : 'Siege at Blue Mountain',
'KOBW' : 'Kings of the Broken Wheel',
'HY' : 'Hidden Years',
'SH' : 'Shards',
'NB' : 'New Blood',
'TC' : 'Blood of Ten Chiefs',
'KA' : 'Kahvi',
'TS' : 'Two-Spear',
'JK' : 'Jink',
'RB' : 'Rebels',
'WD' : 'WaveDancers',
'MET' : 'Metamorphosis',
'EQ2i' : 'ElfQuest v2 (by issue)',
'EQ2s' : 'ElfQuest v2 (by story)',
'os' : 'one shots',
'WS' : 'Wolfshadow',
'REC' : 'Recognition',
'IABB' : 'In All But Blood',
'SAS' : 'Searcher and the Sword',
'DISC' : 'Discovery',
'FQ' : 'Final Quest',
'misc' : 'misc'
}

# exclude previous and thumbnail directories as well as misc other files
def is_valid(entry):
    # special case for one story which was never drawn
    if entry == 'DisplayMEN5.html': return True
    ignore = ('Parent Directory', 'html', 'gif', 'tif', 'php', 'thumb/')
    return not entry.endswith(ignore)

# create dir path if it doesn't exist
def check_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

# each member of the returned set 'pages' is a tuple in
# the format (image url, full local file path, progress bar key)
def find_pages(local_dir, base_url, pages, is_root, pb_key=''):
    r = requests.get(base_url)
    if r.ok:
        soup = BeautifulSoup(r.content)
        # filter out invalid entries in current dir
        links = set(x['href'] for x in soup('a') if is_valid(''.join(x.stripped_strings)))
        # separate into files and dirs
        files = set(l for l in links if not l.endswith('/'))
        dirs = links - files
        for f in files:
            pages.add((base_url + f, local_dir + f.lower(), pb_key))
        for d in dirs:
            # some code duplication but clearer this way
            if is_root:
                print 'finding pages for', lookup[d]['dir'].split('. ')[-1]
                # rename the first level dirs so they're easily sorted
                sub_dir = local_dir + lookup[d]['dir'] + '/'
                check_dir(sub_dir)
                find_pages(sub_dir, base_url + d, pages, False, lookup[d]['pb'])
            else:
                sub_dir = local_dir + d
                check_dir(sub_dir)
                find_pages(sub_dir, base_url + d, pages, False, pb_key)
    else:
        print 'error1', r, base_url

# creates an animated progress bar with the appropriate options
def create_bar(key, files):
    options = {'width': 45, 'fill': '*', 'end': files,
               'format' : '%(progress)s%% [%(fill)s%(blank)s] ' + progress_bar_names[key]}
    return AnimatedProgressBar(**options)

# pull out random pages and attempt to save them locally.
# if that fails, put them back in the pool and try again.
def download_pages(pages, progress_bar):
    while pages:
        image, local_file, pb_key = pages.pop()
        new_name = local_file.split('/')[-1]
        r = requests.get(image)
        if r.ok:
            with open(local_file, 'wb') as f:
                f.write(r.content)
            progress_bar + 1
            progress_bar.show_progress()
        else:
            print 'error2', r, image
            pages.add((image, local_file, pb_key))

def main():
    base_url = 'http://www.elfquest.com/gallery/OnlineComics/'
    image_dir = os.getcwd() + '/elfquest/'
    pages = set()
    find_pages(image_dir, base_url, pages, True)
    progress_bars = {lookup[x]['pb'] for x in lookup}
    for series in progress_bars:
        series_pages = {x for x in pages if x[2] == series}
        bar = create_bar(series, len(series_pages))
        download_pages(series_pages, bar)
        print '' # so the progress bars don't overwrite each other

if __name__ == '__main__':
    main()
