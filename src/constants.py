import leveldb
from os.path import join
from util import create_dir_if_not_exist


# log
LOG_DIR = join('..', 'log')
DEFAULT_LOG_PATH = join(LOG_DIR, 'log.txt')
create_dir_if_not_exist(LOG_DIR)

# leveldb
DB_DIR = join('..', 'leveldb')
DB_PATH_ID_PERSON_JSON = join(DB_DIR, 'id_person_json')
DB_ID_PERSON_JSON = leveldb.LevelDB(DB_PATH_ID_PERSON_JSON)

