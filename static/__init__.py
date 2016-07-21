import os
# __file__ refers to the file settings.py
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')
APP_RES = os.path.join(APP_ROOT, 'res')
APP_LIB = os.path.join(APP_ROOT, 'lib')

APP_PARSER = os.path.join(APP_LIB, 'stanford-parser-2013')
APP_NLTK_DATA = os.path.join(APP_LIB, 'nltk_data')
APP_RULES = os.path.join(APP_RES, 'rules')