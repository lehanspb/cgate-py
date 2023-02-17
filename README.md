# cgate-py
Useful Python scripts for Communigate Pro

## listInactive.py
Sends out email with inactive account names (who had not logged in recently)

### Running the program

listInactive.py needs an installed CPGCLI module.
```
pip install CGPCLI==1.1.9
```

In the Communigate Pro settings you need to enable PWD listener (assign IP and port)
```
Settings -> Services -> PWD -> TCP
```
You should also limit the IP addresses from which connections to the PPTP server are allowed.

Settings inside listInactive.py file:
```
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
```

