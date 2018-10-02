"""
方便收集南邮一卡通网站验证码的简单打码工具
"""
import base64
import tkinter
from io import BytesIO

import requests
from PIL import Image, ImageTk


class CaptchaGUI:
    BASE_URL = "http://yktapp.njupt.edu.cn:8070"
    CAPTCHA_URL = BASE_URL + "/Login/GetValidateCode"
    LOGIN_URL = BASE_URL + "/Login/LoginBySnoQuery"

    def __init__(self):
        self.pwd = ""  # your njupt card number
        self.account = ""  # your njupt card password
        self.s = requests.session()
        self.r = self.s.get(self.CAPTCHA_URL)
        self.im = Image.open(BytesIO(self.r.content))
        self.root = tkinter.Tk()
        self.tkimg = ImageTk.PhotoImage(self.im)
        self.imgLabel = tkinter.Label(self.root, image=self.tkimg)
        self.imgLabel.pack()
        self.message = tkinter.Entry(self.root)
        self.message.pack()
        self.root.bind('<Return>', self.judge_and_save)
        self.root.mainloop()

    def judge_and_save(self, event):
        captcha_value = self.message.get()
        print(captcha_value)

        data = {
            "sno": self.account,
            "pwd": base64.b64encode(self.pwd.encode("utf8")),
            "ValiCode": captcha_value,
            "remember": 1,
            "uclass": 1,
            "zqcode": "",
            "json": True,
        }

        r = self.s.post(self.LOGIN_URL, data=data)
        if r.json()["IsSucceed"]:
            print("成功！")
            with open("captchas/{}.gif".format(captcha_value), 'wb+') as f:
                f.write(self.r.content)
        else:
            print(r.json())
            print("验证码输错了")
        self.r = self.s.get(self.CAPTCHA_URL)
        self.im = Image.open(BytesIO(self.r.content))
        self.tkimg = ImageTk.PhotoImage(self.im)
        self.imgLabel.config(image=self.tkimg)
        self.message.delete(0, 'end')


if __name__ == "__main__":
    captcha_gui = CaptchaGUI()
