# -*- coding: utf-8 -*-

import psycopg2, smtplib, mimetypes, base64
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 

pgsql_pass = 'WUEwSU5aMTRRUjQ4'

pgsql_conn = psycopg2.connect(host='10.244.216.39',port=5432,database='webplatform',user='webplatform_admin',password=base64.b64decode(pgsql_pass.encode()).decode())

cursor = pgsql_conn.cursor()

def send_email(addr_to, msg_subj, msg_text):
	addr_from = "viy@sber-bank.by"
	msg = MIMEMultipart()
	msg['From']    = addr_from
	msg['To']      = addr_to
	msg['Subject'] = msg_subj
	body = msg_text
	msg.attach(MIMEText(body, 'plain'))
	server = smtplib.SMTP('10.244.216.42', 25)
	server.send_message(msg)
	server.quit()

sql = """select u.mail, u.username from webplatform.users u, webplatform.reg_requests r 
where 
u.grants is not Null
and u.status = 'I'
and r.req_type = 'REGISTER'
and r.status = 'A'
and r.username = u.username"""

cursor.execute(sql)

emails_usernames = cursor.fetchall()

for email_usermane in emails_usernames:
	cursor.execute(f"update webplatform.users set status = 'A' where username = '{email_usermane[1]}'")
	cursor.execute(f"update webplatform.reg_requests set status = 'I' where username = '{email_usermane[1]}' and req_type = 'REGISTER'")
	pgsql_conn.commit()
	mail_text = """
Приветствую!
        
Рады сообщить, что Ваша заявка на регистрацию в Веб-платформе ВИЮ одобрена.
Можете повторить попытку входа.

Данное сообщение сгенерировано автоматически, пожалуйста не отвечайте на него."""

	send_email(email_usermane[0],'Одобрение заявки на Веб-платформе ВИЮ',mail_text)

pgsql_conn.close()
