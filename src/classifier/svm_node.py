import re
import os
import sys
from util import prefix_is_invalid_keyword
reload(sys)
sys.setdefaultencoding('utf8')


class SvmNode:

    def __init__(self, google_item_dict, aff_word_list, all_emails):
        self.addr_repeat_time = 0
        self.aff_word_list = aff_word_list
        self.all_emails = all_emails
        self.item_dict = google_item_dict
        self.email = str(google_item_dict['email_addr']).lower()
        self.person_name = str(google_item_dict['person_name']).lower().replace('.', '')
        self.google_title = str(google_item_dict['title']).lower().replace('.', '')
        self.google_content = str(google_item_dict['content']).lower().replace('.', '')
        self.cite_url = str(google_item_dict['cite_url']).lower()

        self.last_name = self.person_name.replace('-', ' ').split(' ')[-1]
        self.first_name = self.person_name.replace('-', ' ').split(' ')[0]
        self.first_char_list = [name[0] for name in self.person_name.replace('-', '').split(' ')]

        self.domain = self.email[self.email.find('@')+1:]
        self.prefix = self.email[:self.email.find('@')]
        self.prefix = re.sub(r'([\d]+)', '', self.prefix)

    def google_title_contain_aff_word(self):
        contain_aff_word = False
        for aff_word in self.aff_word_list:
            aff_word = aff_word.lower()
            if aff_word in self.google_title.split(' ') or aff_word in self.domain or aff_word in self.cite_url:
                contain_aff_word = True
                break
        return contain_aff_word

    def google_content_contain_aff_word(self):
        contain_aff_word = False
        for aff_word in self.aff_word_list:
            if aff_word in self.google_content.split(' '):
                contain_aff_word = True
                break
        return contain_aff_word

    def prefix_contain_last_name(self):
        is_contain_last_name = self.last_name in self.prefix
        return is_contain_last_name

    def prefix_contain_first_name(self):
        is_contain_first_name = self.first_name in self.prefix and len(self.first_name) > 2
        return is_contain_first_name

    def prefix_is_invalid_keyword(self):
        return prefix_is_invalid_keyword(self.prefix)

    def google_title_contain_last_name(self):
        is_contain_last_name = self.last_name in self.google_title
        return is_contain_last_name

    def google_title_contain_first_name(self):
        is_contain_first_name = self.first_name in self.google_title
        return is_contain_first_name

    def google_content_contain_last_name(self):
        is_contain_last_name = self.last_name in self.google_content
        return is_contain_last_name

    def google_content_contain_first_name(self):
        is_contain_first_name = self.last_name in self.google_content
        return is_contain_first_name

    def prefix_contained_in_last_name(self):
        is_contained_in_last_name = self.prefix in self.last_name
        return is_contained_in_last_name

    def prefix_contained_in_first_name(self):
        is_contained_in_first_name = self.prefix in self.first_name
        return is_contained_in_first_name

    def prefix_contain_all_first_char(self):
        all_char = ''
        for name_part in self.person_name.split(' '):
            all_char += name_part[0]
        is_contain_all_first_char = False
        if all_char in self.prefix:
            is_contain_all_first_char = float(len(all_char)) >= float(len(self.prefix)) * 0.75
        return is_contain_all_first_char

    def prefix_contained_in_name_part_with_first_char(self):
        first_name_with_first_char = self.last_name[0] + self.first_name
        last_name_with_first_char = self.first_name[0] + self.last_name

        last_name_with_all_first_char = ''
        for name_part in self.person_name.split(' ')[:-1]:
            last_name_with_all_first_char += name_part[0]
        last_name_with_all_first_char += self.last_name

        is_prefix_contained = self.prefix in first_name_with_first_char or self.prefix in last_name_with_first_char or self.prefix in last_name_with_all_first_char
        return is_prefix_contained

    def google_title_contain_name(self):
        is_contain_name = self.person_name in self.google_title
        return is_contain_name

    def google_content_contain_name(self):
        is_contain_name = self.person_name in self.google_content
        return is_contain_name

    def domain_contain_aff_word(self):
        is_domain_contain_aff_word = False
        for aff_word in self.aff_word_list:
            if aff_word.lower() in self.domain:
                is_domain_contain_aff_word = True
                break
        return is_domain_contain_aff_word

    def cite_url_contain_aff_word(self):
        is_contain_aff_word = False
        for aff_word in self.aff_word_list:
            if aff_word.lower() in self.cite_url:
                is_contain_aff_word = True
                break
        return is_contain_aff_word

    def same_domain_with_invalid(self):
        for mail in self.all_emails:
            mail = mail.lower()
            if mail == self.email:
                continue
            prefix = mail[:mail.find('@')]
            domain = mail[mail.find('@')+1:]
            if domain == self.domain and prefix_is_invalid_keyword(prefix) and not prefix_is_invalid_keyword(self.prefix):
                return True
        return False

    def get_svm_feature_line(self):
        feature_list = [
            self.prefix_contain_last_name(),
            self.prefix_contain_first_name(),

            self.prefix_contained_in_last_name(),
            self.prefix_contained_in_first_name(),

            self.google_title_contain_last_name(),
            self.google_title_contain_first_name(),

            self.google_content_contain_last_name(),
            self.google_content_contain_first_name(),

            self.google_title_contain_name(),
            self.google_content_contain_name(),

            self.prefix_contain_all_first_char(),
            self.prefix_contained_in_name_part_with_first_char(),

            self.google_title_contain_aff_word(),
            self.google_content_contain_aff_word(),

            self.prefix_is_invalid_keyword(),
            self.domain_contain_aff_word(),
            self.same_domain_with_invalid()
            # self.cite_url_contain_aff_word()
        ]

        feature_line = '1 '
        for looper in range(len(feature_list)):
            feature_id = str(looper + 1)
            feature_line += feature_id + ':' + str(int(feature_list[looper])) + ' '
        feature_line += '#' + self.person_name + '[' + self.email + ']' + '\n'
        return feature_line