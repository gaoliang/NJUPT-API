"""
方便收集正方验证码的简单打码工具
"""
import tkinter
from io import BytesIO

import requests
from PIL import Image, ImageTk
from bs4 import BeautifulSoup


class CaptchaGUI:
    captcha_url = "http://jwxt.njupt.edu.cn/CheckCode.aspx"
    login_url = "http://jwxt.njupt.edu.cn/default2.aspx"

    def __init__(self):

        self.s = requests.session()
        self.get_viewstate()
        self.r = self.s.get(self.captcha_url)
        self.im = Image.open(BytesIO(self.r.content))

        self.root = tkinter.Tk()
        self.tkimg = ImageTk.PhotoImage(self.im)
        self.imgLabel = tkinter.Label(self.root, image=self.tkimg)
        self.imgLabel.pack()
        self.message = tkinter.Entry(self.root)
        self.message.pack()
        self.root.bind('<Return>', self.judge_and_save)
        self.root.mainloop()

    def get_viewstate(self):
        r = self.s.get(self.login_url)
        soup = BeautifulSoup(r.content, "lxml")
        self.viewstate = soup.find('input', attrs={"name": "__VIEWSTATE"}).get("value")

    def judge_and_save(self, event):
        captcha_value = self.message.get()
        print(captcha_value)
        data = {
            "__VIEWSTATE": self.viewstate,
            'txtUserName': "",  # 账号
            'TextBox2': "",  # 密码
            'RadioButtonList1': "%D1%A7%C9%FA",
            "Button1": "",
            "txtSecretCode": captcha_value,
            "hidPdrs": "",
            "hidsc": ""
        }

        r = self.s.post(self.login_url, data=data)
        if "请到信息维护中完善个人联系方式" in r.text:
            print("成功！")
            with open("captchas/{}.gif".format(captcha_value), 'wb+') as f:
                f.write(self.r.content)
        else:
            print("验证码输错了")
        self.get_viewstate()
        self.r = self.s.get(self.captcha_url)
        self.im = Image.open(BytesIO(self.r.content))
        self.tkimg = ImageTk.PhotoImage(self.im)
        self.imgLabel.config(image=self.tkimg)
        self.message.delete(0, 'end')


if __name__ == "__main__":
    captcha_gui = CaptchaGUI()
