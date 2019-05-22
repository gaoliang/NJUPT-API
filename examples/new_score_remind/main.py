import json
import os

import requests
import toml

from njupt import SSO

root = os.path.dirname(os.path.abspath(__file__))

message_title_template = '{}出成绩了'
message_desp_template = "# {} 成绩：{}"


def remind(course_name, score, token):
    requests.post("https://sc.ftqq.com/{}.send".format(token),
                  data={
                      'text': message_title_template.format(course_name),
                      'desp': message_desp_template.format(course_name, score)
                  })


with open(os.path.join(root, 'accounts.toml')) as fp:
    accounts = toml.load(fp)['accounts']
    for account in accounts:
        zf = SSO(username=account['username'], password=account['password']).zhengfang()
        scores = zf.list_exam_scores()
        score_dict = {score['课程代码']: score for score in scores}
        score_dict_path = os.path.join(root, '{}_scores.json'.format(account['username']))
        if not os.path.exists(score_dict_path):
            with open(score_dict_path, 'w', encoding='utf-8') as score_file:
                json.dump(score_dict, score_file)
        else:
            with open(score_dict_path, 'r+', encoding='utf-8') as score_file:
                old_score_dict = json.load(score_file)
                for score_code, score in score_dict.items():
                    if score_code not in old_score_dict:
                        remind(course_name=score['课程名称'],
                               score=score['成绩'],
                               token=account['ftqq_token']
                               )
            with open(score_dict_path, 'w', encoding='utf-8') as score_file:
                json.dump(score_dict, score_file)
