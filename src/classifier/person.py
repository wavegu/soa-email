# encoding: utf-8

import json

from svm import SVMLight
from util import is_a_in_b
from email_model import EmailModel


class Person:

    def __init__(self, person_dict, google_item_dir_path):
        self.name = person_dict['name']
        self.google_item_dir_path = google_item_dir_path
        self.affiliation_word_list = person_dict['affiliation_words']
        self.google_item_dict_list = []

        self.email_email_model_dict = {}
        self.personal_email_model_list = []
        self.get_google_item_dict_list()
        self.get_email_email_model_dict()

    def get_all_email_addr_list(self):
        all_email_addr_list = []
        for google_item_dict in self.google_item_dict_list:
            all_email_addr_list += google_item_dict['email_addr_list']
        return all_email_addr_list

    def get_google_item_dict_list(self):
        with open(self.google_item_dir_path + self.name + '.json') as google_item_file:
            self.google_item_dict_list = json.loads(google_item_file.read())
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
