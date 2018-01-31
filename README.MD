
# NJUPT-API 简介

NJUPT-API 的初衷是希望为NJUPT的各个系统提供一套跨系统的简洁、优雅的、Pythonic的API接口，以便用户能够在此基础上进行扩展开发。

项目结构受到了开源项目 [zhihu-api](https://github.com/lzjun567/zhihu-api)的启发，在这里对作者[@lzjun567](https://github.com/lzjun567/)表示感谢

欢迎pr

# 目前实现的功能
## 正方系统

### 登录
```python
from njupt import Zhengfang
zhengfang = Zhengfang()
>> zhengfang.login(account='B1xxxxxxx',password='password')
    {
        'success':True,
        'code':0,
        'msg':'登录成功'
    }
# or zhengfang = Zhengfang('B1xxxxxxx','password')

```
### 获取课程成绩和绩点
```python
>>> zhengfang.get_score() 
    {'gpa': 4.99,
    'coursers': [{
        'year': '2015-2016', # 学年
        'semester': '1', # 学期
        'code': '00wk00003', # 课程代码
        'name': '从"愚昧"到"科学"-科学技术简史', # 课程名称
        'attribute': '任选', # 课程性质
        'belong': '全校任选课', # 课程归属
        'credit': '2.0', # 学分
        'point': '', # 绩点
        'score': '81', # 成绩
        'minor_mark': '0', # 辅修标记
        'make_up_score': '', # 辅修标记
        'retake_score': '', # 重修成绩 
        'college': '网络课程', # 开课学院
        'note': '', # 备注 
        'retake_mark': '0', # 重修标记
        'english_name': '' # 英文名称
        }, 
        ]
    }
```

### 获取等级考试信息
```python
>>> zhengfang.get_grade() 
    [
        {
        'date': '20151219',
         'name': '全国大学英语四级考试',
         'number': '320082152113313',
         'score': '547',
         'semester': '1',
         'year': '2015-2016'
        },
        ...
    ]
```
### 获取课表
```python
>>> zhengfang.get_schedule(week=1)
    # 二维列表，[i][j] 代表周i第j节课的课程。 为了方便，i或j为零0的单元均不使用。
    # 课程的节次使用一天12节课的形式描述。
    # 课程信息使用dict进行描述。
    # 一个参考的结构如下
    [
        [],
        [   None,
            {
            'classroom': '教4－202', 
            'name': '技术经济学', 
            'teacher': '储成祥'
            },
            ...
        ],
        ...
    ]



```

## 校园卡系统
### 登录
```python

from njupt import Card
>>> card = Card(account='11020xxxxxxxxxx',password='passwd')
    {
        'success': True,
        'code': 0, 
        'msg': '登录成功'
    }

# or card = Card(), card.login(account,password)
```

### 获取余额
```python
>>> card.get_balance()
    {
        'balance': 10.01,  # 到账余额
        'unsettle_balance': 0.01  # 过渡余额
        'total': 10.02  # 总余额
    }
```
### 充值(绑定银行卡 -> 校园卡)
```python
>>> card.recharge(amount=2.33)
    {   
        'success':True,  # 转账是否成功
        'code': 0,  # 状态码
        'msg': '转账成功'  # 附加信息
    }
```
### 获取账单
```python
>>> card.get_bill(start_date='2017-02-33',end_date='2018-01-03',rows=30,page=1)
    {'recodes': 
        [
            {'balances': 39.71, # 余额
              'change': -5, # 变动
              'comment': '未知系统,交电费', # 注释
              'department': '仙林售电处', # 操作部门
              'time': '2018-01-26 20:55:40', # 时间
              'type': '代扣代缴', # 类型
              'week': '星期五'}, # 星期
            {'balances': 39.71,
              'change': -7.5,
              'comment': '',
              'department': '一餐厅二楼清真食堂',
              'time': '2018-01-24 17:09:36',
              'type': '持卡人消费',
              'week': '星期三'},
               ... 
        ],
    'total': 52, # 总的记录数
    'total_pages':2,  # 总页数
    'page':1  # 当前的页码
    }
```

### 获取Dr.com的网费余额
```python
>>> card.get_net_balance()
    2.33
```

### 充值网费
```python
>>> card.recharge_net(amount=2.33)
    {
        'success': True, 
        'code' : 0,
        'Msg' : '充值成功'
    }
```
### 充值寝室电费
```python
>>> card.recharge_xianlin_elec(amount=2.33,building_name='兰苑11栋',room_id='4031')
    {
        'success': True, 
        'code' : 0,
        'Msg' : '缴费成功！'
    }
    # 三牌楼校区为card.recharge_sanpailou_elec()，参数相同（未测试）
```


# todos

图书馆系统和奥兰系统的常用接口