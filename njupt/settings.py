# encoding: utf-8

# UserAgent list
user_agent_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
]

USER_AGENT = user_agent_list[0]

HEADERS = {
    'User-Agent': USER_AGENT
}
#
# # 教务系统headers
# JWXT_HEADERS = {
#     "Host": "jwxt.njupt.edu.cn",
#     "Referer": "http://jwc.njupt.edu.cn/",
#     'User-Agent': USER_AGENT
# }

# # COOKIE 存储位置
# COOKIES_FILE = os.path.join(os.path.expanduser('~'), "cookies.txt")
#
# # BASE_DIR, 使用os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
