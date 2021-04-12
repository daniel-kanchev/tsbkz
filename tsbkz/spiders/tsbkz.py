import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from tsbkz.items import Article


class tsbkzSpider(scrapy.Spider):
    name = 'tsbkz'
    start_urls = ['https://www.tsb.kz/en/news']

    def parse(self, response):
        links = response.xpath('//a[@class="posts-list-item-body-action-link"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//ul[@class="pagination"]//a/@href').getall()
        yield from response.follow_all(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="heading-title-text"]/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//section[@itemprop="articleBody"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
