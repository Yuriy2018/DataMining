# -*- coding: utf-8 -*-
import re
import scrapy
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from gbparse.items import InstagramItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = '***'
    insta_pass  = '***'
    insta_login_link = 'https://instagram.com/accounts/login/ajax/'
    parse_user = '***'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    user_data_hash = 'c9100bf9110dd636167f113dd02e7d6'
    following_hash =  'd04b0a864b4b54837c0d870b0e77e076' # Я на кого подписан
    followers_hash = 'c76146de99bb02f6415203be841dd25a' # Кто на меня подписан
    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.insta_login_link,
            method="POST",
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'password': self.insta_pass},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            yield response.follow(
                f'/{self.parse_user}',
                callback=self.userdata_parse,
                cb_kwargs={'username': self.parse_user}

            )

    def userdata_parse(self, response:HtmlResponse, username):
        # user_id = self.fetch_user_id(response.text, username)
        hash_list = [self.followers_hash, self.following_hash]  # Список хэша подпищик и подписка
        user_list = ['5739008676','1920756005',	"23116470535"]  # Список id пользователей у которых парсятся подписки и подписчики
        for user_id in user_list:
            for curr_hash in hash_list:
                varibles = {
                    'id': user_id,
                    "include_chaining": True,
                    "include_reel": True,
                    "include_logged_out_extras": False,
                    'first':50,
                }

                url = f'{self.graphql_url}query_hash={curr_hash}&{urlencode(varibles)}'

                yield response.follow(
                    url,
                    callback=self.user_data,
                    cb_kwargs={'username': username,'user_id': user_id,'curr_hash': curr_hash}
                )

    def user_data(self, response:HtmlResponse, username, user_id, curr_hash):
        J_user_data = json.loads(response.text)

        if curr_hash == 'c76146de99bb02f6415203be841dd25a':
            status = 'followers'
            list_data = J_user_data['data']['user']['edge_followed_by']['edges']
            next = J_user_data['data']['user']['edge_followed_by']['page_info']['end_cursor']
        else:
            status = 'following'
            list_data = J_user_data['data']['user']['edge_follow']['edges']
            next = J_user_data['data']['user']['edge_follow']['page_info']['end_cursor']


        if next != None:
            # user_id = user_id
            varibles = {
                'id': user_id,
                "include_chaining": True,
                "include_reel": True,
                "include_logged_out_extras": False,
                'first': 50,
                'after': next,
            }

            url = f'{self.graphql_url}query_hash={curr_hash}&{urlencode(varibles)}'

            yield response.follow(
                url,
                callback=self.user_data,
                cb_kwargs={'username': username, 'user_id': user_id, 'curr_hash': curr_hash}
            )




        for fol in list_data:
            id_user = fol['node']['id']
            username = fol['node']['username']
            full_name = fol['node']['full_name']
            yield {'main id':user_id, 'status': status, 'id user':id_user, 'username':username, 'full_name':full_name}
            # item = InstagramItem(user_id=user_id,   Закомментировал, решил обойтись без items
            #                      id_user=id_user,
            #                      username=username,
            #                      full_name=full_name,
            #                      status=status)
            # yield item
            # followed[key] = value


    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"','')


    def fetch_user_id(self, text, username):
        matched = re.search('\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
        return json.loads(matched).get('id')

