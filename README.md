# Scrape NASA Images

## Installation

1. Clone the repo

2. Install requirements

`pip install -r requirements.txt`

## Usage

To scrape for a particular search term:

`python scraper.py --search "SEARCH TERM"

Limit the number of pages of results downloaded by passing `--max-pages N` where `N` is pages of 100 results each.  Specify the start page with `--start-page M`.
