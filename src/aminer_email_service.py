# encoding=utf8
import json
import sys

from service_log import service_log
from person import Person
from constants import DB_ID_PERSON_JSON

reload(sys)
sys.setdefaultencoding('utf8')

G_IS_TEST = False
sys.dont_write_bytecode = True


class AminerEmailService:

    def __init__(self):
        self.task_person_list = []

    def get_task_person_list(self, size):
        if G_IS_TEST:
            with open('../resource/test/test_person_list.json') as json_file:
                self.task_person_list = [Person(person_dict, is_test=True) for person_dict in json.load(json_file)]
        else:
            import urllib
            query_url = 'http://alpha.api.aminer.org/api/fusion/person/ctasks/email/s/' + str(size)
            print query_url
            return_content = urllib.urlopen(query_url).read()
            print return_content
            return_dict = json.loads(return_content)
            return_status = return_dict['status']
            if not return_status:
                service_log.error_log('Aminer server error:' + return_dict['message'])
                exit()
            service_log.success_log('Get task_person_list')
            for person_dict in return_dict['tasks']:
                print person_dict
            self.task_person_list = [Person(person_dict) for person_dict in return_dict['tasks']]


if __name__ == '__main__':
    service = AminerEmailService()
    service.get_task_person_list(10)
    for person in service.task_person_list:
        person.get_recommend_email()
        DB_ID_PERSON_JSON.Put(str(person.id), person.to_json())
        with open('../resource/test/' + person.name + '.json', 'w') as f:
            f.write(person.to_json())
