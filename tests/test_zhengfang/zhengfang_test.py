from datetime import datetime

import responses

from tests.conftest import mock_response


@mock_response(file_name='htmls/zhengfang/list_optional_courses.html')
@responses.activate
def test_list_optional_courses(zhengfang):
    optional_courses = zhengfang.list_optional_courses()
    assert len(optional_courses) == 2
    assert optional_courses[0]['学分'] == 2
    assert optional_courses[1]['余量'] == 150


@mock_response(file_name='htmls/zhengfang/get_grades.html')
@responses.activate
def test_list_exam_grades(zhengfang):
    grades = zhengfang.list_exam_grades()
    assert len(grades) == 6
    assert grades[0]['考试日期'] == datetime(2015, 12, 19)
    assert grades[0]['学期'] == 1


@mock_response(method='POST', file_name='htmls/zhengfang/scores.html')
@mock_response(method='GET', file_name='htmls/zhengfang/scores.html')
@responses.activate
def test_get_gpa(zhengfang):
    gpa = zhengfang.get_gpa()
    assert gpa == 3.52


@mock_response(method='POST', file_name='htmls/zhengfang/scores.html')
@mock_response(method='GET', file_name='htmls/zhengfang/scores.html')
@responses.activate
def test_list_exam_scores(zhengfang):
    exam_scores = zhengfang.list_exam_scores()
    assert exam_scores[0]['学分'] == 2.0
    assert exam_scores[0]['成绩'] == 81
    assert not exam_scores[0]['绩点']
    assert exam_scores[8]['成绩'] == "优秀"
