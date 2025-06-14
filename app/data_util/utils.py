# !/usr/bin/python
# -*- coding: utf-8 -*-
import pyrouge


def print_results(article, abstract, decoded_output):
    print("")
    print('ARTICLE:  %s', article)
    print('REFERENCE SUMMARY: %s', abstract)
    print('GENERATED SUMMARY: %s', decoded_output)
    print("")


def calc_running_avg_loss(loss, running_avg_loss, step, decay=0.99):
    if running_avg_loss == 0:  # on the first iteration just take the loss
        running_avg_loss = loss
    else:
        running_avg_loss = running_avg_loss * decay + (1 - decay) * loss
    running_avg_loss = min(running_avg_loss, 12)  # clip
    # print("writing to summary step: ", step)
    return running_avg_loss


def print_config(conf, path):
    path = os.path.join(path, "config.txt")
    with open(path, "w") as f:
        f.write('\n'.join(['%s:%s' % item for item in conf.__dict__.items()]))
    print("writing config to dir " + path + " done!")


def write_eval_results(decode_path, eval_result, prefix=""):
    count = 0
    file_path = os.path.join(decode_path, f"{prefix}ROUGE-RESULT.txt")
    with open(file_path, "w") as f:
        for key, value in eval_result.items():
            count += 1
            f.write(key + ": " + str(value) + " ")
            if count % 3 == 0:
                f.write("\n")
    print("writing eval result done!")


import re
import os
import shutil
import datetime
import sys

sys.setrecursionlimit(10000)

REMAP = {"-lrb-": "(", "-rrb-": ")", "-lcb-": "{", "-rcb-": "}",
         "-lsb-": "[", "-rsb-": "]", "``": '"', "''": '"'}


def clean(x):
    return re.sub(r"-lrb-|-rrb-|-lcb-|-rcb-|-lsb-|-rsb-|``|''", lambda m: REMAP.get(m.group()), x)


def pyrouge_score_all(hyps_list, refer_list, config, remap=True):
    nowTime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    print("[DEBUG] config.log_root =", config.log_root)
    BASE = os.getcwd()               
    BASE_PATH = os.path.join(BASE, "pyrouge_root")
    PYROUGE_ROOT = os.path.join(BASE_PATH, nowTime)
    print(f"[DEBUG] cwd={BASE}")
    print(f"[DEBUG] will create BASE_PATH={BASE_PATH}")
    print(f"[DEBUG] will create PYROUGE_ROOT={PYROUGE_ROOT}")

    try:
        os.mkdir(PYROUGE_ROOT)
        print(f"[DEBUG] created {PYROUGE_ROOT}")
    except Exception as e:
        print(f"[DEBUG] error creating {PYROUGE_ROOT}: {e}")

    SYSTEM_PATH = os.path.join(PYROUGE_ROOT, 'gold')
    MODEL_PATH = os.path.join(PYROUGE_ROOT, 'system')
    if os.path.exists(SYSTEM_PATH):
        shutil.rmtree(SYSTEM_PATH)
    os.makedirs(SYSTEM_PATH)
    if os.path.exists(MODEL_PATH):
        shutil.rmtree(MODEL_PATH)
    os.makedirs(MODEL_PATH)

    assert len(hyps_list) == len(refer_list)
    gold_path = os.path.join(config.decode_path, f"gold.txt")
    pred_path = os.path.join(config.decode_path, f"pred.txt")

    for i in range(len(hyps_list)):
        system_file = os.path.join(SYSTEM_PATH, 'Reference.%d.txt' % i)
        model_file = os.path.join(MODEL_PATH, 'Model.A.%d.txt' % i)

        refer = clean(refer_list[i]) if remap else refer_list[i]
        hyps = clean(hyps_list[i]) if remap else hyps_list[i]

        with open(system_file, 'wb') as f:
            f.write(refer.encode('utf-8'))
        with open(model_file, 'wb') as f:
            f.write(hyps.encode('utf-8'))

        with open(gold_path, 'a') as f:
            f.write(refer.replace("\n", " "))
            f.write("\n")
        with open(pred_path, 'a') as f:
            f.write(hyps.replace("\n", " "))
            f.write("\n")

    r = pyrouge.Rouge155()
    r.system_dir = SYSTEM_PATH
    r.model_dir = MODEL_PATH
    r.system_filename_pattern = 'Reference.(\d+).txt'
    r.model_filename_pattern = 'Model.[A-Z].#ID#.txt'
    ###### change this line to your pyrouge dir ######
    output = r.convert_and_evaluate(rouge_args="-e /home/bruce.kim/searchforest-ai/app/tools/ROUGE-1.5.5/data -a -m -n 2 -d")

    output_dict = r.output_to_dict(output)

    shutil.rmtree(PYROUGE_ROOT)

    scores = {}
    scores['rouge_1_precision'], scores['rouge_1_recall'], scores['rouge_1_f_score'] = output_dict['rouge_1_precision'], \
                                                                                       output_dict['rouge_1_recall'], \
                                                                                       output_dict[
                                                                                           'rouge_1_f_score']
    scores['rouge_2_precision'], scores['rouge_2_recall'], scores['rouge_2_f_score'] = output_dict['rouge_2_precision'], \
                                                                                       output_dict['rouge_2_recall'], \
                                                                                       output_dict[
                                                                                           'rouge_2_f_score']
    scores['rouge_l_precision'], scores['rouge_l_recall'], scores['rouge_l_f_score'] = output_dict['rouge_l_precision'], \
                                                                                       output_dict['rouge_l_recall'], \
                                                                                       output_dict[
                                                                                           'rouge_l_f_score']
    return scores


