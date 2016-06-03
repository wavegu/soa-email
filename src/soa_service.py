import json
import leveldb
from constants import DB_PATH_ID_PERSON_JSON
from person import Person
from flask import request
from service_log import service_log
from src import SERVER_IP, SERVER_PORT, server, g


def request_to_dict(http_request):
    raw_dict = dict(http_request.form)
    new_dict = {}
    for key in raw_dict.keys():
        new_dict[key] = raw_dict[key][0]
    return new_dict


@server.route('/email', methods=['POST'])
def get_emails():

    request_dict = request_to_dict(request)
    print 'request dict = ', request_dict
    try:
        names = request_dict['names'].split(';')
        print names
        task_person_list = [Person({'name': name.strip()}) for name in names if name]
        service_log.success_log('Get task_person_list')

        name_email_dict = {}
        post_body = {
            'results': []
        }
        for person in task_person_list:
            person.get_recommend_email()
            person_result = {
                'name': person.name,
                'email': person.recommend_email
            }
            post_body['results'].append(person_result)
            name_email_dict[person.name] = person.recommend_email

        import json
        service_log.debug_log(json.dumps(name_email_dict, indent=4))
        return json.dumps(post_body)

    except KeyError as k:
        service_log.error_log('Getting emails: request dict not complete')


if __name__ == '__main__':

    server.debug = True
    server.run(host=SERVER_IP, port=SERVER_PORT)