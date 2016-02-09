import os
from classifier.util import create_dir_if_not_exist
from os.path import join

# log
LOG_DIR = join('..', 'log')
DEFAULT_LOG_PATH = join(LOG_DIR, 'log.txt')

# leveldb
DB_DIR = join('..', 'leveldb')
DB_ID_NAME = join(DB_DIR, 'id_name')
DB_ID_ITEM = join(DB_DIR, 'id_item')

create_dir_if_not_exist(LOG_DIR)