def test_get_score(zhengfang):
    score = zhengfang.get_score()
    assert 0 < score['gpa'] < 5

def test_get_schedule(zhengfang):
    assert zhengfang.get_schedule(1) is not None

def test_get_courses(zhengfang):
    assert zhengfang.get_courses() is not None
