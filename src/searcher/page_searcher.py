# encoding: utf-8

import os
import random
import time
import json

from search_helper.search_helper import GoogleHelper


class PageSearcher:

    def __init__(self, keyword, person_dict_list, result_path):
        self.names = []
        self.ok_name_list = []
        self.error_name_list = []
        self.keyword = keyword
        self.result_path = result_path
        self.person_dict_list = person_dict_list

    def get_page_file_path(self, person_name):
        return self.result_path + person_name + '/' + self.keyword.replace(' ', '_') + '.html'

    def get_google_page_from(self, person_name, search_helper):
        name = person_name.replace('\n', '')
        print '******', name, '*******'
        personal_path = self.result_path + name + '/'
        # 建立搜索引擎文件夹
        if not os.path.exists(self.result_path):
            os.mkdir(self.result_path)
        # 建立每个人的文件夹
        if not os.path.exists(personal_path):
            os.mkdir(personal_path)
        # 打开文件
        search_page_cache_file = open(self.get_page_file_path(person_name), 'w')
        try:
            # 获取搜索主页，并保存在个人文件夹下
            search_page_content = search_helper.get_search_page_by_name(name + ' ' + self.keyword)
            if search_page_content is None:
                self.error_name_list.append(name)
                print '[Error]@EmailSearcher.get_google_page_from(): search_page_content is None'
                with open('missing_name.txt', 'w') as missing_name_file:
                    for missing_name in self.error_name_list:
                        missing_name_file.write(str(missing_name) + '\n')
                return False
            search_page_cache_file.write(search_page_content)
            search_page_cache_file.close()
            self.ok_name_list.append(name)
            print name, 'OK...'
            with open('ok_name.txt', 'a') as ok_name_file:
                ok_name_file.write(str(name) + '\n')
            time.sleep(random.randint(1, 3))

        except Exception as e:
            print e
            self.error_name_list.append(name)
            with open(self.result_path + 'missing_name.txt', 'w') as missing_name_file:
                for missing_name in self.error_name_list:
                    missing_name_file.write(str(missing_name) + '\n')
            return False
        return True

    def start_from(self, start_name):
        flag = False
        person_name_list = [person_dict['name'] for person_dict in self.person_dict_list]
        try:
            for person_name in person_name_list:
                if person_name in os.listdir(self.result_path):
                    continue
                if person_name == start_name or start_name == '':
                    flag = True
                    if start_name:
                        print 'starting from', start_name
                if not flag:
                    continue
                self.get_google_page_from(str(person_name), GoogleHelper())
        except Exception as e:
            print e

    def refresh_empty_pages(self):
        for person_name in os.listdir(self.result_path):
            try:
                with open(self.get_page_file_path(person_name)) as search_page:
                    if len(search_page.read()) < 10:
                        self.get_google_page_from(person_name, GoogleHelper())
            except Exception as e:
                print e


if __name__ == '__main__':
    searcher = PageSearcher('email')
    searcher.start_from('')
    searcher.refresh_empty_pages()
