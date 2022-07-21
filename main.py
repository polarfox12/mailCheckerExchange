# For install requirements use command "pip install -r requirements.txt" in cmd with active env

import logging
import smtplib
import imaplib
import time
import email
import requests
from settings import TOKEN_TELEGRAM, CHANEL_ID_TELEGRAM, WAITING_TIME, mailbox1, mailbox2
from exchangelib import DELEGATE, Account, Credentials, Configuration, NTLM, Message, Mailbox


logging.basicConfig(filename="main.log", level=logging.INFO)


def send_message(host, port, subject, to_addr, from_addr, text, username, password):
    body = "\r\n".join((
        "From: %s" % from_addr,
        "To: %s" % to_addr,
        "Subject: %s" % subject,
        "",
        text
    ))

    server = smtplib.SMTP(host, port)
    server.starttls()
    logging.info(time.asctime() + ' connect to server ' + host)
    server.login(username, password)
    logging.info(time.asctime() + ' ' + host + ' connected')
    server.sendmail(from_addr, [to_addr], body)
    logging.info(time.asctime() + ' message from {0} to {1} sending!'.format(from_addr, to_addr))
    server.quit()


def get_message(username, password, host):
    logging.info(time.asctime() + ' connect to server ' + host)
    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)
    logging.info(time.asctime() + ' ' + host + ' connected')
    mail.list()
    mail.select('inbox')

    result, data = mail.search(None, 'ALL')

    ids = data[0]
    id_list = ids.split()
    if len(id_list) == 0:
        return None
    latest_email_id = id_list[-1]

    result, data = mail.fetch(latest_email_id, '(RFC822)')
    raw_email = data[0][1]
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)
    return email_message


def send_telegram(text: str, chanel_id):
    token = TOKEN_TELEGRAM
    url = "https://api.telegram.org/bot"
    chanel_id = chanel_id
    url += token
    method = url + "/sendMessage"

    r = requests.post(method, data={
        "chat_id": chanel_id,
        "text": text
    })
    print(r)

    if r.status_code != 200:
        try:
            raise Exception('post_text_error', r.status_code)
        except Exception as e:
            logging.error(time.asctime() + ' Message NOT send in telegram ' + str(r.status_code))
            pass
    logging.info(time.asctime() + ' Message send in telegram')


def clear_inbox(host, username, password):
    imap = imaplib.IMAP4_SSL(host)
    imap.login(username, password)
    imap.select("INBOX")
    status, messages = imap.search(None, "ALL")
    if len(messages) == 0:
        return None
    messages = messages[0].split()
    for mail in messages:
        _, msg = imap.fetch(mail, "(RFC822)")
        imap.store(mail, "+FLAGS", "\\Deleted")


def account_exchange(smtp_srv, login, password, src_address):
    config = Configuration(
        server = smtp_srv,
        credentials=Credentials(username=login, password=password),
        auth_type=NTLM,
        # verify_ssl=False
    )
    account_exchange = Account(
        primary_smtp_address=src_address,
        config=config,
        access_type=DELEGATE,
    )
    return account_exchange


def send_message_exchange(account, subject, text_mail, to_recipients):
    message = Message(account=account,
                      folder=account.sent,
                      subject=subject,
                      body=text_mail,
                      to_recipients=[Mailbox(email_address=to_recipients)])
    message.send()


def main():
    print('running...')
    text_smtp = 'Test email from Python'
    mailboxes = [mailbox1, mailbox2]
    counter = 0
    errors = 0
    alarms = 0
    last_mail = None
    while True:
        for box in mailboxes:
            if box.port_smtp == 'Exchange':
                try:
                    exchange_box = account_exchange(box.smtp_srv, box.login, box.password, box.from_address)
                    exchange_box.inbox.all().delete()
                except Exception as e:
                    logging.error(time.asctime() + ' CLEAR_INBOX_EXCHANGE_ERROR: ' + str(e))
                    errors += 1
                    continue
            else:
                try:
                    clear_inbox(box.imap_srv, box.login, box.password)
                except Exception as e:
                    logging.error(time.asctime() + ' CLEAR_TEST_BOX_ERRORS: ' + str(e))
                    errors += 1
                    continue
        for box in mailboxes:
            box.subject = time.asctime()
            if box.port_smtp == 'Exchange':
                try:
                    logging.info(time.asctime() + ' connect to server ' + box.smtp_srv)
                    exchange_box = account_exchange(box.smtp_srv, box.login, box.password, box.from_address)
                    logging.info(time.asctime() + box.smtp_srv + ' connected')
                    send_message_exchange(exchange_box, box.subject, text_smtp, box.to_address)
                    logging.info(time.asctime() + ' message from {0} to {1} sending!'.format(box.from_address, box.to_address))
                except Exception as e:
                    logging.error(time.asctime() + ' EXCHANGE_SEND_MESSAGE_ERROR: ' + str(e))
                    errors += 1
                    continue
            else:
                try:
                    send_message(box.smtp_srv, box.port_smtp, box.subject, box.to_address, box.from_address, text_smtp, box.login, box.password)
                except Exception as e:
                    logging.error(time.asctime() + ' TEST_BOX_SEND_MESSAGE_ERROR: ' + str(e))
                    errors += 1
                    continue
        logging.info(time.asctime() + 'wait...')
        time.sleep(WAITING_TIME)
        logging.info(time.asctime() + 'unsleeping')
        mailbox1.subject, mailbox2.subject = mailbox2.subject, mailbox1.subject
        for box in mailboxes:
            if box.port_smtp == 'Exchange':
                imap_counter = 0
                while imap_counter < 5:
                    try:
                        logging.info(time.asctime() + ' connect to server ' + box.imap_srv)
                        exchange_box = account_exchange(box.smtp_srv, box.login, box.password, box.from_address)
                        logging.info(time.asctime() + ' Exchange connected')
                        mail = exchange_box.inbox.all().order_by()
                        logging.info(time.asctime() + ' Message getting')
                        last_mail = mail[0].subject
                        logging.info(time.asctime() + ' Subject getting')
                        imap_counter += 5
                    except Exception as e:
                        logging.error(time.asctime() + ' IMAP_EXCHANGE_ERROR: ' + str(e))
                        errors += 1
                        imap_counter += 1
                        time.sleep(120)
                        continue
            else:
                try:
                    last_mail = get_message(box.login, box.password, box.imap_srv)
                    last_mail = last_mail['Subject']
                except Exception as e:
                    logging.error(time.asctime() + ' IMAP_TEST_BOX_ERRORS: ' + str(e))
                    last_mail = None
                    errors += 1
                    continue
            if last_mail is None or box.subject != last_mail:
                logging.info('ALARM TO TELEGRAM!!!')
                text = 'Сообщение не доставлено!\n From: {0}\n To: {1}\n Subject: {2}\n Проверьте работоспособность почтового сервиса'.format(box.to_address, box.from_address, box.subject)
                alarms +=1
                try:
                    send_telegram(text, CHANEL_ID_TELEGRAM)
                except Exception as e:
                    logging.error(time.asctime() + ' SEND_TO_TELEGRAM_ERRORS: ' + str(e))
                    errors += 1
                    continue

        counter += 1
        logging.info(time.asctime() + '\n Counter: {0} \n Errors: {1} \n Alarms: {2} \n'.format(counter, errors, alarms))


if __name__ == '__main__':
    main()
