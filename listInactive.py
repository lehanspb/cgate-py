#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# *************************************************************************
# listInactive.py
# listInactive_exclude.txt
# *************************************************************************
'''
Sends out email with inactive account names (who had not logged in recently)

Please mail your comments and suggestions to <g@lehan.ru>
'''

from collections import namedtuple
from email import message
from CGPCLI.Commands import Server
from CGPCLI.Parser import parse_to_python_object
import CGPCLI.Errors
import datetime
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import socket
from os.path import join, abspath, dirname

####  YOU SHOLD REDEFINE THESE VARIABLES !!!

inactivityDays = 60
exclude_file = 'listInactive_exclude.txt'

smtp_server = 'smtp.domain'
port = 465
sender_email = 'adminemail@domain'
use_auth = False # Use SMTP authentication True/False
password = '' # If use_auth == True set this
receiver_email  = 'adminemail@domain'

pwd_server = 'mailserver.domain' # Communigate PWD CLI
pwd_user = 'postmaster'
pwd_password = 'password'

#### end of the customizeable variables list

def str_dt_to_str(date_time_str):
	''' Convert str date '30-11-2012_20:00:19' from Communigate Created date format to string'''
	date_time_obj = datetime.datetime.strptime(date_time_str, '%d-%m-%Y_%H:%M:%S').strftime("%Y.%m.%d")
	return str(date_time_obj)

def str_to_dt(date_time_str):
	''' Convert date time format '21-07-2011_12:33:21' from Communigate Created date format to datetime.date object'''
	date_time_obj = datetime.datetime.strptime(date_time_str, '%d-%m-%Y_%H:%M:%S')
	return date_time_obj

def dt_convert_ll(date_time_str):
	''' Convert date from Communigate LastLogin date format to human'''
	# date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S').strftime("%Y.%m.%d")
	return str(date_time_str.strftime("%Y.%m.%d"))

def convert_bytes(num):
	step_unit = 1024
	for x in ['b', 'Kb', 'Mb', 'Gb', 'Tb']:
		if num < step_unit:
			return f'{round(num, 1):g} {x}'
		num /= step_unit

def check_loc(loc):
	if 'Accounts' in loc:
		return loc.partition('/')[0]
	else:
		return 'Accounts'

hostname = socket.gethostname()



# Try open text file exclude. If not found - skip exclude check
current_dir = dirname(__file__)
exclude_path = join(current_dir, exclude_file)
exclude_path = abspath(exclude_path)
exclude = set()
try:
	with open(exclude_path) as f:
		exclude = set([line.rstrip('\n') for line in f])
except FileNotFoundError:
	print(f'File {exclude_path} not found. Skipping...')

deadline = datetime.datetime.now() - datetime.timedelta(days=inactivityDays)

# Connect to Communigate
server = Server(pwd_server)

# list accounts
ll = []
# list failed accounts
lf = []

