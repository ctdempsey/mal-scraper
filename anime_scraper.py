import argparse
import csv
import re
import urllib3
import certifi
from dataclasses import dataclass
from datetime import date
from time import sleep

import requests
from bs4 import BeautifulSoup

MAL_ANIME_SEARCH_URL = "https://myanimelist.net/anime.php"
QUERY_PARAM = "?q="

ANIME_TYPE_PARAM = "&type="
ANIME_TYPE_OPTS = {
    "tv":      1,
    "ova":     2,
    "movie":   3,
    "special": 4,
    "ona":     5,
    "music":   6
}

ANIME_SCORE_PARAM = "&score="
ANIME_SCORE_OPTS = {
    "10": 10,
    "9":   9,
    "8":   8,
    "7":   7,
    "6":   6,
    "5":   5,
    "4":   4,
    "3":   3,
    "2":   2,
    "1":   1
}

ANIME_STATUS_PARAM = "&status="
ANIME_STATUS_OPTS = {
    "current":  1,
    "finished": 2,
    "nya":      3
}

ANIME_RATING_PARAM = "&r="
ANIME_RATING_OPTS = {
    "g":     1,
    "pg":    2,
    "pg-13": 3,
    "r":     4,
    "r+":    5,
    "rx":    6
}

ANIME_START_DAY_PARAM = "&sd="
ANIME_START_MONTH_PARAM = "&sm="
ANIME_START_YEAR_PARAM = "&sy="

ANIME_END_DAY_PARAM = "&ed="
ANIME_END_MONTH_PARAM = "&em="
ANIME_END_YEAR_PARAM = "&ey="

ANIME_SORT_BY_PARAM = "&o="
ANIME_SORT_BY_OPTS = {
    "alphabetical": 1,
    "type":         6,
    "episodes":     4,
    "score":        3,
    "start-date":   2,
    "end-date":     5,
    "members":      7,
    "rating":       8
}

ANIME_SORT_ORDER_PARAM = "&w="
ANIME_SORT_ORDER_OPTS = {
    "DESC": 1,
    "ASC": 2
}

SEARCH_PAGE_PARAM = "&show="

STATS_PAGE_URL = "/stats"

ANIME_PER_PAGE = 50

DEFAULT_OUTPUT_FILE = f"MAL_anime_{ date.today() }.csv"
DEFAULT_MAX_SEARCH = 100
DEFAULT_MAX_RETRIES = 5
DEFAULT_RETRY_PAUSE = 0.5
DEFAULT_REQUEST_DELAY = 2


@dataclass
class AnimeInfo:
    title: str
    anime_type: str
    episodes: int
    status: str
    aired: str
    premiered: str
    broadcast: str
    producers: str
    licensors: str
    studios: str
    source: str
    genres: str
    duration: str
    rating: str
    ranked: int
    popularity: int
    favorites: int
    total_members: int
    weighted_score: float
    scores_10: int
    scores_9: int
    scores_8: int
    scores_7: int
    scores_6: int
    scores_5: int
    scores_4: int
    scores_3: int
    scores_2: int
    scores_1: int
    members_watching: int
    members_completed: int
    members_on_hold: int
    members_dropped: int
    members_plan_to_watch: int


def get_html(url, delay=DEFAULT_REQUEST_DELAY, max_retries=DEFAULT_MAX_RETRIES, retry_pause=DEFAULT_RETRY_PAUSE):
    sleep(delay)
    print("Sending GET request to: " + url)
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where(),
                               retries=urllib3.Retry(total=max_retries, backoff_factor=retry_pause))
    response = http.request('GET', url)
    print("GET request completed.")
    return response.data.decode('utf-8')


def get_anime_urls_from_page(html):
    soup = BeautifulSoup(html, "html.parser")
    anime_list = soup.find("div", "js-block-list")
    if anime_list is None:
        return []
    anime_table = anime_list.table
    anime_rows = anime_table.contents[1:]
    anime_urls = []
    for anime in anime_rows:
        if (anime.find("a") != -1):
            anime_urls.append(anime.find("a")["href"])
    return anime_urls


