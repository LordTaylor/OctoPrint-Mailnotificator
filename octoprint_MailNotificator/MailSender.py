import smtplib
class MailSender(object):
    printer_Mail = '' 
    printer_Mail_Password = '' 
    server_address = ''
    your_Mail = ''


    sent_from = printer_Mail
    to = ['',''] 
    subject = 'OMG Super Important Message'
    body = 'Hey, whats up?\n\n- You'

    email_text = """\
    From: %s
    To: %s
    Subject: %s
    %s
    """ % (sent_from, ", ".join(to), subject, body)
    def __init__(self,printerMailAddres,mailPassword,yourMailAddress,server,port):
        self.gmail_user = printerMailAddres
        self.gmail_password = mailPassword
        self.to = [printerMailAddres,yourMailAddress]
        self.server_address = server
        self.server_port = port
        self.your_Mail = yourMailAddress

    def sendMail(self, title):
        try:
            server = smtplib.SMTP_SSL(self.server_address, self.server_port)
            server.ehlo()
            server.login(self.printer_Mail, self.printer_Mail_Password)
            server.sendmail(self.sent_from, to,self.email_text)
            server.close()

            print ('Email sent!')
        except:
            print ('Something went wrong...')