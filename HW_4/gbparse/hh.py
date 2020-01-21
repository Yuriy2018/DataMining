# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from gbparse.items import GbparseItem



class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = [f'https://hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text=Data+scientist&page={idx}' for idx in range(0,4)]

    def parse(self, response):
        print(1)
        for url in response.xpath('//div[@class="resume-search-item__name"]//a[@data-qa="vacancy-serp__vacancy-title"]'):
            yield response.follow(url, callback=self.post_parse)


    def post_parse(self,response: HtmlResponse):

         item = ItemLoader(GbparseItem(),response)
         # item.add_value('url',response.url)

         item.add_value('title', response.xpath("//div[@class='vacancy-title ']/h1/text()").extract_first())

         item.add_xpath('salary', '//p[@class="vacancy-salary"]/text()')
         # item.add_xpath('keySkils', '//div[@class="vacancy-branded-user-content"]/ul/li')
         item.add_xpath('keySkils', '//div[@class="g-user-content"]/p/span')
         item.add_value('organization', response.xpath('//span[@itemprop="name"]/span/text()').extract_first())

         item.add_xpath('organization_url', '//a[@class="vacancy-company-logo"]/@href')

         item.add_value('organization_photo', response.xpath("//a[@class='vacancy-company-logo']/img/@src").extract_first())

         print(1)

         yield item.load_item()
