# encoding: utf-8
import os
import json

from util import is_a_in_b
from searcher.google_item_parser import GoogleItemParser
from classifier.svm import SVMLight
from classifier.email_model import EmailModel
from constants import DB_ID_PERSON_JSON
from service_log import service_log


MIN_GOOGLE_PAGE_CONTENT_LENGTH = 1024


class Person:

    def __init__(self, person_dict, is_test=False):
        self.is_test = is_test
        self.id = str(person_dict['id'])
        self.name = str(person_dict['name'])
        self.affiliation = str(person_dict['org'])

        self.google_page_content = ''
        self.google_item_dict_list = []
        self.email_email_model_dict = {}
        self.personal_email_model_list = []
        self.recommend_email_list = []

        from classifier.aff_words_extractor import AffWordsExtractor
        extractor = AffWordsExtractor(os.path.join('..', 'resource', 'aff_stopwords.txt'))
        self.affiliation_word_list = extractor.get_aff_words_list(self.affiliation)
        # self.get_google_item_dict_list()
        # self.get_email_email_model_dict()

    def __get_google_page__(self):
        service_log.debug_log('Getting google page content:' + self.name)
        if self.is_test:
            with open('../resource/test/test_google_page/'+self.name+'.html') as google_page:
                self.google_page_content = google_page.read()
                return self.google_page_content
        else:
            try:
                from searcher.page_searcher import PageSearcher
                page_searcher = PageSearcher('email')
                self.google_page_content = page_searcher.get_google_page(self.name)
            except Exception as e:
                service_log.error_log('Getting google page content:' + self.name + '\n       ' + str(e))
            return self.google_page_content

    def get_google_item_dict_list(self):
        try:
            self.__get_google_page__()
            fail_time = 0
            while fail_time < 4 and len(self.google_page_content) < MIN_GOOGLE_PAGE_CONTENT_LENGTH:
                fail_time += 1
                service_log.error_log('Trying to refind google page: %s [%d]' % (self.name, fail_time))
                self.__get_google_page__()
            if fail_time >= 4:
                raise LookupError
            item_parser = GoogleItemParser()
            self.google_item_dict_list = item_parser.parse_google_items_from_google_pages(self.google_page_content)
            service_log.success_log('Getting google items:' + self.name)
        except LookupError:
            service_log.error_log('Refind google page fails:' + self.name)
            self.google_item_dict_list = []
        except Exception as e:
            service_log.error_log('Getting google items:' + self.name + '\n       ' + str(e))
            self.google_item_dict_list = []
        return self.google_item_dict_list

    def get_email_email_model_dict(self):
        for google_item_dict in self.google_item_dict_list:
            title = google_item_dict['title'].lower()
            content = google_item_dict['content'].lower()
            cite_url = google_item_dict['cite_url'].lower()
            cite_name = google_item_dict['cite_name'].lower()
            email_addr_list = google_item_dict['email_addr_list']

            for email_addr in email_addr_list:
                # 若当前email地址没有对应的email_model，则创建一个新的
                if email_addr not in self.email_email_model_dict:
                    tag = -1
                    self.email_email_model_dict[email_addr] = EmailModel(self.name, email_addr, self.get_all_email_addr_list(), tag)
                # 对当前model进行google_item相关的参数赋值
                person_last_name = self.name.lower().split(' ')[-1]
                tem_email_model = self.email_email_model_dict[email_addr]
                tem_email_model.is_last_name_in_google_title = tem_email_model.is_last_name_in_google_title or is_a_in_b(person_last_name, title)
                tem_email_model.is_last_name_in_google_content = tem_email_model.is_last_name_in_google_content or is_a_in_b(person_last_name, content)

                # TODO: is_affiliation_in_google_title
                aff_word_num_in_title = 0
                aff_word_num_in_content = 0
                for aff_word in self.affiliation_word_list:
                    if is_a_in_b(aff_word, title):
                        aff_word_num_in_title += 1
                    if is_a_in_b(aff_word, content):
                        aff_word_num_in_content += 1
                aff_word_proportion_in_title = float(aff_word_num_in_title) / float(len(self.affiliation_word_list)+1)
                aff_word_proportion_in_content = float(aff_word_num_in_content) / float(len(self.affiliation_word_list)+1)
                if tem_email_model.max_affiliation_proportion_in_title < aff_word_proportion_in_title:
                    tem_email_model.max_affiliation_proportion_in_title = aff_word_proportion_in_title
                if tem_email_model.max_affiliation_proportion_in_content < aff_word_proportion_in_content:
                    tem_email_model.max_affiliation_proportion_in_content = aff_word_proportion_in_content

                self.email_email_model_dict[email_addr] = tem_email_model

    def write_feature_file(self, feature_dir_path):
        feature_file_path = feature_dir_path + self.name.replace(' ', '_') + '.feature'
        with open(feature_file_path, 'w') as feature_file:
            print 'writing feature:', self.name
            if not self.google_item_dict_list:
                return
            for email_addr, email_model in self.email_email_model_dict.items():
                feature_file.write(email_model.get_feature_line() + '\n')

    def to_json(self):
        person_dict = {
            'id': str(self.id),
            'name': self.name,
            'org': self.affiliation,
            'google_item_list': self.google_item_dict_list,
            'recommend_email_list': self.recommend_email_list
        }
        return json.dumps(person_dict, indent=4)

    def get_recommend_email_list(self):
        try:
            person_json = DB_ID_PERSON_JSON.Get(self.id)
            person_dict = json.loads(person_json)
            self.recommend_email_list = person_dict['recommend_email_list']
            if not self.recommend_email_list:
                raise KeyError
            else:
                service_log.success_log('Recommend email list already in:' + self.name)
                return self.recommend_email_list
        except KeyError:
            service_log.debug_log('Getting recommend email list:' + self.name)
            self.recommend_email_list = []
            self.get_google_item_dict_list()
            for item in self.google_item_dict_list:
                self.recommend_email_list += item['email_addr_list']
        except Exception as e:
            service_log.error_log('Getting recommend email list:' + self.name + '\n       ' + str(e))
        return self.recommend_email_list