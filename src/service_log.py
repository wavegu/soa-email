from datetime import datetime
from constants import DEFAULT_LOG_PATH


class ServiceLog:

    def __init__(self, log_path=DEFAULT_LOG_PATH):
        self.log_path = log_path
        self.log_file = open(self.log_path, 'a')
        self.log_template = '>>> <TIME>\n[<TYPE>] <CONTENT> <SUFFIX>\n'

    def get_log_sentence(self, log_type, content, suffix=''):
        log_sentence = self.log_template.replace('<TIME>', str(datetime.now())).replace('<TYPE>', log_type)\
            .replace('<SUFFIX>', suffix).replace('<CONTENT>', content)
        print log_sentence
        return log_sentence

    def debug_log(self, content):
        self.log_file.write(self.get_log_sentence('DEBUG', content))

    def error_log(self, content):
        self.log_file.write(self.get_log_sentence('ERROR', content))

    def success_log(self, content):
        self.log_file.write(self.get_log_sentence('SUCCESS', content, 'ok...'))

service_log = ServiceLog()