def construct_search_url(**kwargs):
    url = [MAL_ANIME_SEARCH_URL]
    if len(kwargs) > 0:
        url.append(QUERY_PARAM)
    if kwargs["search"]:
        url.append("+".join(kwargs["search"].strip().lower().split()))
    if kwargs["type"]:
        url.append(ANIME_TYPE_PARAM + str(ANIME_TYPE_OPTS[kwargs["type"]]))
    if kwargs["score"]:
        url.append(ANIME_SCORE_PARAM + str(ANIME_SCORE_OPTS[kwargs["score"]]))
    if kwargs["status"]:
        url.append(ANIME_STATUS_PARAM + str(ANIME_STATUS_OPTS[kwargs["status"]]))
    if kwargs["rating"]:
        url.append(ANIME_RATING_PARAM + str(ANIME_RATING_OPTS[kwargs["rating"]]))
    if kwargs["start_date"]:
        start_date = kwargs["start_date"]
        url.append(ANIME_START_YEAR_PARAM + str(start_date.year))
        url.append(ANIME_START_MONTH_PARAM + str(start_date.month))
        url.append(ANIME_START_DAY_PARAM + str(start_date.day))
    if kwargs["end_date"]:
        end_date = kwargs["end_date"]
        url.append(ANIME_START_YEAR_PARAM + str(end_date.year))
        url.append(ANIME_START_MONTH_PARAM + str(end_date.month))
        url.append(ANIME_START_DAY_PARAM + str(end_date.day))
    if kwargs["order_by"]:
        url.append(ANIME_SORT_BY_PARAM + str(ANIME_SORT_BY_OPTS[kwargs["order_by"]]))
    if kwargs["order"]:
        url.append(ANIME_SORT_ORDER_PARAM + str(ANIME_SORT_ORDER_OPTS[kwargs["order"]]))

    return "".join(url)


def get_anime_urls(**kwargs):
    print("Retrieving individual Anime page URLs.")
    anime_urls = []
    max_urls = kwargs["max"]
    if max_urls == 0:
        max_urls = float('inf')
    delay = kwargs["delay"]
    max_retries = kwargs["retries"]
    retry_pause = kwargs["retry_pause"]

    search_url = construct_search_url(**kwargs)
    while len(anime_urls) < max_urls:
        new_search_url = search_url + SEARCH_PAGE_PARAM + str(len(anime_urls))
        search_page = get_html(new_search_url, delay, max_retries, retry_pause)
        prev_urls = len(anime_urls)
        results = get_anime_urls_from_page(search_page)
        if len(results) == 0:
            print("No new URLs found.")
            break
        anime_urls.extend(results)
        print(f"Found {len(anime_urls) - prev_urls} URLs.")

    if kwargs["max"] != 0:
        anime_urls = anime_urls[:max_urls]
    print(f"Returning total of {len(anime_urls)} Anime URLs.")
    return anime_urls


def get_anime_info(anime_url, **kwargs):
    delay = kwargs["delay"]
    max_retries = kwargs["retries"]
    retry_pause = kwargs["retry_pause"]

    anime_page = get_html(anime_url, delay, max_retries, retry_pause)
    print(f"Processing data from {anime_url}.")

    soup = BeautifulSoup(anime_page, "html.parser")
    title = soup.find("span", itemprop="name").string.strip()
    anime_type = soup.find("span", string="Type:").parent.a.string.strip()
    episodes = soup.find("span", string="Episodes:").next_sibling.string.strip()
    status = soup.find("span", string="Status:").next_sibling.string.strip()
    aired = soup.find("span", string="Aired:").next_sibling.string.strip()
    premiered = soup.find("span", string="Premiered:").parent.a.string.strip()
    broadcast = soup.find("span", string="Broadcast:").next_sibling.string.strip()
    producers = ', '.join([s.string.strip() for s in soup.find("span", string="Producers:").parent.find_all("a")])
    licensors = ', '.join([s.string.strip() for s in soup.find("span", string="Licensors:").parent.find_all("a")])
    if licensors == "add some":
        licensors = "None"
    studios = ', '.join([s.string.strip() for s in soup.find("span", string="Studios:").parent.find_all("a")])
    source = soup.find("span", string="Source:").next_sibling.string.strip()
    genres = ', '.join([g.string.strip() for g in soup.find_all("span", itemprop="genre")])
    duration = soup.find("span", string="Duration:").next_sibling.string.strip()
    rating = soup.find("span", string="Rating:").next_sibling.string.strip()
    ranked = int(soup.find("span", string="Ranked:").next_sibling.string.strip()[1:])
    popularity = int(soup.find("span", string="Popularity:").next_sibling.string.strip()[1:])
    favorites = int(soup.find("span", string="Favorites:").next_sibling.string.strip().replace(',', ''))
    total_members = int(soup.find("span", string="Members:").next_sibling.string.strip().replace(',', ''))
    weighted_score = float(soup.find("span", string="Score:").next_sibling.next_sibling.string.strip())

    stats_page = get_html(anime_url + STATS_PAGE_URL, delay, max_retries, retry_pause)
    print(f"Processing data from {anime_url}.")

    soup = BeautifulSoup(stats_page, "html.parser")
    watching = int(soup.find("span", string="Watching:").next_sibling.string.strip().replace(',', ''))
    completed = int(soup.find("span", string="Completed:").next_sibling.string.strip().replace(',', ''))
    on_hold = int(soup.find("span", string="On-Hold:").next_sibling.string.strip().replace(',', ''))
    dropped = int(soup.find("span", string="Dropped:").next_sibling.string.strip().replace(',', ''))
    plan_to_watch = int(soup.find("span", string="Plan to Watch:").next_sibling.string.strip().replace(',', ''))
    scores = soup.find_all("small", string=re.compile(r'votes'))
    scores_10 = int(scores[0].string.strip()[1:-7])
    scores_9 = int(scores[1].string.strip()[1:-7])
    scores_8 = int(scores[2].string.strip()[1:-7])
    scores_7 = int(scores[3].string.strip()[1:-7])
    scores_6 = int(scores[4].string.strip()[1:-7])
    scores_5 = int(scores[5].string.strip()[1:-7])
    scores_4 = int(scores[6].string.strip()[1:-7])
    scores_3 = int(scores[7].string.strip()[1:-7])
    scores_2 = int(scores[8].string.strip()[1:-7])
    scores_1 = int(scores[9].string.strip()[1:-7])

    print(f"Extracted data for {title}.")
    return AnimeInfo(title, anime_type, episodes, status, aired, premiered, broadcast, producers, licensors, studios,
                     source, genres, duration, rating, ranked, popularity, favorites,
                     total_members, weighted_score, scores_10, scores_9, scores_8, scores_7, scores_6, scores_5,
                     scores_4, scores_3, scores_2, scores_1, watching, completed, on_hold, dropped, plan_to_watch)


