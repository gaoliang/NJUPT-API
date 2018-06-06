def test_get_score(zhengfang):
    assert 'gpa' in zhengfang.get_score()


def test_get_schedule(zhengfang):
    assert zhengfang.get_schedule(1) is not None


def test_get_courses(zhengfang):
    assert zhengfang.get_courses() is not None
