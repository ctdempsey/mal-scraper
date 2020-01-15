# MAL Scraper
A Python web scraper for retrieving anime data from [MyAnimeList](https://myanimelist.net/).
Scrapes all relevant data for each requested anime title and saves it as a CSV spreadsheet.

## Installation

Install the Python distribution and Python packages listed below in Prerequisites.
Download [anime_scraper.py](./anime_scraper.py) to your computer.
Follow the usage guide to start using the Python script.

### Prerequisites

- [Python 3.7+](https://www.python.org/downloads/)
- [urllib3](https://urllib3.readthedocs.io/en/latest/)
- [certifi](https://pypi.org/project/certifi/)
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)

##  Usage
Command-line arguments and usage are listed below. Most of the search options correspond
to equivalent options in MyAnimeList's own online search function. If a search option
is not used, then whatever MyAnimeList's search function defaults to will be used instead.

It is **highly recommended** that the `retry-pause` and `delay` options are left on
default, or even increased, so as to reduce the strain on MyAnimeList's servers and
prevent you from being blocked or registered as a DDOS attack (Can't guarantee
that it will happen, but also won't guarantee that it won't).


```
usage: anime_scraper.py [-h] [-o OUTPUT] [-s SEARCH] [--max MAX]
                        [--type {tv,ova,movie,special,ona,music}]
                        [--score {10,9,8,7,6,5,4,3,2,1}]
                        [--status {current,finished,nya}]
                        [--rating {g,pg,pg-13,r,r+,rx}]
                        [--start-date START_DATE] [--end-date END_DATE]
                        [--order-by {alphabetical,type,episodes,score,start-date,end-date,members,rating}]
                        [--order {DESC,ASC}] [--retries RETRIES]
                        [--retry-pause RETRY_PAUSE] [--delay DELAY]

Download Anime info from MyAnimeList.

optional arguments:
  -h, --help            show this help message and exit

Search Options:
  -o OUTPUT, --output OUTPUT
                        name of file that results are saved to
  -s SEARCH, --search SEARCH
                        key words to search for using MAL's search algorithm
  --max MAX             maximum number of results returned (default: 100) (0 for no limit)
  --type {tv,ova,movie,special,ona,music}
                        anime type restriction
  --score {10,9,8,7,6,5,4,3,2,1}
                        anime score restriction
  --status {current,finished,nya}
                        anime status restriction
  --rating {g,pg,pg-13,r,r+,rx}
                        anime rating restriction
  --start-date START_DATE
                        earliest anime start date (YYYY-MM-DD)
  --end-date END_DATE   latest anime end date (YYYY-MM-DD)
  --order-by {alphabetical,type,episodes,score,start-date,end-date,members,rating}
                        what to order anime search results by
  --order {DESC,ASC}    anime search result order

Request Options:
  --retries RETRIES     maximum number of times to retry each web request (default: 5)
  --retry-pause RETRY_PAUSE
                        how many seconds to pause before each web request (default: 0.5)
  --delay DELAY         backoff factor applied between request retries, equal to
                        {DELAY}*(2**({no. of retries}-1)) seconds (default: 2)

```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
