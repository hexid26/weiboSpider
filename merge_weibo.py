#!/usr/bin/env python
# coding:utf-8
"""merge_weibo.py"""

import argparse
import logging
import json, xlwt, xlrd
import glob
import re
import datetime
# def set_argparse():
#   """Set the args&argv for command line mode"""
#   parser = argparse.ArgumentParser()
#   parser.add_argument("file", type=str, default="", help="input data file")
#   return parser.parse_args()

mode_keys = [["新增", "累计", "确诊", "肺炎", "冠状病毒", "疫情"]]


def get_logger(logname):
  """Config the logger in the module
  Arguments:
      logname {str} -- logger name
  Returns:
      logging.Logger -- the logger object
  """
  logger = logging.getLogger(logname)
  formater = logging.Formatter(
      fmt='%(asctime)s - %(filename)s : %(levelname)-5s :: %(message)s',
      # filename='./log.log',
      # filemode='a',
      datefmt='%m/%d/%Y %H:%M:%S')
  stream_hdlr = logging.StreamHandler()
  stream_hdlr.setFormatter(formater)
  logger.addHandler(stream_hdlr)
  logger.setLevel(logging.DEBUG)
  return logger


# ! mode 0 肺炎 冠状病毒 疫情
# ! mode 1 新增 累计 确诊 肺炎 冠状病毒 疫情
def gen_score(content, score_mode):
  score = []
  global mode_keys
  # * 只跑一种打分
  # for keys in mode_keys:
  #   tmp_sorce = 0
  #   for key in keys:
  #     if key in content:
  #       tmp_sorce += 1
  #   score.append(tmp_sorce)
  # * 跑所有打分
  for keys in mode_keys:
    tmp_sorce = 0
    for key in keys:
      if key in content:
        tmp_sorce += 1
    score.append(tmp_sorce)
  return score


def filter_weibo(content, score_mode):
  score = 0
  tmp_title = ""
  title_pattern_1 = re.compile(r'【(.*?)】')
  title_pattern_2 = re.compile(r'#(.*?)#')
  tmp_title = title_pattern_1.findall(content)
  if (len(tmp_title) == 0):
    tmp_title = title_pattern_2.findall(content)
    if len(tmp_title) == 0:
      score = gen_score(content, 0)
      return ["", score]
    else:
      tmp_title = tmp_title[0]
  else:
    tmp_title = tmp_title[0]
  # ! score 打分
  score = gen_score(content, 0)
  return [tmp_title, score]


def read_json_file(file_name):
  temp_weibo_list = []
  with open(file_name, 'r') as json_file:
    json_data = json.load(json_file)
  user_id = json_data["user"]["id"]
  who = json_data["user"]["nickname"]
  for weibo_item in json_data["weibo"]:
    # ! 这里可以加 filter
    item = {}
    res = filter_weibo(weibo_item["content"], 0)
    item["title"] = res[0]
    item["score"] = res[1]
    item["id"] = weibo_item["id"]
    item["user_id"] = user_id
    item["who"] = who
    item["time"] = weibo_item["publish_time"]
    item["body"] = weibo_item["content"]
    item["url"] = "https://weibo.com/" + user_id + "/" + weibo_item["id"]
    item["type"] = "weibo"
    temp_weibo_list.append(item)
  return temp_weibo_list


def load_json_file(file_name):
  json_data = ""
  with open(file_name, 'r') as json_file:
    json_data = json.load(json_file)
  return json_data


def sort_json(key_name, json_object, re_flag):
  json_object.sort(key=lambda k: (k.get(key_name, 0)), reverse=re_flag)


def sort_json_by_score(json_object, score_mode, re_flag):
  json_object.sort(key=lambda k: k["score"][score_mode], reverse=re_flag)


def save_json(file_path, json_object):
  with open(file_path, "w") as json_file:
    json.dump(json_object, json_file, ensure_ascii=False)
  json_file.close()


def load_files_to_json(file_path):
  if file_path == "":
    json_data = []
    for json_file in glob.glob("weibo/*/*.json"):
      json_data += read_json_file(json_file)
    sort_json("time", json_data, True)
    return json_data
  else:
    json_data = read_json_file(file_path)
    sort_json("time", json_data, True)
    return json_data


def save_json_to_xlsx_file(json_object, file_path, score_mode):
  global mode_keys
  workbook = xlwt.Workbook(encoding='utf-8')
  sheet = workbook.add_sheet('-'.join(mode_keys[score_mode]), cell_overwrite_ok=True)
  row = 0
  for item in json_object:
    sheet.write(row, 0, str(item["score"][score_mode]))
    sheet.write(row, 1, item["who"])
    sheet.write(row, 2, item["title"])
    sheet.write(row, 3, item["body"])
    sheet.write(row, 4, item["time"])
    sheet.write(row, 5, item["id"])
    sheet.write(row, 6, item["user_id"])
    sheet.write(row, 7, item["url"])
    sheet.write(row, 8, item["type"])
    row += 1
  workbook.save(file_path)
  return


def save_json_to_xlsx_file_all_mode(json_object, file_path):
  global mode_keys
  workbook = xlwt.Workbook(encoding='utf-8')
  sheet = workbook.add_sheet("all mode", cell_overwrite_ok=True)
  row = 0
  for item in json_object:
    col = 0
    for score_mode in range(0, len(mode_keys)):
      sheet.write(row, col, str(item["score"][score_mode]))
      col += 1
    sheet.write(row, col + 0, item["who"])
    sheet.write(row, col + 1, item["title"])
    sheet.write(row, col + 2, item["body"])
    sheet.write(row, col + 3, item["time"])
    sheet.write(row, col + 4, item["id"])
    sheet.write(row, col + 5, item["user_id"])
    sheet.write(row, col + 6, item["url"])
    sheet.write(row, col + 7, item["type"])
    row += 1
  workbook.save(file_path)
  return


# ! 得分 < min 的剔除
def exclude_by_score(min, score_mode, json_data):
  tmp_json = list(filter(lambda x: x["score"][score_mode] >= min, json_data))
  return tmp_json


def redundancy(json_data):
  pass


def test_time():
  cur_time = datetime.datetime.now()
  delta = datetime.timedelta(minutes=30)
  start_time = cur_time - delta
  start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
  __logger__.debug(start_time)
  exit()


def main():
  """Main function"""
  # __logger__.info('Process start!')
  json_data = load_files_to_json("")
  json_data = exclude_by_score(6, 0, json_data)
  existed_data = load_json_file("Archive.json")
  existed_data = existed_data + json_data
  # sort_json_by_score(existed_data, 0, True)
  # save_json_to_xlsx_file(json_data, "Mode0.xls", 0)
  save_json_to_xlsx_file_all_mode(existed_data, "Mode.xls")
  sort_json("time", existed_data, True)
  save_json("Archive.json", existed_data)
  # __logger__.debug(json.dumps(json_data, ensure_ascii=False))
  # __logger__.info('Process end!')


if __name__ == '__main__':
  # ! Uncomment the next line to read args from cmd-line
  __logger__ = get_logger('merge_weibo.py')
  main()
