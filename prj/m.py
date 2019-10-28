import smtplib

content ="Auction is going to start"

mail=smtplib.SMTP('smtp.gmail.com:587')

mail.ehlo()

mail.starttls()

mail.login('ayush.astra@gmail.com','9290827021')

mail.sendmail('ayush.astra@gmail.com','ayush632000@gmail.com',content)

mail.close