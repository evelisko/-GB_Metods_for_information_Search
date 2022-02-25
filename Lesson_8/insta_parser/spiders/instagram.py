# -*- coding: utf-8 -*-
import json
import re
from copy import deepcopy
from urllib.parse import urlencode

import scrapy
from scrapy.http import HtmlResponse

from insta_parser.items import InstaParserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_loginlink = 'https://www.instagram.com/accounts/login/ajax/'
    insta_login = 'здесь логин'
    insta_pwd = 'Здесь зашифрованный пароль'
    parse_users = ['ai_machine_learning', 'raspberrypi', 'madmaxmovie']
    followers_hash = 'c76146de99bb02f6415203be841dd25a'
    followings_hash = 'd04b0a864b4b54837c0d870b0e77e076'
    graphql_url = 'https://www.instagram.com/graphql/query/?'

    def parse(self, response):
        yield scrapy.FormRequest(
            self.insta_loginlink,
            method='POST',
            callback=self.page_pars,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': self.fetch_csrf_token(response.text)}
        )

    def page_pars(self, response: HtmlResponse):
        # print(response.text)
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for parse_user in self.parse_users:
                yield response.follow(
                    f'/{parse_user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': parse_user}
                )

    def user_data_parse(self, response: HtmlResponse, username):  # Список подписок,# Список подписчиков.
        user_id = self.fetch_user_id(response.text, username)  # Получаем id пользователя
        variables = {'id': user_id, 'first': 10}
        url_posts = f'{self.graphql_url}query_hash={self.followings_hash}&{urlencode(variables)}' 
        print(url_posts)
        yield response.follow(
            url_posts,
            callback=self.users_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables),  # variables ч/з deepcopy во избежание гонок
                       'edge_type': 'edge_follow',
                       'info_type': 'following'}
        )
    # -----------------------------------------------------------------------------------------------------------------------------------------
        url_posts = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
        yield response.follow(
            url_posts,
            callback=self.users_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables),
                       'edge_type': 'edge_followed_by',
                       'info_type': 'follower'}
        )

    def users_parse(self, response: HtmlResponse, username, user_id, variables, edge_type, info_type):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get(edge_type).get('page_info')
        print(f"page_info:{page_info}")
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            if info_type == 'following':
                url_posts = f'{self.graphql_url}query_hash={self.followings_hash}&{urlencode(variables)}'
            else:
                url_posts = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.users_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables),
                           'edge_type': edge_type,
                           'info_type': info_type}
            )
        users = j_data.get('data').get('user').get(edge_type).get('edges')  # Подписки
        for user in users:  # Перебираем посты, собираем данные
            item = InstaParserItem(
                current_user_name=username,
                current_user_id=user_id,
                follow_id=user['node']['id'],
                follow_name=user['node']['username'],
                follow_full_name=user['node']['full_name'],
                follow_pic_url=user['node']['profile_pic_url'],
                follow_user_type=info_type
                # post=user['node']
            )
            # print(item)
            yield item  # В пайплайн

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        print(matched)
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
