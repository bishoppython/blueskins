import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import flask

server = flask.Flask(__name__)

app_home = dash.Dash(__name__, server=server, url_base_pathname='/')

app_home.layout = html.Div([
    html.H1('Página Inicial'),
    html.Div([
        dcc.Link(html.Img(src='/static/icon1.png', alt='Ícone 1'), href='/page1'),
        dcc.Link(html.Img(src='/static/icon2.png', alt='Ícone 2'), href='/page2'),
        dcc.Link(html.Img(src='/static/icon3.png', alt='Ícone 3'), href='/page3'),
    ])
])

if __name__ == '__main__':
    app_home.run_server(debug=True)
