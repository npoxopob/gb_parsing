import os
import requests
import bs4
import time
from urllib.parse import urljoin
from dotenv import load_dotenv

from database import Database

from dateutil.parser import parse

class ParseError(Exception):
    def __init__(self, txt):
        self.txt = txt


class GbParse:
    def __init__(self, start_url, api_url, database):
        self.start_url = start_url
        self.api_url = api_url
        self.done_urls = set()
        self.tasks = [self.parse_task(self.start_url, self.pag_parse)]
        self.done_urls.add(self.start_url)
        self.database = database

    @staticmethod
    def _get_response(url, *args, **kwargs) -> requests.Response:
        while True:
            try:
                response = requests.get(url, *args, **kwargs)
                if response.status_code > 399:
                    raise ParseError(response.status_code)
                time.sleep(0.1)
                return response
            except (requests.RequestException, ParseError):
                time.sleep(0.5)
                continue

    def _get_soup(self, *args, **kwargs):
        response = self._get_response(*args, **kwargs)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        return soup

    def parse_task(self, url, callback):
        def wrap():
            soup = self._get_soup(url)
            return callback(url, soup)

        return wrap

    def run(self):
        for task in self.tasks:
            result = task()
            if result:
                self.database.create_post(result)

    def __unpack_items(self, comments, result):
        for comment in comments:
            result.append(comment)
            comment_children = comment['comment']['children']
            if len(comment_children) != 0:
                self.__unpack_items(comment_children, result)

        return result

    def _get_comments(self, _soup: bs4.BeautifulSoup) -> list:
        __cm_attrs = {"class": "referrals-social-buttons-small-wrapper"}
        commentable_id = _soup.find("div", attrs=__cm_attrs).attrs["data-minifiable-id"]

        __comments_params = f"comments?commentable_type=Post&commentable_id={commentable_id}&order=desc"
        url_comment_api = urljoin(self.api_url, __comments_params)

        request = self._get_response(url_comment_api).json()

        __comments = []

        if request:
            return self.__unpack_items(request, __comments)

        return __comments

    def post_parse(self, url, soup: bs4.BeautifulSoup) -> dict:
        author_name_tag = soup.find("div", attrs={"itemprop": "author"})

        data = {
            "post_data": {
                "url": url,
                "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                "img_url": soup.find("div", attrs={"class": "blogpost-content"}).img.attrs['src'],
                'date_time': parse(soup.find("div", attrs={"class": "blogpost-date-views"}).time.attrs['datetime'])
            },
            "author": {
                "url": urljoin(url, author_name_tag.parent.get("href")),
                "name": author_name_tag.text,
            },
            "tags": [
                {
                    "name": tag.text,
                    "url": urljoin(url, tag.get("href")),
                }
                for tag in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments": [
                {
                    "comment": {
                        "id": comment['comment']['id'],
                        "parent_id": comment['comment']['parent_id'],
                        "text": comment['comment']['body']
                    },
                    "writer": {
                        "author_name": comment['comment']['user']['full_name'],
                        "id": comment['comment']['user']['id']
                    }
                }
                for comment in self._get_comments(soup)
            ]
        }
        return data

    def pag_parse(self, url, soup: bs4.BeautifulSoup):
        gb_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        a_tags = gb_pagination.find_all("a")
        for a in a_tags:
            pag_url = urljoin(url, a.get("href"))
            if pag_url not in self.done_urls:
                task = self.parse_task(pag_url, self.pag_parse)
                self.tasks.append(task)
                self.done_urls.add(pag_url)

        posts_urls = soup.find_all("a", attrs={"class": "post-item__title"})
        for post_url in posts_urls:
            post_href = urljoin(url, post_url.get("href"))
            if post_href not in self.done_urls:
                task = self.parse_task(post_href, self.post_parse)
                self.tasks.append(task)
                self.done_urls.add(post_href)


if __name__ == "__main__":
    load_dotenv(".env")
    parser = GbParse("https://geekbrains.ru/posts",
                     "https://geekbrains.ru/api/v2/",
                     Database(os.getenv("SQL_DB")))
    parser.run()
