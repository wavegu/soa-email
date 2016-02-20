# encoding: utf-8

import os
import random
import time
import json

from search_helper.search_helper import GoogleHelper


class PageSearcher:

    def __init__(self, keyword):
        self.names = []
        self.error_name_list = []
        self.keyword = keyword

    def get_google_page(self, person_name):
        name = person_name.replace('\n', '')
        print '******', name, '*******'
        try:
            search_page_content = GoogleHelper.get_search_page_by_name(name + ' ' + self.keyword)
            if search_page_content is None:
                self.error_name_list.append(name)
                print '[Error]@EmailSearcher.get_google_page_from(): search_page_content is None'
                with open('missing_name.txt', 'w') as missing_name_file:
                    for missing_name in self.error_name_list:
                        missing_name_file.write(str(missing_name) + '\n')
                return False
            print name, 'OK...'
            time.sleep(random.randint(1, 3))

        except Exception as e:
            print e
            self.error_name_list.append(name)
            # with open(self.result_path + 'missing_name.txt', 'w') as missing_name_file:
            #     for missing_name in self.error_name_list:
            #         missing_name_file.write(str(missing_name) + '\n')
            return ''
        return search_page_content

if __name__ == '__main__':
    searcher = PageSearcher('email')
    content = searcher.get_google_page('jietang')
    print content
