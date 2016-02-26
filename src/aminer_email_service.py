# encoding=utf8
import json
import time
import sys

from service_log import service_log
from person import Person
from constants import DB_ID_PERSON_JSON

reload(sys)
sys.setdefaultencoding('utf8')

G_IS_TEST = False
G_SLEEP_SECONDS = 10
sys.dont_write_bytecode = True


class AminerEmailService:

    def __init__(self):
        self.task_person_list = []
        self.post_url = 'http://alpha.api.aminer.org/api/fusion/person/ctasks/email'

    def get_task_person_list(self, size):
        if G_IS_TEST:
            with open('../resource/test/test_person_list.json') as json_file:
                self.task_person_list = [Person(person_dict, is_test=True) for person_dict in json.load(json_file)]
        else:
            import urllib
            query_url = 'http://alpha.api.aminer.org/api/fusion/person/ctasks/email/s/' + str(size)
            return_content = urllib.urlopen(query_url).read()
            service_log.debug_log('Getting server response:'+return_content)
            return_dict = json.loads(return_content)
            return_status = return_dict['status']
            if not return_status:
                # service_log.error_log('Aminer server error:' + return_dict['message'])
                return []
            self.task_person_list = [Person(person_dict) for person_dict in return_dict['tasks']]
            service_log.success_log('Get task_person_list')

    def recommend_and_submit(self):
        name_email_dict = {}
        post_body = {
            'token': 'iamkegger',
            'results': []
        }
        for person in self.task_person_list:
            person.get_recommend_email()
            DB_ID_PERSON_JSON.Put(str(person.id), person.to_json())
            person_result = {
                'i': person.id,
                'e': person.recommend_email
            }
            post_body['results'].append(person_result)
            name_email_dict[person.name] = person.recommend_email
            # with open('../resource/test/' + person.name + '.json', 'w') as f:
            #     f.write(person.to_json())

        headers = {"Content-type": "application/json"}
        import requests
        r = requests.post(self.post_url, data=json.dumps(post_body), headers=headers)
        service_log.debug_log(json.dumps(r.content))
        service_log.debug_log(json.dumps(name_email_dict, indent=4))


class ServiceProvider:

    def __init__(self):
        self.list_len = 20

    def run_service(self):
        while True:
            try:
                service = AminerEmailService()
                service.get_task_person_list(self.list_len)
                if not service.task_person_list:
                    time.sleep(G_SLEEP_SECONDS)
                    continue
                service.recommend_and_submit()
            except KeyboardInterrupt:
                service_log.debug_log('Service killed, see you next time !')
                break
            except Exception as e:
                service_log.error_log(str(e))
                time.sleep(G_SLEEP_SECONDS)
                continue


def run_email_service():
    service_provider = ServiceProvider()
    service_provider.run_service()


if __name__ == '__main__':
    run_email_service()