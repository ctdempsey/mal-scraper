import csv
import re
from dataclasses import dataclass
from time import sleep

import requests
from bs4 import BeautifulSoup

MAL_ANIME_SEARCH_URL = "https://myanimelist.net/anime.php"
QUERY_PARAMS = "?q=&type=1&score=0&status=0&p=0&r=0&sm=1&sd=1&sy=2010&em=0&ed=0&ey=0&c[0]=a&c[1]=b&c[2]=c&c[3]=f"
SORT_BY_SCORE_DESC_PARAM = "&o=3&w=1"
SORT_BY_MEMBERS_DESC_PARAM = "&o=7&w=1"
PAGE_PARAM = "&show="
STATS_PAGE_URL = "/stats"
CSV_FILENAME = "MAL_anime.csv"
ANIME_PER_PAGE = 50
MAX_PAGES_SEARCH = 5
MAX_REQUEST_RETRIES = 10
RETRY_PAUSE = 6
REQUEST_DELAY = 2


@dataclass
class AnimeInfo:
    title: str
    episodes: int
    premiered: str
    broadcast: str
    studios: str
    source: str
    genres: str
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


def get_html(url):
    sleep(REQUEST_DELAY)
    print("Sending GET request to: " + url)
    response = requests.get(url)
    retries = 0
    while response.status_code == 429 and retries < MAX_REQUEST_RETRIES:
        print(f"Received Too Many Requests Error. Retrying in {RETRY_PAUSE} seconds.")
        sleep(RETRY_PAUSE)
        response = requests.get(url)
        retries += 1
    if response.status_code != 200:
        print(f"Received Status Code {response.status_code}.")
        raise Exception("Couldn't get data")
    print("GET request completed.")
    return response.text


def get_anime_urls_from_page(html):
    soup = BeautifulSoup(html, "html.parser")
    anime_table = soup.find("div", "js-block-list").table
    anime_rows = anime_table.contents[1:]
    anime_urls = []
    for anime in anime_rows:
        if (anime.find("a") != -1):
            anime_urls.append(anime.find("a")["href"])
    return anime_urls


def get_anime_urls():
    print("Retrieving individual Anime page URLs.")
    anime_urls = set()
    by_score_url = MAL_ANIME_SEARCH_URL + QUERY_PARAMS + SORT_BY_SCORE_DESC_PARAM
    by_members_url = MAL_ANIME_SEARCH_URL + QUERY_PARAMS + SORT_BY_MEMBERS_DESC_PARAM

    for p in range(0, ANIME_PER_PAGE * MAX_PAGES_SEARCH, ANIME_PER_PAGE):
        by_score_page = get_html(by_score_url + PAGE_PARAM + str(p))
        if by_score_page is None:
            print(f"Failed to retrieve page {(p // ANIME_PER_PAGE) + 1} of Anime By Score." +
                  f"Returning {len(anime_urls)} found URLs.")
            return anime_urls
        prev_urls = len(anime_urls)
        anime_urls.update(get_anime_urls_from_page(by_score_page))
        print(f"Added {len(anime_urls) - prev_urls} URLs from page {(p // ANIME_PER_PAGE) + 1} of Anime By Score.")

        by_members_page = get_html(by_members_url + PAGE_PARAM + str(p))
        if by_members_page is None:
            print(f"Failed to retrieve page {(p // ANIME_PER_PAGE) + 1} of Anime By Members." +
                  f"Returning {len(anime_urls)} found URLs.")
            return anime_urls
        prev_urls = len(anime_urls)
        anime_urls.update(get_anime_urls_from_page(by_members_page))
        print(f"Added {len(anime_urls) - prev_urls} URLs from page {(p // ANIME_PER_PAGE) + 1} of Anime By Members.")
    print(f"Found total of {len(anime_urls)} Anime URLs.")
    return anime_urls


def get_anime_info(anime_url):
    anime_page = get_html(anime_url)
    print(f"Processing data from {anime_url}.")
    soup = BeautifulSoup(anime_page, "html.parser")
    title = soup.find("span", itemprop="name").string.strip()
    episodes = soup.find("span", string="Episodes:").next_sibling.string.strip()
    premiered = soup.find("span", string="Premiered:").parent.a.string.strip()
    broadcast = soup.find("span", string="Broadcast:").next_sibling.string.strip()
    studios = ', '.join([s.string.strip() for s in soup.find("span", string="Studios:").parent.find_all("a")])
    source = soup.find("span", string="Source:").next_sibling.string.strip()
    genres = ', '.join([g.string.strip() for g in soup.find_all("span", itemprop="genre")])
    ranked = int(soup.find("span", string="Ranked:").next_sibling.string.strip()[1:])
    popularity = int(soup.find("span", string="Popularity:").next_sibling.string.strip()[1:])
    favorites = int(soup.find("span", string="Favorites:").next_sibling.string.strip().replace(',', ''))
    total_members = int(soup.find("span", string="Members:").next_sibling.string.strip().replace(',', ''))
    weighted_score = float(soup.find("span", itemprop="ratingValue").string.strip())
    stats_page = get_html(anime_url + STATS_PAGE_URL)
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
    return AnimeInfo(title, episodes, premiered, broadcast, studios, source, genres, ranked, popularity, favorites,
                     total_members, weighted_score, scores_10, scores_9, scores_8, scores_7, scores_6, scores_5,
                     scores_4, scores_3, scores_2, scores_1, watching, completed, on_hold, dropped, plan_to_watch)


def export_to_csv(anime_info_list):
    print("Exporting retrieved Anime data to CSV file.")
    with open(CSV_FILENAME, "w", newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Title', 'Episodes', 'Premiered', 'Broadcast', 'Studios', 'Source', 'Genres', 'Ranked',
                         'Popularity', 'Favorites', 'Total Members', 'Weighted Score', '10 Scores', '9 Scores',
                         '8 Scores', '7 Scores', '6 Scores', '5 Scores', '4 Scores', '3 Scores', '2 Scores',
                         '1 Scores', 'Members Watching', 'Members Completed', 'Members On-Hold', 'Members Dropped',
                         'Members Plan to Watch'])
        for anime in anime_info_list:
            writer.writerow([anime.title, anime.episodes, anime.premiered, anime.broadcast, anime.studios, anime.source,
                             anime.genres, anime.ranked, anime.popularity, anime.favorites, anime.total_members,
                             anime.weighted_score, anime.scores_10, anime.scores_9, anime.scores_8, anime.scores_7,
                             anime.scores_6, anime.scores_5, anime.scores_4, anime.scores_3, anime.scores_2,
                             anime.scores_1, anime.members_watching, anime.members_completed, anime.members_on_hold,
                             anime.members_dropped, anime.members_plan_to_watch])
    print(f"Data saved to '{CSV_FILENAME}'.")


def main():
    print("Starting MAL Anime scraping.")
    anime_urls = get_anime_urls()
    anime_info_list = []
    total_anime = len(anime_urls)
    counter = 1
    for url in anime_urls:
        print(f"Getting info for Anime #{counter} of {total_anime}.")
        anime_info = get_anime_info(url)
        anime_info_list.append(anime_info)
        counter += 1
    export_to_csv(anime_info_list)
    print("MAL Anime scraping completed.")


if __name__ == "__main__":
    main()
