# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

msg = EmailMessage()
msg.set_content('This is a test')



# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = 'Test Python Email'
msg['From'] = 'no-reply@nyu.edu'
msg['To'] = 'cmn10@nyu.edu'

# Send the message via our own SMTP server.
s = smtplib.SMTP('smtp.nyu.edu', 25)
s.send_message(msg)
s.quit()
