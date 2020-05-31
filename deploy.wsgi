import os
import sys
import site

# Add virtualenv site packages
site.addsitedir(os.path.join(os.path.dirname(__file__), '/lib/python3.5/site-packages'))

# Path of execution
sys.path.append('/var/www/html/repupro/')

activate_this = '/var/www/html/repupro/env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# import my_flask_app as application
from app import app as application