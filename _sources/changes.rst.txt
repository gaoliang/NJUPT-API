Changelog
====================

Version 0.3.0
--------------

- 支持SSO登录正方 :class:`njupt.SSO` 支持利用my.njupt.edu.cn进行sso登录


Version 0.2.3
--------------

- 早锻炼系统 :class:`njupt.RunningMan` check时返回的打卡记录感知时区(UTC+8)


Version 0.2.2
--------------

- 支持早锻炼系统 :class:`njupt.RunningMan`


Version 0.1.5
--------------

- 支持图书馆 :class:`njupt.Library`
- 验证码识别重构，提高速度，减少依赖
- setup.py 使用 https://github.com/kennethreitz/setup.py 模板
- Pipfile不再指定Python版本