import json
import time
from pathlib import Path
import requests
import os

class ParseError(Exception):
    def __init__(self, txt):
        self.txt = txt


class Parser:
    _params = {
        "records_per_page": 100,
        "page": 1,
    }
    _headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    }

    def __init__(self, start_url, result_path):
        self.start_url = start_url
        self.result_path = result_path

        _ = self.result_path.mkdir() if not self.result_path.is_dir() else 0

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

    @staticmethod
    def save_to_json_file(data: dict, path, file_name):
        with open(f"{path}/{file_name}.json", "w", encoding="UTF-8") as file:
            json.dump(data, file, ensure_ascii=False)

class Parser5kaProductsSO(Parser):
    """
        Products in special offers
    """
    def run(self):
        for product in self.parse(self.start_url):
            self.save_to_json_file(product, self.result_path, f"{product['id']}.json")

    def parse_product(self, url):
        params = self._params
        while url:
            response = self._get_response(url, params=params, headers=self._headers)
            if params:
                params = {}
            data = json.loads(response.text)
            url = data.get("next")
            for product in data.get("results"):
                yield product

class Parse5kaCategory(Parser5kaProductsSO):

    def __init__(self, start_url, category_url, result_path):
        super().__init__(start_url, result_path)
        self.category_url = category_url

    def get_categories(self, url):
        response = requests.get(url, headers=self._headers)
        return response.json()

    def run(self):
        for category in self.get_categories(self.category_url):
            data = {
                "name": category["parent_group_name"],
                "code": category["parent_group_code"],
                "products": [],
            }

            self._params["categories"] = category["parent_group_code"]

            for products in self.parse_product(self.start_url):
                data["products"].extend([products])
                
            self.save_to_json_file(data, self.result_path, category["parent_group_code"])


if __name__ == "__main__":
    parser = Parse5kaCategory(start_url="https://5ka.ru/api/v2/special_offers/",
                              category_url="https://5ka.ru/api/v2/categories/",
                              result_path=Path(__file__).parent.joinpath("category"))
    parser.run()
