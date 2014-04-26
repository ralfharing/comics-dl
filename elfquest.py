from bs4 import BeautifulSoup
import requests
import os
from progressbar import AnimatedProgressBar

# all series have a url code, what the local path, the progress bar code.
# some have issues and will then have an end length for how many.
# most are formatted with leading zeroes, and sometimes there is a
# special non-integer issue number.
class Series:
    def __init__(self, code, path, pb, issues=False, end=0, zeroes=True, special=''):
        self.code = code
        self.path = path
        self.pb = pb
        self.issues = issues
        self.end = end
        self.zeroes = zeroes
        self.special = special
    
    def __repr__(self):
        return 'Series({0}, \'{1}\')'.format(self.code, self.path)
    
    @property
    def x(self):
        return self._x

# lookup what to label the progress bars
progress_bar_names = {'OQ' : 'Original Quest',
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
                      'misc' : 'misc'}

# setup all the series and attributes
def init_series():
    series = set()
    series.add(Series('OQ', '1. The Original Quest', 'OQ', True, 21))
    series.add(Series('SABM', '2. Siege at Blue Mountain', 'SABM', True, 8))
    series.add(Series('KOBW', '3. Kings of the Broken Wheel', 'KOBW', True, 9))
    series.add(Series('HY', '4. Hidden Years', 'HY', True, 29, special='09.5'))
    series.add(Series('SH', '5. Shards', 'SH', True, 16))
    series.add(Series('NB', '6. New Blood', 'NB', True, 35, special='SS2'))
    series.add(Series('TC', '7. Blood of Ten Chiefs', 'TC', True, 20))
    series.add(Series('KA', '8. Kahvi', 'KA', True, 6))
    series.add(Series('TS', '9. Two-Spear', 'TS', True, 5))
    series.add(Series('JK', '10. Jink', 'JK', True, 12))
    series.add(Series('RB', '11. The Rebels', 'RB', True, 12))
    series.add(Series('WD', '12. WaveDancers', 'WD', True, 1))
    series.add(Series('MET', '13. Metamorphosis', 'MET'))
    series.add(Series('EQ2', '14. ElfQuest volume 2 (by issue)', 'EQ2i', True, 33))
    series.add(Series('DT', '14. ElfQuest volume 2 (by story)/Dreamtime', 'EQ2s'))
    series.add(Series('DTC', '14. ElfQuest volume 2 (by story)/Dreamtime (color)', 'EQ2s'))
    series.add(Series('WH', '14. ElfQuest volume 2 (by story)/Wild Hunt', 'EQ2s'))
    series.add(Series('FE', '14. ElfQuest volume 2 (by story)/Fire-Eye', 'EQ2s'))
    series.add(Series('WDa', '14. ElfQuest volume 2 (by story)/WaveDancers', 'EQ2s'))
    series.add(Series('RC', '14. ElfQuest volume 2 (by story)/Rogue\'s Curse', 'EQ2s'))
    series.add(Series('FQ', '14. ElfQuest volume 2 (by story)/FutureQuest', 'EQ2s'))
    series.add(Series('WR', '14. ElfQuest volume 2 (by story)/Wolfrider!', 'EQ2s'))
    series.add(Series('MEN3', '14. ElfQuest volume 2 (by story)/Mender\'s Tale part 3', 'EQ2s'))
    series.add(Series('MEN4', '14. ElfQuest volume 2 (by story)/Mender\'s Tale part 4', 'EQ2s'))
    series.add(Series('BS', '15. one shots/Bedtime Stories', 'os'))
    series.add(Series('FFJ', '15. one shots/The Jury', 'os'))
    series.add(Series('FFR', '15. one shots/Rogue\'s Curse', 'os'))
    series.add(Series('WP', '15. one shots/Worldpool', 'os'))
    series.add(Series('KC', '15. one shots/King\'s Cross', 'os', True, 2, zeroes=False))
    series.add(Series('HS', '15. one shots/Homespun', 'os'))
    series.add(Series('WGA', '15. one shots/Courage, By Any Other Name', 'os'))
    series.add(Series('SS2WS', '16. Wolfshadow', 'WS'))
    series.add(Series('SS2REC', '17. Recognition/Recognition (part 1)', 'REC'))
    series.add(Series('SS2aREC', '17. Recognition/Recognition (parts 1 & 2)', 'REC'))
    series.add(Series('IABB', '18. In All But Blood', 'IABB'))
    series.add(Series('SAS', '19. The Searcher and the Sword', 'SAS'))
    series.add(Series('DISC', '20. The Discovery', 'DISC'))
    series.add(Series('EQFQ', '21. Final Quest prologue', 'FQ'))
    series.add(Series('ESS', 'misc/Essential ElfQuest', 'misc'))
    series.add(Series('WDX', 'misc/WaveDancers (lost chapters)', 'misc'))
    series.add(Series('HYC', 'misc/Hidden Years (color)', 'misc'))
    series.add(Series('KAC', 'misc/Kahvi (color)', 'misc'))
    series.add(Series('SHC', 'misc/Shards (color)', 'misc'))
    series.add(Series('ASH', 'misc/Hidden Years & Shards ashcan', 'misc'))
    series.add(Series('GOHO', 'misc/A Gift of Her Own', 'misc'))
    series.add(Series('PressWR94', 'misc/movie storyboards 1994', 'misc'))
    series.add(Series('PressWR95', 'misc/movie storyboards 1995', 'misc'))
    series.add(Series('XAN', 'misc/Xanth - Return to Centaur', 'misc'))
    return series

