
## NJUPT-API 简介

NJUPT-API 的初衷是希望为NJUPT的各个系统提供一套跨系统的简洁、优雅的、Pythonic的API接口，以便用户能够在此基础上进行扩展开发。

项目结构受到了开源项目 [zhihu-api](https://github.com/lzjun567/zhihu-api)的启发，在这里对作者[@lzjun567](https://github.com/lzjun567/)表示感谢

欢迎pr

## 目前实现的功能
### 正方系统

##### 登录
```python
from njupt import Zhengfang
zhengfang = Zhengfang()

# 验证码自动识别
zhengfang.login('B1xxxxxxx','password')
```
##### 获取课程成绩和绩点
```python
>>> zhengfang.get_score() 
    {'gpa': 4.99,
    'coursers': [{
        'year': '2015-2016',
        'semester': '1',
        'code': '00wk00003',
        'name': '从"愚昧"到"科学"-科学技术简史',
        'attribute': '任选',
        'belong': '全校任选课',
        'credit': '2.0',
        'point': '',
        'score': '81',
        'minorMark': '0',
        'makeUpScore': '',
        'retakeScore': '',
        'college': '网络课程',
        'note': '',
        'retakeMark': '0',
        'englishName': ''
        }, 
        ]
    }
```
### 奥兰系统
#### 登录
```python
from njupt import Aolan
aolan =  Aolan()

# 验证码自动识别
aolan.login('B1xxxxxxx','password')

```

## todos

各种接口。。欢迎pr