try:
	server.connect()
	server.login(pwd_user, pwd_password)

	domains = server.list_domains()
	dom = namedtuple('Domains', domains.keys())(*domains.values())
	i = 0
	for domain in dom.body:
		locations = server.list_account_storage(domain)
		locations_multiple = True if locations.get('body') else False
		ll.insert(i, [])
		lf.insert(i, [])
		data = server.list_accounts(domain)
		accounts = list(acc for acc in data['body'])
		ll[i].append(domain)
		ll[i].append([])
		lf[i].append(domain)
		lf[i].append([])
		for login in accounts:
			full_acc_name = login + '@' + domain
			accinfo = server.get_account_info(full_acc_name)
			accloc = server.get_account_location(full_acc_name)
			loc = accloc.get('body')
			loc = check_loc(loc)
			name = accinfo['body'].get('Created')
			timecr = accinfo['body'].get('Created')
			lastip = accinfo['body'].get('LastAddress', 'no data').strip('[]')
			lastlogin = accinfo['body'].get('LastLogin')
			du = int(accinfo['body'].get('StorageUsed'))
			if full_acc_name not in exclude:
				if lastlogin is not None:
					if timecr is not None:
						timecr_str = str_dt_to_str(accinfo['body'].get('Created'))
						timecr_dt = str_to_dt(accinfo['body']['Created'])
					else:
						timecr_str = 'no data'
					lastlogin_str = dt_convert_ll(lastlogin)
					lastlogin_dt = accinfo['body']['LastLogin']
					if lastlogin_dt < deadline > timecr_dt:
						# ll[i].append((full_acc_name, timecr_str, lastlogin_str, lastip))
						ll[i][1].append((full_acc_name, timecr_str, lastlogin_str, lastip, du, loc))
						# print(f'Acc: {full_acc_name}\tCreated: {timecr_str}\tLast login: {lastlogin_str}\t Last IP: {lastip}')
				else:
					# lf[i][1].append(full_acc_name)
					if timecr is not None:
						timecr_str = str_dt_to_str(accinfo['body'].get('Created'))
					else:
						timecr_str = 'no data'
					# ll[i][1].append((full_acc_name, timecr_str, 'no data', lastip, du))
					lf[i][1].append((full_acc_name, timecr_str, 'no data', lastip, du, loc))
		ll[i][1].sort(key=lambda x:x[2], reverse=True)
		lf[i][1].sort(key=lambda x:x[1], reverse=True)
		ll[i][1] = ll[i][1] + lf[i][1]
		i += 1
	server.disconnect()
	message = '<html>\n'
	message += '<head>\n'
	message += '<head>\n'
	message += '<style>\n'
	message += 'table {border-collapse: collapse; margin: 0px auto;}\n'
	message += 'th, td {border: solid 1px #000; padding: 5px 15px;}\n'
	message += 'th {background-color: #5c87b2; text-align:center;}\n'
	message += 'table tr:nth-child(odd) {background: #C9E4F6;}\n'
	message += 'table tr:nth-child(even) {background: #B4DAF2;}\n'
	message += 'h3, p {text-align:center;}\n'
	message += '</style>\n'
	message += '</head>\n'
	message += '<body>\n'
	# message += f'<h3>Список почтовых ящиков {", ".join(str(v[i]) for i, v in enumerate(ll) if ll[i][1])}, к которым не обращались более {inactivityDays} дней</h3>\n'
	# message += f'<p>Примите меры или добавьте в список исключений</p>\n'
except ConnectionRefusedError as e:
  	print(f'CLI: Connection to {pwd_server} refused')
except CGPCLI.Errors.FailedLogin:
	print(f'CLI: Wrong username or password')
except TimeoutError:
	print(f'CLI: connection to {pwd_server} is timed out')
except socket.gaierror as e:
	print(f'CLI: Could not connect to {pwd_server}')
except:
  	print(f'CLI: Could not connect to {pwd_server}')
else:
	y = 0
	sendmail_allow = False
	for i in ll:
		# if no inactive accounts
		if i[1]:
			sendmail_allow = True
			message += f'<h3>{i[0]}</h3>\n'
			message += f'<table>\n'
			message += f'<tr><th>Acc</th><th>Created</th><th>Last login</th><th>Last IP</th><th>Storage Used</th>{"<th>Location</th>" if locations_multiple else ""}</tr>\n'
			for j in i[1]:
				message += f'<tr><td><strong>{j[0]}</strong></td><td>{j[1]}</td><td><strong>{j[2]}</strong></td><td>{j[3]}</td><td>{convert_bytes(j[4])}</td>{"<td>"+j[5]+"</td>" if locations_multiple else ""}</tr>\n'
				# print(f'{(j)=}')
			message += f'</table>\n'
			# print(f'{(lf)=}')
			# message += f'<p>Аккаунты никогда не использовались, либо пустое поле LastLogin:<br>{", ".join(str(i) for i in lf[y][1])}</p>\n'
			y += 1
		else:
			message += f'<p>В домене <strong>{i[0]}</strong> неактивных аккаунтов нет</p>\n'

	message += '<hr>\n'
	message += f'<div class=\'not\'><i>Generated by {hostname}</i></div>\n'
	message += '</body>\n'
	message += '</html>\n'

	msg = MIMEMultipart()
	msg['From'] = sender_email
	msg['To'] = receiver_email
	msg.add_header('Content-Type', 'text/html')
	msg.add_header('content-transfer-encoding', 'quoted-printable')
	msg['Subject'] = f'[CGate {", ".join(str(v[0]) for i, v in enumerate(ll) if ll[i][1])}] Список неактивных почтовых ящиков'
	msg.attach(MIMEText(message, 'html'))

	
	if sendmail_allow:
		context = ssl.create_default_context()
		with smtplib.SMTP_SSL(smtp_server, port, context) as server:
			try:
				if use_auth:
					server.login(sender_email, password)
				server.sendmail(sender_email, receiver_email, msg.as_string())
			except smtplib.SMTPAuthenticationError:
				print(f'SMTP: incorrect password or account name')
			except smtplib.ConnectionRefusedError:
				print(f'SMTP: connection refused')
			except TimeoutError:
				print(f'SMTP: connection is timed out')
			except:
				print(f'SMTP: failed')

