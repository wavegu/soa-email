import json
import re
import string

__author__ = 'hong'


class AffWordsExtractor:

    def __init__(self, stop_words_file_path):
        self.stop_words = [line.replace('\n', '') for line in open(stop_words_file_path).readlines()]

    def get_aff_words_list(self, aff):

        is_eng = False
        for ch in aff:
            if ch.isalpha():
                is_eng = True
                break

        if not is_eng:
            return []

        aff = aff.replace('\n', ' ').lower()
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
        return list(aff_word_set)
