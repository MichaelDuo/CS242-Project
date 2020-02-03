# -*- coding: utf-8 -*-
import scrapy
import logging
from scrapy.utils.log import configure_logging
import os
import json

projectPath = os.getcwd()
dataPath = os.path.join(projectPath, 'data')

def prepare():
    if os.path.exists(dataPath):
        print('Exists')
    else:
        try:
            os.mkdir(dataPath)
        except OSError:
            print('Data directory creation failed')
        else:
            print('Data directory creation succeed')

class WikipediaSpider(scrapy.Spider):
    prepare()
    name = 'wikipedia'
    allowed_domains = ['wikipedia.org']
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
    }
    start_urls = ['https://en.wikipedia.org/wiki/University_of_California,_Riverside']

    crawledUrl = set() # Prevent duplication

    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt', 
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    def parse(self, response):
        content = response.css('#content')
        header = content.css('#firstHeading::text').get()
        contents = response.css('#mw-content-text p::text').getall()
        bodyText = ''.join(contents)
        urls = content.css('a::attr(href)').getall()

        self.save({
            'header': header,
            'url': response.url,
            'body': bodyText,
            'urls': urls
        })

        urls = urls[:5]
        for url in urls:
            next_page = response.urljoin(url)
            if next_page not in self.crawledUrl and self.isValidUrl(url):
                self.crawledUrl.add(next_page)
                yield scrapy.Request(next_page, callback=self.parse)

    def save(self, data):
        filename = '%s.json' % data['header']
        filepath = os.path.join(dataPath, filename)
        filepath = filepath.replace(" ", "_")
        with open(filepath, 'w') as f:
            json.dump(data, f)
    
    def isValidUrl(self, url):
        if 'File:' in url:
            return False
        return True