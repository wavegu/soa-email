# encoding=utf8
import json
import leveldb
from service_log import service_log
from classifier.svm import SVMLight
from classifier.person import Person
from classifier.aff_words_extractor import AffWordsExtractor
from classifier.util import create_dir_if_not_exist
from searcher.google_item_parser import GoogleItemParser

import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.dont_write_bytecode = True


class AminerEmailService:

    def __init__(self):
        self.task_person_list = []

    def get_task_person_list(self, size):
        import urllib
        query_url = 'http://alpha.api.aminer.org/api/fusion/person/ctasks/email/s/' + str(size)
        return_content = urllib.urlopen(query_url).read()
        return_dict = json.loads(return_content)
        return_status = return_dict['status']
        if not return_status:
            service_log.error_log('Aminer server error:' + return_dict['message'])
            exit()
        service_log.success_log('Get task_person_list')
        self.task_person_list = return_dict['tasks']
        


if __name__ == '__main__':
    service = AminerEmailService()
    service.get_task_person_list(10)
    for person in service.task_person_list:
        print person