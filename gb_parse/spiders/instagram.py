import json
import scrapy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    tag_path = '/explore/tags/'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    
    def __init__(self, login, password, tags:list, *args, **kwargs):
        self.__login = login
        self.__password = password
        self.tags = tags
        super().__init__(*args, **kwargs)

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.__login,
                    'enc_password': self.__password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError:
            if response.json().get('authenticated'):
                for tag in self.tags:
                    tag_url = f'{self.tag_path}{tag}'
                    yield response.follow(tag_url, callback=self.tag_parse)
            print(1)
    
    def tag_parse(self, response):
        print(1)
        
    @staticmethod
    def js_data_extract(response) -> dict:
        script = response.xpath("/html/body/script[contains(text(), 'window._sharedData = ')]/text()").get()
        return json.loads(script.replace('window._sharedData = ', '')[:-1])
