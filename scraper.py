from __future__ import print_function
import time
import sys
import json
import re
import os
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

def download_file(url, local_filename):
    if local_filename is None:
        local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return local_filename


def get_photos(qs, page=1, original=False):
    params = {
        'media_type': 'image',
        'page': page,
    }

    if qs is not None:
        params['q'] = qs

    results = requests.get('https://images-api.nasa.gov/search', params=params).json()
    return results


def search(qs, original=False, max_pages=None, start_page=1):
    # create a folder for the query if it does not exist
    foldername = os.path.join('images', re.sub(r'[\W]', '_', qs if qs is not None else ''))

    if not os.path.exists(foldername):
        os.makedirs(foldername)

    jsonfilename = os.path.join(foldername, 'results' + str(start_page) + '.json')

    if not os.path.exists(jsonfilename):

        # save results as a json file
        photos = []
        current_page = start_page

        results = get_photos(qs, page=current_page, original=original)
        if results is None:
            with open(jsonfilename, 'w') as outfile:
                json.dump(results, outfile)
            return

        total_pages = results['collection']['metadata']['total_hits']/100
        if max_pages is not None and total_pages > start_page + max_pages:
            total_pages = start_page + max_pages

        #photos += results['collection']

        while current_page < total_pages:
            print('downloading metadata, page {} of {}'.format(current_page, total_pages))
            current_page += 1
            print(get_photos(qs, page=current_page, original=original))
            photos += get_photos(qs, page=current_page, original=original)['collection']['items']
            time.sleep(0.5)

        with open(jsonfilename, 'w') as outfile:
            json.dump(photos, outfile)

    else:
        with open(jsonfilename, 'r') as infile:
            photos = json.load(infile)

    # download images
    print('Downloading images...')
    for data in tqdm(photos):
        try:
            url = "https://images-assets.nasa.gov/image/"+data['data'][0]['nasa_id']+"/"+data['data'][0]['nasa_id']+"~orig.jpg"
            localname = os.path.join(foldername, '{}.{}'.format(data['data'][0]['nasa_id'], 'jpg'))
            if not os.path.exists(localname):
                download_file(url, localname)
        except Exception as e:
            continue
    print("""   *                                                            *
                             aaaaaaaaaaaaaaaa               *
                         aaaaaaaaaaaaaaaaaaaaaaaa
                      aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                    aaaaaaaaaaaaaaaaa           aaaaaa
                  aaaaaaaaaaaaaaaa                  aaaa
                 aaaaaaaaaaaaa aa                      aa
*               aaaaaaaa      aa                         a
                aaaaaaa aa aaaa
          *    aaaaaaaaa     aaa
               aaaaaaaaaaa aaaaaaa                               *
               aaaaaaa    aaaaaaaaaa
               aaaaaa a aaaaaa aaaaaa
                aaaaaaa  aaaaaaa
                aaaaaaaa                                 a
                 aaaaaaaaaa                            aa
                  aaaaaaaaaaaaaaaa                  aaaa
                    aaaaaaaaaaaaaaaaa           aaaaaa        *
      *               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                         aaaaaaaaaaaaaaaaaaaaaaaa
                      *      aaaaaaaaaaaaaaaa""")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Download images from NASA')
    parser.add_argument('--search', '-s', dest='q_search', default=None, required=False, help='Search term')
    parser.add_argument('--original', '-o', dest='original', action='store_true', default=False, required=False, help='Download original sized photos if True, large (1024px) otherwise')
    parser.add_argument('--max-pages', '-m', dest='max_pages', required=False, help='Max pages (default none)')
    parser.add_argument('--start-page', '-st', dest='start_page', required=False, help='Start page (default 1)')
    args = parser.parse_args()

    qs = args.q_search
    original = args.original

    if qs is None:
        sys.exit('Must specify a search term')

    print('Searching for {}'.format(qs if qs is not None else ''))
  
    max_pages = None
    if args.max_pages:
        max_pages = int(args.max_pages)

    start_page = 1
    if args.start_page:
        start_page = int(args.start_page)


    search(qs, original, max_pages, start_page)

