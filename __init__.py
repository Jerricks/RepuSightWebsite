from flask import Flask
from flask_login import LoginManager
from logging import Formatter
import logging


app = Flask(__name__)
app.config.from_object('config')
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from logging.handlers import SMTPHandler

ADMINS = ['sanket.mokashi@repusight.com', 'shubham.trivedi@repusight.com']
mail_handler = SMTPHandler(mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                               fromaddr=app.config['DEFAULT_MAIL_SENDER'], toaddrs=ADMINS,
                               credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']),
                               subject='Application Failed', secure=())
mail_handler.setLevel(logging.ERROR)

mail_handler.setFormatter(Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
    '''))

app.logger.addHandler(mail_handler)


from app import views