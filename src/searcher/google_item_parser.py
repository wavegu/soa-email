# encoding: utf-8


import re
import os
import json
from HTMLParser import HTMLParser

import sys

reload(sys)
sys.setdefaultencoding('utf8')


class GoogleItem:

    def __init__(self):
        self.title = ''
        self.content = ''
        self.cite_url = ''
        self.cite_name = ''
        self.email_list = []

    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'cite_url': self.cite_url,
            'cite_name': self.cite_name,
            'email_addr_list': self.email_list
        }


class GoogleItemParser(HTMLParser):
    """
    search for e-mail address from search page
    """

    def __init__(self, input_google_pages_path, output_google_items_path):
        HTMLParser.__init__(self)
        self.tem_googleItem = GoogleItem()
        self.is_in_title = False
        self.is_in_content = False
        self.is_in_cite_url = False
        self.is_in_cite_name = False
        self.google_item_list = []
        self.content_span_num = 0
        self.input_google_pages_path = input_google_pages_path
        self.output_google_items_path = output_google_items_path

    def handle_starttag(self, tag, attrs):
        if tag == 'span':
            for (variable, value) in attrs:
                if variable == "class" and value == "st":
                    self.is_in_content = True
                    break
            if self.is_in_content:
                self.content_span_num += 1

        elif tag == 'div':
            for (variable, value) in attrs:
                if variable == "class" and value == "rc":
                    self.is_in_title = True
                    self.tem_googleItem = GoogleItem()
                    break
                if variable == 'class' and value == 'crl':
                    self.is_in_cite_name = True
                    break

        elif tag == 'cite':
            for (variable, value) in attrs:
                if variable == 'class' and value == '_Rm':
                    self.is_in_cite_url = True
                    break

    def handle_endtag(self, tag):
        if self.is_in_title and tag == 'a':
            self.is_in_title = False
            return

        if self.is_in_cite_url and tag == 'cite':
            self.is_in_cite_url = False
            return

        if self.is_in_cite_name and tag == 'div':
            self.is_in_cite_name = False
            return

        if self.is_in_content and tag == 'span':
            self.content_span_num -= 1
            if self.content_span_num > 0:
                return
            self.is_in_content = False
            if self.tem_googleItem.content == '':
                return
            try:
                self.tem_googleItem.content = str(self.tem_googleItem.content).lower()
            except Exception as e:
                print e
                print self.tem_googleItem.content
                return []

            # if self.tem_googleItem.content.find('@') < 0 and self.tem_googleItem.content.find(' at ') < 0 and self.tem_googleItem.content.find('[at]') < 0:
            #     return []

            rough_pattern = re.compile('[a-z0-9-\._]+(@| at | \[at\] |\[at\])(([a-z0-9\-]+)(\.| dot | \. | \[dot\] ))+([a-z]+)')
            rough_match = rough_pattern.finditer(self.tem_googleItem.content)
            for rm in rough_match:
                pattern = re.compile('(([a-z0-9-_]+)(\.| dot | \. )?)+(@| at | \[at\] |\[at\])(([a-z0-9\-]+)(\.| dot | \.  \[dot\] ))+([a-z]+)')
                match = pattern.finditer(rm.group())
                for m in match:
                    self.tem_googleItem.email_list.append(m.group().replace(' dot ', '.').replace(' at ', '@').replace('[at]', '@').replace(' ', ''))

            if self.tem_googleItem.email_list:
                self.google_item_list.append(self.tem_googleItem)

    def handle_data(self, data):
        if self.is_in_title:
            self.tem_googleItem.title += data
        if self.is_in_cite_url:
            self.tem_googleItem.cite_url += data
        if self.is_in_cite_name:
            self.tem_googleItem.cite_name += data
        if self.is_in_content:
            self.tem_googleItem.content += data

    def parse_google_items_from_google_pages(self):
        import codecs
        if not os.path.isdir(self.output_google_items_path):
            os.mkdir(self.output_google_items_path)
        counter = 0
        for person in os.listdir(self.input_google_pages_path):
            google_item_file_path = self.output_google_items_path + person + '.json'
            if person + '.json' in os.listdir(self.output_google_items_path):
                continue
            if not os.path.isdir(self.input_google_pages_path + person):
                continue
            counter += 1
            print 'parsing item: [%d] %s\n' % (counter, person)
            google_page_file_path = os.listdir(self.input_google_pages_path + person)[0]
            for filename in os.listdir(self.input_google_pages_path + person):
                if '.html' in filename and '~' not in filename:
                    google_page_file_path = self.input_google_pages_path + person + '/' + filename
                    break
            google_page_content = open(google_page_file_path).read()

            self.feed(google_page_content)
            google_item_dict_list = [google_item.to_dict() for google_item in self.google_item_list]
            with codecs.open(google_item_file_path, "w", encoding="utf-8") as f_out:
                json.dump(google_item_dict_list, f_out, indent=4, ensure_ascii=False)
            self.google_item_list = []


# if __name__ == '__main__':
    # parser = GoogleSearchPageMailParser()
    # parser.handle_data(data)
    # print parser.emails
    # parse_mails_from_search_page('google')