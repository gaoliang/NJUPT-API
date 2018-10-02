from functools import wraps

from njupt.utils.captchas.zhengfang.zhengfang_captcha import ZhengfangCaptcha  # noqa
from njupt.exceptions import UnauthorizedError


def table_to_list(table, remove_index_list=None, index_cast_dict=None):
    """将html的table转换python中的list

    :type table
    :param table: bs4 选中的table
    :type remove_index_list: list[int] or None
    :param remove_index_list: 需要剔除的列的下标
    :type index_cast_dict: dict[int, function] or None
    :param index_cast_dict: 类型转换函数集， key为列的下标，value为对该值的cast函数
    :rtype list[dict]
    :return: table转换而成的列表， 每个元素为包含所需信息的字典
    """
    index_cast_dict = index_cast_dict or {}
    remove_index_list = remove_index_list or []
    trs = list(table.select('tr'))
    keys = [key.text.strip() for col_index, key in enumerate(trs[0].select('td')) if col_index not in remove_index_list]
    result = []
    for tr in trs[1:]:
        values = []
        for col_index, td in enumerate(tr.select('td')):
            if col_index in remove_index_list:
                continue
            value = td.text.strip()
            if col_index in index_cast_dict:
                value = index_cast_dict[col_index](value)
            values.append(value)
        recode = dict(zip(keys, values))
        result.append(recode)
    return result


def table_to_dict(table, remove_index_list=None, index_cast_dict=None):
    """将html的table转换python中的dict

    :type table
    :param table: bs4 选中的table
    :type remove_index_list: list[int] or None
    :param remove_index_list: 需要剔除的列的下标
    :type index_cast_dict: dict[int, function] or None
    :param index_cast_dict: 类型转换函数集， key为列的下标，value为对该值的cast函数
    :rtype list[dict]
    :return: table转换而成的列表， 每个元素为包含所需信息的字典
    """
    index_cast_dict = index_cast_dict or {}
    remove_index_list = remove_index_list or []
    trs = table.select('tr')
    result = {}
    for row_index, tr in enumerate(trs):
        if row_index in remove_index_list:
            continue
        tds = tr.select('td')
        if len(tds) != 2:
            continue
        key = tds[0].text.strip()
        value = tds[1].text.strip()
        if row_index in index_cast_dict:
            value = index_cast_dict[row_index](value)
        result[key] = value
    return result


def login_required(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.verify:
            return func(self, *args, **kwargs)
        else:
            raise UnauthorizedError('login required!')
    return wrapper
