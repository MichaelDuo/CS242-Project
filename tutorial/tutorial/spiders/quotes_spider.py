import scrapy

class Quotes_Spider(scrapy.Spider):
    name = "quotes"

    start_urls = [
        'http://quotes.toscrape.com/page/1/',
    ]
    
    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'autor': quote.css('small.autor::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall()
            }
        for a in response.css('li.next a'):
            print(a.css('::attr(href)').get())
            yield response.follow(a, callback=self.parse)