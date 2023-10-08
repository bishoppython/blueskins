import dash
import dash_bootstrap_components as dbc
#from sql_server import *
import dash_auth
from flask_caching import Cache
from flask_session import Session
from flask import Flask, session,request

#key = acesso_banco_sql()
#VALID_USERNAME_PASSWORD_PAIRS = dict(zip(key['PASSWORD'],key['USERNAME']))
VALID_USERNAME_PASSWORD_PAIRS = {'000':'000'}


# FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"
cache = Cache()
server = Flask(__name__)
server.config['SECRET_KEY']='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
pilot = dash.Dash(__name__, external_stylesheets= [dbc.themes.CERULEAN],server=server,suppress_callback_exceptions=True, requests_pathname_prefix='/elevacao/')
# auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

auth = dash_auth.BasicAuth(pilot, VALID_USERNAME_PASSWORD_PAIRS)
pilot.scripts.config.serve_locally = True


sess = Session()
sess.init_app(pilot)
Session(pilot)
