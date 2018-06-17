from njupt.utils.aolan.aolan_captcha import AolanCaptcha
from njupt.utils.card.card_captcha import CardCaptcha
from njupt.utils.zhengfang.zhengfang_captcha import ZhengfangCaptcha


def zhengfang_table_to_list(trs, remove_index_list=None, index_cast_dict=None):
    """
    将正方中经常出现的table转换python中的list
    :param trs: bs4选中的所有的tr
    :param remove_index_list: 需要剔除的列的下标
    :param index_cast_dict: 类型转换函数集， dict， key为列的下标，value为对该值的cast函数
    :rtype list
    :return: 列表元素为表格每行信息的dict
    """
    index_cast_dict = index_cast_dict or {}
    trs = list(trs)
    keys = [key.text.strip() for col_index, key in enumerate(trs[0].select('td')) if col_index not in remove_index_list]
    result = []
    for tr in trs[1:]:
        values = []
        for col_index, td in enumerate(tr.select('td')):
            value = td.text.strip()
            if col_index in remove_index_list:
                continue
            if col_index in index_cast_dict:
                value = index_cast_dict[col_index](value)
            values.append(value)
        recode = dict(zip(keys, values))
        result.append(recode)
    return result
