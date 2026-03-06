
from flask import Flask
from my_server.config import Config

app = Flask(__name__)    
app.config.from_object(Config)

from my_server import routes

from my_server.errors import register_errorhandlers
register_errorhandlers(app)

