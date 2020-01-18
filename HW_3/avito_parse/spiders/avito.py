# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse

class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/rossiya/kvartiry/prodam?cd=1&p=1']

    def parse(self, response):

        s = response.css('.pagination-page::text').extract() # Находим элемент в HTML
        if s[len(s)-1] == 'Последняя':   # Проверяем на присутствие "Последняя", если присутствует, значет мы не на последней странице
           numPage = str(response.request.url).split('p=')[1]
           if numPage == '':
               numPage = 2
           else:
               numPage = int(numPage) + 1 # Получаем номер следующей страницы
           nextpage = '/rossiya/kvartiry/prodam?cd=1&p=' + str(numPage) # собираем ссылку на следующию страницу с постами(квартир)
           print(nextpage)
           yield response.follow(nextpage, callback=self.parse) # Переходим на следующию страницу с квартирами


        sp = response.css('.js-item-extended-contacts::attr(data-item-url)').extract() # Получаем  список квартир на страние
        for i in  sp: # Обходим квартир на странице
            yield response.follow(i, callback=self.post_parse)


    def post_parse(self, response: HtmlResponse): # В этой процедуре извлекаем из поста данные:
        title = response.css('h1 span::text').extract_first()                             #Заголовок
        price = response.css('span .js-item-price::text').extract_first()                 #Цена

        spPar = response.css('.item-params-list-item').extract() # получение списка параметров квартиры
        Params = {}
        for Par in spPar:                                                                 #Параметры
            label = Par.split('<span class="item-params-label">')[1].split(': </span>')[0]
            Value = Par.split('</span>')[1].replace(' </li>','')
            Params[label] = Value

        yield {'title': title,
               'price': price,
               'parameters': Params}





