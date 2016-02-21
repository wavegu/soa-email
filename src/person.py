# encoding: utf-8
import os
import json

from util import is_a_in_b
from classifier.svm_node import SvmNode
from searcher.google_item_parser import GoogleItemParser
from constants import DB_ID_PERSON_JSON
from constants import SVM_LOG_PATH
from constants import SVM_MODEL_PATH
from constants import SVM_CLASSIFIER_PATH
from constants import SVM_FEATURE_FILE_PATH
from constants import SVM_PREDICTION_FILE_PATH
from service_log import service_log


SVM_THRESHOLD = 0
MIN_GOOGLE_PAGE_CONTENT_LENGTH = 1024


class Person:

    def __init__(self, person_dict, is_test=False):
        self.is_test = is_test
        self.id = str(person_dict['id'])
        self.name = str(person_dict['name'])
        self.affiliation = str(person_dict['org'])

        self.google_page_content = ''
        self.google_item_dict_list = []
        self.abandoned_email_list = []
        self.recommend_email = ''

        from classifier.aff_words_extractor import AffWordsExtractor
        extractor = AffWordsExtractor(os.path.join('..', 'resource', 'aff_stopwords.txt'))
        self.affiliation_word_list = extractor.get_aff_words_list(self.affiliation)

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
        from copy import copy
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
            raw_item_dict_list = item_parser.parse_google_items_from_google_pages(self.google_page_content)
            for raw_item_dict in raw_item_dict_list:
                for email_addr in raw_item_dict['email_addr_list']:
                    item_dict = copy(raw_item_dict)
                    item_dict.pop('email_addr_list')
                    item_dict['email_addr'] = email_addr
                    item_dict['person_name'] = self.name
                    self.google_item_dict_list.append(item_dict)
            service_log.success_log('Getting google items:' + self.name)
        except LookupError:
            service_log.error_log('Refind google page fails:' + self.name)
            self.google_item_dict_list = []
        except Exception as e:
            service_log.error_log('Getting google items:' + self.name + '\n       ' + str(e))
            self.google_item_dict_list = []
        return self.google_item_dict_list

    def to_json(self):
        person_dict = {
            'id': str(self.id),
            'name': self.name,
            'org': self.affiliation,
            'google_item_list': self.google_item_dict_list,
            'recommend_email': self.recommend_email,
            'abandoned_email_list': self.abandoned_email_list,
            'aff_words': self.affiliation_word_list
        }
        return json.dumps(person_dict, indent=4)

    def svm_predict(self):
        all_emails = [item['email_addr'] for item in self.google_item_dict_list]
        with open(SVM_FEATURE_FILE_PATH, 'w') as feature_file:
            for item_dict in self.google_item_dict_list:
                svm_node = SvmNode(item_dict, self.affiliation_word_list, all_emails)
                feature_file.write(svm_node.get_svm_feature_line())
        cmd = SVM_CLASSIFIER_PATH + ' ' + SVM_FEATURE_FILE_PATH + ' ' + SVM_MODEL_PATH + ' ' + SVM_PREDICTION_FILE_PATH + ' > ' + SVM_LOG_PATH
        os.system(cmd)

    def get_recommend_email(self):
        # if already have recommend record, return history recommend directly
        try:
            person_json = DB_ID_PERSON_JSON.Get(self.id)
            person_dict = json.loads(person_json)
            self.recommend_email = person_dict['recommend_email']
            if not self.recommend_email:
                raise KeyError
            else:
                service_log.success_log('Recommend email list already in:' + self.name)
                return self.recommend_email
        # if no history record
        except KeyError:
            service_log.debug_log('Getting recommend email list:' + self.name)
            self.recommend_email = ''
            self.get_google_item_dict_list()
            self.svm_predict()
            with open(SVM_PREDICTION_FILE_PATH) as prediction_file:
                max_svm_value = -999.9
                for line in prediction_file.readlines():
                    prediction_value = float(line)
                    if prediction_value > max_svm_value and prediction_value > SVM_THRESHOLD:
                        max_svm_value = prediction_value
            with open(SVM_PREDICTION_FILE_PATH) as prediction_file:
                looper = 0
                for line in prediction_file.readlines():
                    prediction_value = float(line)
                    if prediction_value == max_svm_value:
                        self.recommend_email += self.google_item_dict_list[looper]['email_addr'] + ' ' + line.replace('\n', '') + ','
                    else:
                        self.abandoned_email_list.append(self.google_item_dict_list[looper]['email_addr'] + ' ' + line.replace('\n', ''))
                    looper += 1
                if self.recommend_email and self.recommend_email[-1] == ',':
                    self.recommend_email = self.recommend_email[:-1]

        except Exception as e:
            service_log.error_log('Getting recommend email list:' + self.name + '\n       ' + str(e))
        return self.recommend_email