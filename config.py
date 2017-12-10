import os

class BaseConfig(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = '\xf5+j\xf0x\xbb\x977\x7f_\x8d\x7f\x05\xe0_\xb9\xb3P\x83^\x8b\x066E'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    DEBUG = True
    BOOTSTRAP_SERVE_LOCAL = True
