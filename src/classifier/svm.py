# encoding: utf-8
import subprocess


class SVM:

    def __init__(self, svm_dir_path):
        self.svm_dir_path = svm_dir_path

    def compare_pred_and_test(self, pred_file_path, test_file_path, output_file_path):
        compare_line_list = []
        with open(pred_file_path) as pred_file:
            pred_lines = pred_file.readlines()
        with open(test_file_path) as test_file:
            test_lines = test_file.readlines()
        if len(pred_lines) != len(test_lines):
            print 'Error: prediction line number doesn\'t match test line number'
            return

        unmatch_num = 0
        miss_positive_num = 0
        mistake_judge_num = 0
        for looper in range(len(pred_lines)):
            pred_line = pred_lines[looper]
            test_line = test_lines[looper]
            if not pred_line:
                continue
            pred_tag = pred_line.split(' ')[0]
            test_tag = test_line.split(' ')[0]
            test_tag = int(test_tag)
            if float(pred_tag) < 0.0:
                pred_tag = -1
            else:
                pred_tag = 1
            if pred_tag == test_tag:
                continue
            else:
                unmatch_num += 1
                mistake_judge_num += int(pred_tag == 1)
                miss_positive_num += int(pred_tag == -1)
                compare_line = '[%d/%d] %s' % (pred_tag, test_tag, test_line[test_line.index('#'):])
                compare_line_list.append(compare_line)
                pass

        compare_line_list = sorted(compare_line_list)
        with open(output_file_path, 'w') as compare_file:
            compare_file.write('Accuracy: %f [%d/%d]\n' % (float(len(pred_lines)-unmatch_num)/float(len(pred_lines)), unmatch_num, len(pred_lines)))
            compare_file.write('误判：%d\n' % mistake_judge_num)
            compare_file.write('漏判：%d\n' % miss_positive_num)
            for compare_line in compare_line_list:
                compare_file.write(compare_line)

    def svm_learn(self, test_start):
        pass

    def svm_test(self, test_file_path, model_file_path, prediction_file_path, test_result_file_path):
        pass

    def get_accuracy_from_result(self, test_file_content):
        pass

    def get_precision_from_result(self, test_file_content):
        pass

    def get_recall_from_result(self, test_file_content):
        pass


class SVMLight(SVM):

    def __init__(self, svm_dir_path):
        SVM.__init__(self, svm_dir_path)

    def get_accuracy_from_result(self, test_file_content):
        end_pos = test_file_content.find('%')
        start_pos = test_file_content.find('Accuracy') + 22
        return float(test_file_content[start_pos: end_pos])

    def get_precision_from_result(self, test_file_content):
        start_pos = test_file_content.find('Precision') + 30
        end_pos = test_file_content.find('%', start_pos)
        return float(test_file_content[start_pos: end_pos])

    def get_recall_from_result(self, test_file_content):
        start_pos = test_file_content.find('Precision') + 37
        end_pos = test_file_content.find('%', start_pos)
        return float(test_file_content[start_pos: end_pos])

    def svm_classify(self, feature_file_path, model_file_path, prediction_file_path):
        cmd = self.svm_dir_path + 'svm_classify ' + feature_file_path + ' ' + model_file_path + ' ' + prediction_file_path + ' > prediction.txt'
        print cmd
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
