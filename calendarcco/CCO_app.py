
import dash
import dash_bootstrap_components as dbc
import dash_auth
from flask_caching import Cache
from flask_session import Session
from flask import Flask, session,request
import flask
from CCO_sql import *

key = acesso_banco_sql()
VALID_USERNAME_PASSWORD_PAIRS = dict(zip(key['PASSWORD'],key['USERNAME']))
#VALID_USERNAME_PASSWORD_PAIRS = {'000':'000'}

estilos = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css", "https://fonts.googleapis.com/icon?family=Material+Icons", dbc.themes.COSMO]
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"


# FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"
cache = Cache()
server = Flask(__name__)
server.config['SECRET_KEY']='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
calendarCCO = dash.Dash(__name__, external_stylesheets= estilos + [dbc.themes.BOOTSTRAP],server=server,suppress_callback_exceptions=True, requests_pathname_prefix='/calendarcco/')
# auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)
calendarCCO.title = 'Agenda CCO'
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)
calendarCCO.scripts.config.serve_locally = True
sess = Session()
sess.init_app(calendarCCO)
Session(calendarCCO)