def export_to_csv(anime_info_list, filename):
    print("Exporting retrieved Anime data to CSV file.")
    with open(filename, "w", newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Title', 'Type', 'Episodes', 'Status', 'Aired', 'Premiered', 'Broadcast', 'Producers',
                         'Licensors', 'Studios', 'Source', 'Genres', 'Duration', 'Rating', 'Ranked',
                         'Popularity', 'Favorites', 'Total Members', 'Weighted Score', '10 Scores', '9 Scores',
                         '8 Scores', '7 Scores', '6 Scores', '5 Scores', '4 Scores', '3 Scores', '2 Scores',
                         '1 Scores', 'Members Watching', 'Members Completed', 'Members On-Hold', 'Members Dropped',
                         'Members Plan to Watch'])
        for anime in anime_info_list:
            writer.writerow([anime.title, anime.anime_type, anime.episodes, anime.status, anime.aired, anime.premiered,
                             anime.broadcast, anime.producers, anime.licensors, anime.studios, anime.source,
                             anime.genres, anime.duration, anime.rating, anime.ranked, anime.popularity,
                             anime.favorites, anime.total_members, anime.weighted_score, anime.scores_10,
                             anime.scores_9, anime.scores_8, anime.scores_7, anime.scores_6, anime.scores_5,
                             anime.scores_4, anime.scores_3, anime.scores_2, anime.scores_1, anime.members_watching,
                             anime.members_completed, anime.members_on_hold, anime.members_dropped,
                             anime.members_plan_to_watch])
    print(f"Data saved to '{filename}'.")


def get_args():
    parser = argparse.ArgumentParser(description="Download Anime info from MyAnimeList.")
    search_opts = parser.add_argument_group("Search Options")
    search_opts.add_argument("-o", "--output", default=DEFAULT_OUTPUT_FILE)
    search_opts.add_argument("-s", "--search")
    search_opts.add_argument("--max", type=int, default=DEFAULT_MAX_SEARCH)
    search_opts.add_argument("--type", choices=ANIME_TYPE_OPTS.keys())
    search_opts.add_argument("--score", choices=ANIME_SCORE_OPTS.keys())
    search_opts.add_argument("--status", choices=ANIME_STATUS_OPTS.keys())
    search_opts.add_argument("--rating", choices=ANIME_RATING_OPTS.keys())
    search_opts.add_argument("--start-date", type=lambda s: date.fromisoformat(s))
    search_opts.add_argument("--end-date", type=lambda s: date.fromisoformat(s))
    search_opts.add_argument("--order-by", choices=ANIME_SORT_BY_OPTS.keys())
    search_opts.add_argument("--order", choices=ANIME_SORT_ORDER_OPTS.keys())
    request_opts = parser.add_argument_group("Request Options")
    request_opts.add_argument("--retries", type=int, default=DEFAULT_MAX_RETRIES)
    request_opts.add_argument("--retry-pause", type=float, default=DEFAULT_RETRY_PAUSE)
    request_opts.add_argument("--delay", type=int, default=DEFAULT_REQUEST_DELAY)
    # parser.print_help()
    # parser.print_usage()
    args = parser.parse_args()
    return vars(args)


def main():
    args = get_args()
    print("Starting MAL Anime scraping.")
    anime_urls = get_anime_urls(**args)
    anime_info_list = []
    total_anime = len(anime_urls)
    counter = 1
    try:
        for url in anime_urls:
            print(f"Getting info for Anime #{counter} of {total_anime}.")
            anime_info = get_anime_info(url, **args)
            anime_info_list.append(anime_info)
            counter += 1
        print("All requested Anime info has been retrieved..")
    except (KeyboardInterrupt, SystemExit):
        print("Exiting early. Saving completed work.")
    finally:
        export_to_csv(anime_info_list, args["output"])
    print("MAL Anime scraping completed.")


if __name__ == "__main__":
    main()
