# Run a test server.
from app import app
import logging
from logging.handlers import RotatingFileHandler

# from werkzeug.contrib.profiler import ProfilerMiddleware

# initialize the log handler
logHandler = RotatingFileHandler('info.log', maxBytes=1000, backupCount=1)

# set the log handler level
logHandler.setLevel(logging.INFO)

# set the app logger level
app.logger.setLevel(logging.INFO)

app.logger.addHandler(logHandler)

if __name__ == '__main__':
#    app.config['PROFILE'] = True
#    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
    app.run(host='127.0.0.1', port=8000)