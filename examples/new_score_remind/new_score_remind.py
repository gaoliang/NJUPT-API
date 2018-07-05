import json
import os

from njupt import Zhengfang

root = os.path.dirname(os.path.abspath(__file__))


def email_remind(to_addr, subject, message):
    from email.header import Header
    from email.mime.text import MIMEText
    from email.utils import parseaddr, formataddr

    import smtplib

    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    from_addr = "your sender "
    password = "your sender password"
    smtp_server = "your smtp server"

    msg = MIMEText(message, 'html', 'utf-8')
    msg['From'] = _format_addr('成绩提醒 <%s>' % from_addr)
    msg['To'] = _format_addr('<%s>' % to_addr)
    msg['Subject'] = Header(subject, 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()


msg_template = """
        <!DOCTYPE html>
    <html>
    <body>
    <h3>
        {course_name} 出成绩了！
    </h3>
    
    <h1>分数是: {score}</h1>
    <p>详细信息如下：
        <br>
        {detail}
    </p>
    <h3>你现在的GPA: {gpa}</h3>
    </body>
    </html>
        """

with open(os.path.join(root, 'accounts.json')) as fp:
    accounts = json.load(fp)
    for account in accounts:
        zf = Zhengfang(account['username'], account['password'])
        scores = zf.list_exam_scores()
        score_dict = {score['课程代码']: score for score in scores}

        score_dict_path = os.path.join(root, 'scores', '{}_scores.json'.format(account['username']))
        if not os.path.exists(score_dict_path):
            with open(score_dict_path, 'w', encoding='utf-8') as score_file:
                json.dump(score_dict, score_file)
        else:
            with open(score_dict_path, 'r+', encoding='utf-8') as score_file:
                old_score_dict = json.load(score_file)
                for score_code, score in score_dict.items():
                    if score_code not in old_score_dict:
                        email_remind(
                            to_addr=account['email'],
                            subject="<{}> 出成绩了..".format(score['课程名称']),
                            message=msg_template.format(
                                course_name=score['课程名称'],
                                score=score['成绩'],
                                detail=str(score),
                                gpa=zf.get_gpa(),

                            )
                        )
                score_file.seek(0)
                json.dump(score_dict, score_file)
