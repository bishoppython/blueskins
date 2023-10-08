from werkzeug.middleware.dispatcher import DispatcherMiddleware
from elevacao.PILOT_index import elevacao
from calendarcco.CCO_index import calendarcco
from flask import Flask
from home_app import server as app_home

base_app = Flask(__name__)

app = DispatcherMiddleware(base_app, {
    '/elevacao': pilot.server,
    '/calendarcco':  calendarcco.server,
    '/': app_home
})
