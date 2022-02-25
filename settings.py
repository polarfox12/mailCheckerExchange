import os
import dotenv

dotenv.load_dotenv('.env')


# MAILBOX1_SETTINGS
PASS_MAILBOX1 = os.environ['PASS_MAILBOX1']
LOGIN_MAILBOX1 = os.environ['LOGIN_MAILBOX1']
SMTP_SERVER_BOX1 = 'owa.medicina.ru'
DEST_ADDRESS_SMTP_BOX1 = 'for.test.mail.003@gmail.com'
IMAP_SERVER_BOX1 = 'owa.medicina.ru'
PORT_SMTP_BOX1 = 'Exchange'
SRC_ADDRESS_BOX1 = 'maildeliverychecker@medicina.ru'

# MAILBOX2_SETTINGS
PASS_MAILBOX2 = os.environ['PASS_MAILBOX2']
LOGIN_MAILBOX2 = os.environ['LOGIN_MAILBOX2']
SMTP_SERVER_BOX2 = 'smtp.gmail.com'
DEST_ADDRESS_SMTP_BOX2 = 'maildeliverychecker@medicina.ru'
IMAP_SERVER_BOX2 = 'imap.gmail.com'
PORT_SMTP_BOX2 = 587
SRC_ADDRESS_BOX2 = 'for.test.mail.003@gmail.com'

# TELEGRAM_SETTINGS
TOKEN_TELEGRAM = os.environ['TOKEN_TELEGRAM']
CHANEL_ID_TELEGRAM = os.environ['CHANEL_ID_TELEGRAM']

# LOGIC_SETTINGS
WAITING_TIME = 600


class Mailbox(object):

    def __init__(self,smtp_srv, port_smtp, imap_srv, login, password, from_address, to_address):
        self.smtp_srv = smtp_srv
        self.port_smtp = port_smtp
        self.imap_srv = imap_srv
        self.login = login
        self.password = password
        self.from_address = from_address
        self.to_address = to_address

mailbox1 = Mailbox(SMTP_SERVER_BOX1, PORT_SMTP_BOX1, IMAP_SERVER_BOX1, LOGIN_MAILBOX1, PASS_MAILBOX1, SRC_ADDRESS_BOX1, DEST_ADDRESS_SMTP_BOX1)
mailbox2 = Mailbox(SMTP_SERVER_BOX2, PORT_SMTP_BOX2, IMAP_SERVER_BOX2, LOGIN_MAILBOX2, PASS_MAILBOX2, SRC_ADDRESS_BOX2, DEST_ADDRESS_SMTP_BOX2)

