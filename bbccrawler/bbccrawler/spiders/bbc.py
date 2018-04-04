# -*- coding: utf-8 -*-
import scrapy


class BbcSpider(scrapy.Spider):
    name = 'bbc'
    start_urls = ['http://www.bbc.com/', 'http://www.bbc.com/news']

    def start_requests(self):
        yield scrapy.Request(self.start_urls[1], self.parse)

    def parse(self, response):
        if response.url == self.start_urls[1]:
            urls = response.xpath('//a[contains(@class, "gs-c-promo-heading")]/@href').extract()
            for url in urls:
                yield scrapy.Request(url=self.start_urls[0] + url, callback=self.parse)
        else:
            story = "\n".join(list(filter(None, map(str.strip, response.xpath('//div[contains(@class, "story-body__inner")]/p/text()').extract()))))
            if story:
                yield {"story": story}
