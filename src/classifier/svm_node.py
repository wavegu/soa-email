import re
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class SvmNode:

    def __init__(self, google_item_dict, aff_word_list):
        self.addr_repeat_time = 0
        self.aff_word_list = aff_word_list
        self.item_dict = google_item_dict
        self.label = True
        self.email = str(google_item_dict['email_addr']).lower()
        self.person_name = str(google_item_dict['person_name']).lower().replace('.', '')
        self.google_title = str(google_item_dict['title']).lower().replace('.', '')
        self.google_content = str(google_item_dict['content']).lower().replace('.', '')
        self.grounding_file_path = os.path.join('..', 'result', self.person_name, 'MLN.db')

        self.last_name = self.person_name.replace('-', ' ').split(' ')[-1]
        self.first_name = self.person_name.replace('-', ' ').split(' ')[0]
        self.first_char_list = [name[0] for name in self.person_name.replace('-', '').split(' ')]

        self.domain = self.email[self.email.find('@')+1:]
        self.prefix = self.email[:self.email.find('@')]
        self.prefix = re.sub(r'([\d]+)', '', self.prefix)

    def google_title_contain_aff_word(self):
        contain_aff_word = False
        for aff_word in self.aff_word_list:
            if aff_word in self.google_title.split(' '):
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
        invalid_keyword_list = ['email', 'info', 'mailto', 'lastname', 'name']
        is_invalid_prefix = False
        for invalid_keyword in invalid_keyword_list:
            if self.prefix == invalid_keyword:
                is_invalid_prefix = True
                break
        return is_invalid_prefix

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

            self.prefix_is_invalid_keyword()
        ]

        feature_line = '1 '
        for looper in range(len(feature_list)):
            feature_id = str(looper + 1)
            feature_line += feature_id + ':' + str(int(feature_list[looper])) + ' '
        feature_line += '#' + self.person_name + '[' + self.email + ']' + '\n'
        return feature_line