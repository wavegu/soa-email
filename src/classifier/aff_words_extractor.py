import json
import re
import string

__author__ = 'hong'


class AffWordsExtractor:

    def __init__(self, stop_words_file_path, raw_person_dict_list):
        self.raw_person_dict_list = raw_person_dict_list
        self.stop_words = [line.replace('\n', '') for line in open(stop_words_file_path).readlines()]

    def get_person_dict_with_aff_words_list(self):
        person_dict_with_aff_words_list = []
        for person_dict in self.raw_person_dict_list:
            if 'affiliation' not in person_dict or not person_dict['affiliation']:
                person_dict['affiliation'] = ''
                person_dict['affiliation_words'] = ''
                continue
            aff = person_dict['affiliation']

            aff = aff.replace('\n', ' ')
            # aff = aff.replace('.', ' ').replace(',', ' ').replace('|', ' ')
            # aff = aff.replace('(', ' ').replace(')', ' ')
            regex = re.compile('[%s]' % re.escape(string.punctuation))
            aff = regex.sub(' ', aff)
            aff = re.sub('\s+', ' ', aff).strip(' ')

            aff_words = aff.lower().split(' ', -1)
            aff_word_set = set()
            for word in aff_words:
                if word in self.stop_words:
                    continue
                aff_word_set.add(word)
            person_dict['affiliation_words'] = list(aff_word_set)
            person_dict_with_aff_words_list.append(person_dict)
        return person_dict_with_aff_words_list
