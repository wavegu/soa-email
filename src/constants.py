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
create_dir_if_not_exist(DB_DIR)
DB_ID_PERSON_JSON = leveldb.LevelDB(DB_PATH_ID_PERSON_JSON)

# SVM
SVM_DIR = join('..', 'resource', 'svm')
SVM_FEATURE_FILE_PATH = join(SVM_DIR, 'feature.txt')
SVM_PREDICTION_FILE_PATH = join(SVM_DIR, 'prediction.txt')
SVM_LOG_PATH = join(SVM_DIR, 'svm_log.txt')
SVM_MODEL_PATH = join(SVM_DIR, 'model_with_invalid_domain')
SVM_CLASSIFIER_PATH = join(SVM_DIR, 'svm_classify')