def pyrouge_score_all_multi(hyps_list, refer_list, config, remap=True):
    nowTime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    PYROUGE_ROOT = os.path.join(config.test_result_path, nowTime)
    SYSTEM_PATH = os.path.join(PYROUGE_ROOT, 'system')
    MODEL_PATH = os.path.join(PYROUGE_ROOT, 'gold')
    if os.path.exists(SYSTEM_PATH):
        shutil.rmtree(SYSTEM_PATH)
    os.makedirs(SYSTEM_PATH)
    if os.path.exists(MODEL_PATH):
        shutil.rmtree(MODEL_PATH)
    os.makedirs(MODEL_PATH)

    assert len(hyps_list) == len(refer_list)

    pred_path = os.path.join(config.decode_path, "pred.txt")

    for i in range(len(hyps_list)):
        system_file = os.path.join(SYSTEM_PATH, 'Model.%d.txt' % i)
        # model_file = os.path.join(MODEL_PATH, 'Reference.A.%d.txt' % i)

        hyps = clean(hyps_list[i]) if remap else hyps_list[i]

        with open(system_file, 'wb') as f:
            f.write(hyps.encode('utf-8'))

        referType = ["A", "B", "C", "D", "E", "F", "G"]

        for j in range(len(refer_list[i])):
            model_file = os.path.join(MODEL_PATH, "Reference.%s.%d.txt" % (referType[j], i))
            refer = clean(refer_list[i][j]) if remap else refer_list[i][j]
            with open(model_file, 'wb') as f:
                f.write(refer.encode('utf-8'))

            gold_path = os.path.join(config.decode_path, "gold.%s.txt" % (referType[j]))
            with open(gold_path, 'a') as f:
                f.write(refer)
                f.write("\n")

        with open(pred_path, 'a') as f:
            f.write(hyps)
            f.write("\n")

    r = pyrouge.Rouge155()
    r.system_dir = SYSTEM_PATH
    r.model_dir = MODEL_PATH
    r.system_filename_pattern = 'Model.(\d+).txt'
    r.model_filename_pattern = 'Reference.[A-Z].#ID#.txt'

    output = r.convert_and_evaluate()
    output_dict = r.output_to_dict(output)

    shutil.rmtree(PYROUGE_ROOT)

    scores = {}
    scores["rouge_1_precision"], scores['rouge_1_recall'], scores['rouge_1_f_score'] = output_dict['rouge_1_precision'], \
                                                                                       output_dict['rouge_1_recall'], \
                                                                                       output_dict[
                                                                                           'rouge_1_f_score']
    scores['rouge_2_precision'], scores['rouge_2_recall'], scores['rouge_2_f_score'] = output_dict['rouge_2_precision'], \
                                                                                       output_dict['rouge_2_recall'], \
                                                                                       output_dict[
                                                                                           'rouge_2_f_score']
    scores['rouge_l_precision'], scores['rouge_l_recall'], scores['rouge_l_f_score'] = output_dict['rouge_l_precision'], \
                                                                                       output_dict['rouge_l_recall'], \
                                                                                       output_dict[
                                                                                           'rouge_l_f_score']
    return scores
