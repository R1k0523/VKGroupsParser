import csv
import time
from datetime import datetime
import requests


class Info:
    def __init__(self, group_info: dict, date: int, text: str, img_url: str):
        '''
        Вспомогательный класс для вывода текста новостей
        '''
        self.group_info = group_info
        self.date = date
        self.text = text
        self.img_url = img_url

    def __str__(self):
        date_time = datetime.fromtimestamp(self.date)
        return f'Группа: {self.group_info["name"]}, Фото группы: {self.group_info["photo_200"]}\n' \
               f'Текст: {self.text}, \nДата: {date_time.strftime("%m/%d/%Y, %H:%M:%S")}\n Фото: {self.img_url}'


class NewsParser:

    def __init__(self, service_key, posts_len, domains, offset=0, version=5.92, file_name='file',
                 posts_per_request=100):
        '''
        Парсер новостей
        :type file_name: название файла
        :param service_key: сервисный ключ приложения ВК link: https://vk.com/apps?act=manage
        :param posts_len: количество постов для парсинга
        :param domains: имена групп
        :param offset: смещение
        :param version: версия API ВК
        '''
        if domains is None:
            domains = ['overhear_mtu']
        self.service_key = service_key
        self.domains = domains
        self.version = version
        self.offset = offset
        self.posts_per_request = posts_per_request
        self.posts_len = posts_len
        self.all_posts = None
        self.file_name = file_name

    def parse(self):
        all_posts = []
        for domain in self.domains:
            offset = self.offset
            domain_posts = []
            while offset < self.posts_len:
                response = requests.get('https://api.vk.com/method/wall.get',
                                        params={
                                            'access_token': token,
                                            'v': self.version,
                                            'domain': domain,
                                            'count': self.posts_per_request,
                                            'offset': self.offset
                                        }
                                        )
                data = response.json()['response']['items']
                offset += self.posts_per_request
                domain_posts.extend(data)
            group_id = domain_posts[0]['owner_id']
            domain_info = requests.get('https://api.vk.com/method/groups.getById',
                                       params={
                                           'access_token': token, 'v': self.version,
                                           'group_id': abs(group_id), 'fields': 'name'
                                       }
                                       ).json()['response'][0]
            for post in domain_posts:
                post['group_info'] = domain_info
            all_posts.extend(domain_posts)
        self.all_posts = all_posts
        return all_posts

    def write(self):
        with open(f'{self.file_name}.csv', 'w', encoding='utf-16') as file:
            row = csv.writer(file)
            row.writerow(('group_name', 'group_photo', 'date', 'body', 'image_url'))
            for post in self.all_posts:
                try:
                    if post['attachments'][0]['type']:
                        image_url = post['attachments'][0]['photo']['sizes'][-1]['url']
                except Exception as e:
                    image_url = 'No image'
                # print(Info(post['group_info'], post['date'], post['text'], image_url))
                row.writerow((post['group_info']['name'], post['group_info']['photo_200'],
                              post['date'], post['text'], image_url))


if __name__ == '__main__':
    token = ''
    parser = NewsParser(token, 100, file_name='pepega', domains=['vk', 'apiclub', 'vkmusic', 'edu'])
    print('Created Class')
    t = time.time()
    parser.parse()
    print(f'Parsed: {time.time() - t}')
    t = time.time()
    parser.write()
    print(f'Ended:  {time.time() - t}')