# create dir path if it doesn't exist
def check_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

# perform the actual call to get the image urls from the xml
def parse_images(url, path, pb, pages):
    check_dir(path)
    r = requests.get(url)
    if r.ok:
        soup = BeautifulSoup(r.content)
        images = [x['source'] for x in soup('image')]
        for i in images:
            f = i.rsplit('/', 1)[1].lower()
            pages.add((i, path + f, pb))
    else:
        print 'error1', r, url

# each member of the set 'pages' is a tuple in the format
# (image url, full local file path, progress bar key)
def find_pages(series, local_dir, base_url):
    pages = set()
    for s in series:
        print 'finding pages for', s.path.split('. ')[-1]
        if s.issues:
            # compensate for series where the issues have leading zeroes
            width = 2 if s.zeroes else 1
            issues = {str(x).zfill(width) for x in range(1, s.end + 1)}
            # also add in non-integer issues
            if s.special:
                issues.add(s.special)
            for i in issues:
                url = base_url + s.code + '/' + s.code + i + '/'
                path = local_dir + s.path + '/' + s.code + i + '/'
                parse_images(url, path, s.pb, pages)
        else:
            url = base_url + s.code + '/'
            path = local_dir + s.path + '/'
            parse_images(url, path, s.pb, pages)
    # one page is an html file instead of an image
    check_dir(local_dir + '14. ElfQuest volume 2 (by story)/Mender\'s Tale part 5')
    pages.add(('http://www.elfquest.com/gallery/OnlineComics/MEN5/DisplayMEN5.html', local_dir + '14. ElfQuest volume 2 (by story)/Mender\'s Tale part 5/displaymen5.html', 'EQ2s'))
    return pages

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
    series = init_series()
    base_url = 'http://www.elfquest.com/comic_xml_zoom.php?fd=/gallery/OnlineComics/'
    local_dir = os.getcwd() + '/elfquest/'
    pages = find_pages(series, local_dir, base_url)
    progress_bars = progress_bar_names.keys()
    for series in progress_bars:
        series_pages = {x for x in pages if x[2] == series}
        bar = create_bar(series, len(series_pages))
        download_pages(series_pages, bar)
        print '' # so the progress bars don't overwrite each other

if __name__ == '__main__':
    main()
