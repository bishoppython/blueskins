import dash
from dash import Dash, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import ALL
from dash import html, dcc
import pyodbc
import pandas as pd
import datetime
import json
import os
from dash_table import DataTable
import calendar
from dash.exceptions import PreventUpdate
# from app import app
from CCO_app import *
from CCO_sql import *
import pdb
import ast





meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
        'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

df = pd.DataFrame({
    ("SEG"): [None]*6,
    ("TER"): [None]*6,
    ("QUA"): [None]*6,
    ("QUI"): [None]*6,
    ("SEX"): [None]*6,
    ("SAB"): [None]*6,
    ("DOM"): [None]*6,
})


y = datetime.datetime.today().year
m = datetime.datetime.today().month
h = datetime.datetime.today().day

anos_ = [(y+28) - i for i in range(51)]
anos = list(reversed(anos_))


def get_calendar(y, m):
    calendar_ = calendar.month(y, m)
    calendar_ = calendar_.split('\n')[2:-1]

    pos_primeiro_dia = calendar_[0].find('1')
    dict_position_to_days = {1: "SEG", 4: "TER", 7: "QUA", 10: "QUI", 
                            13: "SEX", 16: "SAB", 19:"DOM"}
    first_day = dict_position_to_days[pos_primeiro_dia]
    last_day = int(calendar_[-1].split(" ")[-1])
    return first_day, last_day


lista_de_eventos = seacher_banco_sql()


# =========  Layout  =========== #
app.layout = dbc.Container([
        dcc.Location(id="url"),
        dcc.Store(id='month', data=m),
        dcc.Store(id='year', data=y),

        dcc.Store(id='intermediate-data-store', storage_type='memory'),
        html.Div([
        dcc.Store(id='lista-de-eventos', data=lista_de_eventos),
            # Inicializar dcc.Store com dados
            dcc.Interval(
                id='interval-component',
                interval=30*60*1000,  # em milissegundos (24 minutos aqui como exemplo)
                n_intervals=0
            ),
        ]),
        dbc.Row([
            dbc.Row([ dbc.Col([
            dbc.CardGroup([
            html.Img(src='assets/azul-logo.png',style={'Width':'100px','height':'100px','align-items':'center','margin-top':'0%','padding-top':'0%'}),
                                        html.Div(id='welcome_name'),html.Div(id='name',style={'font-size':'10px'})
                            ])
                    ], width=4),
            dbc.Col([html.P('Agenda Evento CCO')],width=8, style={'color' : 'white', 'font-size' : '40px', 'margin-top' : '16px'}),
            dbc.Row([html.Div(id='user_new',style={'color':'white'}),html.Div(id='latest-timestamp',style={'color':'white'})]),
            html.Div(
                [
                    dbc.Button(
                        "Calendário completo do mês", id="open-offcanvas-backdrop", n_clicks=0, style={'color':'tomato'}
                    ),
                    dbc.Offcanvas(
                        id="offcanvas-backdrop",
                        title="Calendário do mês",
                        is_open=False,
                        placement ='end'
                    ),
                ])
            ]),
            dbc.Col([
                dbc.Col([
                    dbc.Row([
                        dbc.Button('<', id='voltar',
                        style={'color' : 'black',
                        'background-color' : '#ffffff',
                        'border' : '1px solid black',
                        'border-radius' : '50%',
                        'width' : '35px',
                        'minheight': '35px',
                        'maxheight': '75px',
                        'margin-top' : '60px',
                        'margin-left' : '280px',
                        'font-weight' : 'bold',
                        'font-size' : '20px',
                        'padding' : '0px 0px'
                        }),

                        dbc.Button('>',id='avancar',
                        style={'color' : 'black',
                        'background-color': '#ffffff',
                        'border' : '1px solid black',
                        'border-radius' : '50%',
                        'width' : '35px',
                        'height' : '35px',
                        'margin-top' : '60px',
                        'margin-left' : '160px',
                        'font-weight': 'bold',
                        'font-size' : '20px',
                        'padding' : '0px 12px'
                        }),

                        html.Div('Ano', 
                        style={'width' : 'fit-content',
                        'padding' : '0px',
                        'textAlign': 'center',
                        'margin-left' : '-160px', 
                        'margin-top' : '45px', 
                        'font-weight': 'bold',
                        'font-size' : '40px',
                        'background-color' : 'transparent'},
                        id='div-ano',
                        className='primary-font-color')
                    ]),
                    dbc.Row([
                        html.Div('Mês',
                        style={'width' : '130px',
                        'textAlign': 'center',
                        'margin-left' : '330px',
                        'margin-top' : '0px',
                        'font-weight': 'bold',
                        'font-size' : '26px',
                        'background-color' : 'transparent'},
                        id='div-mes',
                        className ='secundary-font-color')
                    ]),
                    dbc.Row([
                        DataTable(df.to_dict('records'), [{"name" : i, "id": i} for i in df.columns], id="calendar",
                        style_table={'border': '2px solid transparent',
                                    'height': '490px',
                                    'minwidth' : '715px',
                                    'maxWidth' : '1200px',
                                    'margin-top' : '20px',
                        
                                    },
                        style_data_conditional=[],
                        style_cell={'height': '6.5rem'},
                        style_data={'border': '0px',  
                                    'backgroundColor': 'transparent', 
                                    'textAlign' : 'center'},
                        style_header={'border': '0px', 
                                        'color' : 'rgba(255,255,255, 0.4)',
                                        'backgroundColor': 'transparent', 
                                        'textAlign' : 'center', 
                                        'font-weight': 'bold'},
                        ),
                        

                    ], className='primary-font-color'),
                ], md=12, style={'margin-left' : '7.5px', 'margin-top' : '35px', 'border-top-left-radius': '2%',
                                    'border-bottom-left-radius' : '2%'},  className = 'primary-color'),
            ], md = 7,),

            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Div(id='div-dia-mês-atual',
                        style={'margin-left' : '0px',
                                'margin-top' : '20px', 
                                'width' : 'fit-content',
                                'height' : 'fit-content',
                                'font-size': '150px',
                                'line-height': '0.85',
                                'background-color' : 'transparent'},
                                className='primary-font-color'
                        ),

                        html.Div(id='div-dia-semana-atual',
                                style={'margin-left' : '172px',
                                'margin-top' : '-30px', 
                                'width' : '140px',
                                'height' : '30px',
                                'font-size': '20px',
                                'background-color' : 'transparente'},
                                className='primary-font-color'
                        ),

                    ], md=8, className = 'secundary-color'),
                    dbc.Col([
                        html.Div("Adicionar nova tarefa",
                                style={'margin-left' : '20px',
                                'margin-top' : '48px', 
                                'width' : '80px',
                                'height' : '50px',
                                'text-align' : 'left'},
                                className='primary-font-color'
                        ),

                    dbc.Button([html.I(className = "fa fa-plus", style={'font-size' : '400%'})],
                                    id='open-modal-button',
                                    style={'width' : '40px',
                                            'height' : '40px',
                                            'margin-top' : '-77px',
                                            'margin-left' : '120px',
                                            'border-radius' : '50%'},
                                    
                        ),  
                        html.Div(id='div-data-concatenada',
                                hidden=True  
                        )
                    ], md=4, className = 'secundary-color', style={ 'border-top-right-radius' : '7%'}),
                ], style={'margin-top' : '35px', 'width' : '550px'}),
                dbc.Row([
                    dbc.Card(style = {'color' : '#000000',
                        'border-radius' : '0px',
                        'width' : '550px',
                    #   'height' : '500px',
                        'min-height': '490px', 
                        'min-height': '513px',
                        'margin-left' : '0px',
                        'margin-top' : '0px',
                        'background-color': 'rgba(0,0,0)',
                        'border-bottom-right-radius' : '2%'},
                        id='card-geral')
                ])
            ], md = 5)

        ]),

            dbc.Modal([
                dbc.ModalHeader("Nova tarefa", style={'color' : '#ffffff', 'font-size' : '20px'}, className = 'modal-color'),

            dbc.ModalTitle(
                dbc.Input(id="titulo-input", 
                                        placeholder="Adicione um título", type="text", 
                                        style={'width' : '400px',
                                                'border-top' : 'transparent',
                                                'border-left' : 'transparent',
                                                'border-right' : 'transparent',
                                                'border-bottom' : '2px solid black',
                                                'border-radius' : '0px',
                                                'margin-left' : '10px',
                                                'font-weight': 'bold',
                                                'margin-top' : '20px',
                                                },
                                        className='input-modal-color'
                                        
                    ), className = 'modal-color'
            ),

dbc.ModalBody([

            
                dbc.Select(id="type_event",  
                            style={'width' : '450px',
                                    'margin-top' : '20px',
                                    'border' : '1px solid black',
                                    'font-size' : '16px'},
                            className='input-modal-color',
                            #maxlength=7
                    
                    ),        dbc.Label("Nível de Prioridade",style={'color':'white'}),
                dbc.RadioItems(
                options=[
                {"label": html.I('🔴'), "value": 1},
                {"label": html.I('🟡'), "value": 2},
                {"label": html.I('🟢'), "value": 3,},
                ],
                    value=[1],
                    id="radioitems-input",style={'color':'white'}
                ),
                    
                dbc.Input(id="local-input", placeholder="Local", type="text", 
                            style={'width' : '450px',
                                    'margin-top' : '20px',
                                    'border' : '1px solid black'},
                            className='input-modal-color'
                    ),
                dbc.Input(id="dep_pref", placeholder="Dep/Prefixo", type="text", 
                            style={'width' : '450px',
                                    'margin-top' : '20px',
                                    'border' : '1px solid black'},
                            className='input-modal-color'
                    ),
                dbc.Input(id="arr_pref", placeholder="Arr/Prefixo", type="text", 
                            style={'width' : '450px',
                                    'margin-top' : '20px',
                                    'border' : '1px solid black'},
                            className='input-modal-color'
                    ),

                dbc.Input(id="descricao-input", placeholder="Descrição", type="text", 
                            style={'width' : '450px',
                                    'margin-top' : '20px',
                                    'border' : '1px solid black'},
                            className='input-modal-color'
                    ),

                html.Div(id="required-field-notification", 
                            style={'width' : '450px',
                                    'margin-top' : '20px'},
                            className ='secundary-font-color'
                    ),

                dbc.Button('Salvar',  color="light", className="me-1", id='submit-tarefa', n_clicks=0,
                            style={'margin-top' : '15px',
                                        'margin-left' : '390px',
                                        'font-weight': 'bold',
                                        'font-size' : '16px',}
                    )
            ], className = 'modal-color'),



            ],style={'color' : '#000000',
                    'background-color' : 'rgba(255, 255, 255, 0.4)'},
                    id="modal-tarefa",
                    is_open=False
            ),



        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Excluir?")),
                dbc.ModalBody(
                dbc.Button("OK", id="okay-delet", className="me-1", n_clicks=0),
                    ),
            ],
            id="modal-delet",
            size="sm",
            is_open=False,
        ),

], fluid=True, style={"display" : "flex", "justify-content" : "center"})



# =========  Callback  =========== #

@app.callback(
    Output('calendar', 'style_data_conditional'),


    Input('lista-de-eventos', 'data'),
    Input('month', 'data'),
    Input('year', 'data'),
    prevent_initial_call=True
)
def color_days(store_data,mm,yy):
    lista_de_eventos = store_data
    styles = []

    try:
        df_data = pd.DataFrame(lista_de_eventos)
    
    # Filtrando os dados com base no mês e ano
        data = df_data.loc[(df_data['MES'] == mm) & (df_data['ANO'] == yy)]
        
        # Extraindo os dias da coluna 'DATE_END'
        days = data['DIA'].tolist()
        
        # As colunas da tabela DataTable
        days_of_week = ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB', 'DOM']
        
        # Se a lista days estiver vazia, pinte tudo de branco
        if not days:
            return [

            ]
        
        # Se a lista days tiver valores, aplique o estilo condicional
        styles = [
            {
                'if': {
                    'column_id': day,
                    'filter_query': f'{{{day}}} = "{d}"'
                },
                'color': 'tomato',
                'fontWeight': 'bold'
            }
            for d in days
            for day in days_of_week
        ]
    except: styles
    

    
    return styles


@app.callback(
    Output('modal-tarefa', 'is_open'),    
    Output('modal-delet', 'is_open'), 

    Input('open-modal-button', 'n_clicks'),
    Input('submit-tarefa', 'n_clicks'),

    
    State('modal-tarefa', 'is_open'),
    State('modal-delet', 'is_open'), 
    State('type_event', 'value'),
    prevent_initial_call=True
)
def toggle_modal(n1, n2, n3, is_open,is_open2, type_event):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    usuario_atual = flask.request.authorization['username']

    base = acesso_banco_sql()
    perm = pd.DataFrame(base)
    filter_add = perm[perm['ADD'] == 'YES']
    usuarios_com_permissao = filter_add['USERNAME'].to_list()

    if  usuario_atual not in usuarios_com_permissao:
        return  is_open,is_open2
    
    else: 
        if changed_id.split('.')[0] == 'open-modal-button':
            return not is_open

        if changed_id.split('.')[0] == 'submit-tarefa' and type_event:
            return  is_open
        
        if changed_id.split('.')[0] == 'modal-delet':
            return  is_open2
    
        if changed_id.split('.')[0] == 'okay-delet' and type_event:
            return  is_open2
        return  is_open,is_open2
    
@app.callback(
    Output('calendar', 'data'),
    Output('calendar', 'active_cell'),
    Output('month', 'data'),
    Output('year', 'data'),
    Output('div-mes', 'children'),
    Output('div-ano', 'children'),

    Input('avancar', 'n_clicks'),
    Input('voltar', 'n_clicks'),
    State('month', 'data'),
    State('year', 'data')
)
def render_calendar_content(botao_avanca, botao_volta, mm, yy):
    changed_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if botao_avanca != None or botao_volta != None:

        if 'avancar' in changed_id:
            mm += 1
            if mm > 12:
                mm = 1
                yy += 1

        elif 'voltar' in changed_id:
            mm -= 1
            if mm < 1:
                mm = 12
                yy -= 1

    
    day, last_day = get_calendar(yy, mm)
    empty_dict = df.to_dict('records')
    days_of_week = ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB', 'DOM']
    c = 0

    for d in range(1, last_day+1):
        empty_dict[c][day] = d

        if d == h and meses[m-1] == meses[mm-1] and y == anos[yy-2000]:
            initial_active_cell = {'row': c, 'column' : (days_of_week.index(day)), 'column_id' : day, 'row_id' : c}
            
        elif meses[m-1] != meses[mm-1] or y != anos[yy-2000]:
            if d == 1:
                initial_active_cell = {'row': c, 'column' : (days_of_week.index(day)), 'column_id' : day, 'row_id' : c}

        day = 'SEG' if days_of_week.index(day) == 6 else days_of_week[days_of_week.index(day) + 1]
        if day == 'SEG':
            c += 1

    
    return empty_dict, initial_active_cell, mm, yy, meses[mm-1], yy


@app.callback(

    Output('required-field-notification', 'children'),
    Output('user_new', 'children'),
    Input('submit-tarefa', 'n_clicks'),
    Input({'type': 'delete_event', 'index': ALL}, 'n_clicks'),

    State('div-data-concatenada', 'children'),
    State('titulo-input', 'value'),
    State('local-input', 'value'),
    State('dep_pref', 'value'),
    State('arr_pref', 'value'),
    State('descricao-input', 'value'),
    State('type_event', 'value'),
    State('radioitems-input', 'value'),
    State('intermediate-data-store', 'data')


)
def update_lista_eventos(n_clicks, delete_clicks, data_conc,  titulo, local, dep_pref, arr_pref, descricao, type_event,prioridade, store_data):
    df = pd.DataFrame(store_data)
    insert = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")



    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        Trusted_Connection='Yes')
    cursor = conn.cursor()
    user = request.authorization['username']

    base = acesso_banco_sql()
    perm = pd.DataFrame(base)
    filter_add = perm[perm['USERNAME'] == user]
    user_name = filter_add['NAME'].iloc[0]

    f = f'Bem vindo, tripulante {user_name}!'
    notificacao = ''

    print(changed_id)

    if 'submit-tarefa' in changed_id:
        if  not titulo or not local or not dep_pref or not arr_pref or not descricao or not type_event or not  prioridade:
            notificacao = 'Por favor, preencha todos os campos obrigatórios.'
            return  notificacao, f
        else:
            titulo = titulo.upper()
            local = local.upper()
            dep_pref = dep_pref.upper()
            arr_pref = arr_pref.upper()
            descricao = descricao.upper()
            type_event = type_event.upper()

            KEY = f"{data_conc}{titulo}{local}{dep_pref}{arr_pref}{type_event}{prioridade}{insert}"
            insert_query = """
                INSERT INTO TB_CALENDER_CCO ([USER], DATE_END, TITLES, PLACE, DEP_PREF, ARR_PREF, DESCRIPTIONS, TYPE, ACION,PRIORIDAD, [KEY], UPDATETIME)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'INSERT', ?, ?, ?)
            """
            cursor.execute(insert_query, user, data_conc, titulo, local, dep_pref, arr_pref, descricao, type_event,  prioridade, KEY, insert)
            conn.commit()
            notificacao = "Evento adicionado com sucesso!"
            conn.close()
            return  notificacao,f
    elif 'okay-delet' in changed_id:
        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        button_data = eval(button_id)
        card_id = button_data['index']
        click = delete_clicks[card_id]
        df_delet = df.loc[(df['id'] == card_id)]

        if click is not None and click > 0:
            df_delet = df.loc[(df['id'] == card_id)]
            user_del =  df_delet['user'].iloc[0]
            data_conc_del =  df_delet['date_end'].iloc[0]
            titulo_del =  df_delet['titles'].iloc[0]
            local_del =  df_delet['place'].iloc[0]
            dep_pref_del =  df_delet['dep_pref'].iloc[0]
            arr_pref_del =  df_delet['arr_pref'].iloc[0]
            descricao_del = df_delet['descriptions'].iloc[0]
            type_event_del =   df_delet['type'].iloc[0]
            prioridade_del =   df_delet['prioridad'].iloc[0]
            KEY_del = f"{data_conc_del}{titulo_del}{local_del}{dep_pref_del}{arr_pref_del}{descricao_del}{type_event_del}"
            delet_query = """
                INSERT INTO TB_CALENDER_CCO ([USER], DATE_END, TITLES, PLACE, DEP_PREF, ARR_PREF, DESCRIPTIONS, TYPE, ACION, PRIORIDAD, [KEY], UPDATETIME)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'DELET', ?, ?, ?)
            """
            cursor.execute(delet_query, user_del, data_conc_del, titulo_del, local_del, dep_pref_del, arr_pref_del, descricao_del, type_event_del, prioridade_del, KEY_del, insert)
            conn.commit()
            notificacao = "Evento excluido com sucesso!"
            conn.close()

            return  notificacao,f


        # Encontrando o card associado pelo ID
        #card = next((card for card in cards_data if card['id'] == card_id), None)

    
    conn.close()
    return notificacao, f
 


@app.callback(
    Output('div-data-concatenada', 'children'),
    Output('div-dia-semana-atual', 'children'),
    Output('div-dia-mês-atual', 'children'),
    Output('card-geral', 'children'),
    Output('intermediate-data-store', 'data'),

    Input('calendar', 'active_cell'),
    Input('lista-de-eventos', 'data'),

    State('calendar', 'data'), 
    State('div-mes', 'children'),
    State('div-ano', 'children'),
    prevent_initial_call=True
)
def update_card_geral(active_cell, lista_de_eventos, calendar_data, mes, ano):  
    dia = calendar_data[active_cell['row']][active_cell['column_id']]
    mes = meses.index(mes) + 1

    if dia == None:
        dia = 1
    
    data_conc = '{:02d}/{:02d}/{:02d}'.format(dia, mes, ano)

    col = active_cell['column_id']    
    if col == 'SEG':
        col = 'Segunda-Feira'
    elif col == 'TER':
        col = 'Terça-Feira'
    elif col == 'QUA':
        col = 'Quarta-Feira'
    elif col == 'QUI':
        col = 'Quinta-Feira'
    elif col == 'SEX':
        col = 'Sexta-Feira'
    elif col == 'SAB':
        col = 'Sábado'
    elif col == 'DOM':
        col = 'Domingo'

    dia_semana_atual = col
    dia_mês_atual = data_conc[:2] 

    
    eventos_dia = [evento for evento in lista_de_eventos if evento['DATE_END'] == data_conc]

    card_tarefa = []
    num_eventos = len(eventos_dia)
    usuario_atual = flask.request.authorization['username']

    base = acesso_banco_sql()
    perm = pd.DataFrame(base)
    filter_add = perm[perm['DEL'] == 'YES']
    usuarios_com_permissao = filter_add['USERNAME'].to_list()
    #usuarios_com_permissao = ["João", "Maria",'000000']
    
    cards_store = []

    
    if num_eventos == 0:
        card_tarefa = dbc.Card(
            [
                dbc.Row(
                    [
                    html.H3('Não há eventos nessa data')
                    ],
                    className="g-0 d-flex align-items-center",
                    style={'margin-top' : '45px'}
                )
            ],
            className="mb-3",
            style={"maxWidth": "540px",
                    'background-color' : '#000000'},
            id='card-tarefa'
        )
        lista_ordenada_de_eventos = []
    else:
        lista_ordenada_de_eventos = sorted(eventos_dia, key=lambda d: d['id'])
  
    for evento in lista_ordenada_de_eventos:

               
        if usuario_atual in usuarios_com_permissao:
            delete_component = dbc.Button(
                [html.I(className="fa fa-trash", style={'font-size': '200%'})],
                id={
                    'type': 'delete_event',
                    'index': evento['id']  # A chave 'id' não estava no exemplo que você deu para 'Dic'. Por favor, ajuste se necessário.
                }
            )
        else:
            delete_component = html.Div()  # Div vazio para manter o layout
    
        new_card = dbc.Card(
            [
                dbc.Row(
                    [
                        dbc.Col(html.H4(evento['TYPE'],
                                        style={'font-weight': 'bold',
                                                'text-align': 'center',
                                                'font-size': '16px'}),
                                width=3),

                        dbc.Col(
                            dbc.CardBody(
                                [
                                    html.H4(f"{evento['TITLES']} {evento['PRIORIDADE']}",
                                            style={'font-weight': 'bold',
                                                    'margin-top': '-10px',
                                                    'font-size': '14px'}),
                                    html.H4(f"Dep/Pref: {evento['DEP_PREF']} - Arr/Pref: {evento['ARR_PREF']}",
                                            style={'font-weight': 'bold',
                                                    'margin-top': '-2px',
                                                    'font-size': '14px'}),
                                    html.P(evento['PLACE'],
                                            style={'margin-top': '-4px',
                                                    'font-size': '12px',
                                                    'color': 'gray'}),
                                    html.P(evento['DESCRIPTIONS']),
                                    html.P(f"Event Creat: {evento['USER']}",
                                            style={'margin-top': '-4px',
                                                    'font-size': '12px',
                                                    'color': 'gray'}),

                                ]
                            ),
                            md=9
                        ),

                        dbc.Col(
                            delete_component,
                            className="col-md-1",
                            md=3
                        ),
                    ],
                    className="g-0 d-flex align-items-center",
                    style={'border-bottom': '1px solid white', }
                )
            ], className="mb-3",
            style={"maxWidth": "540px",
                    'background-color': '#000000'}, )
        card_tarefa.append(new_card)

    for evento in lista_ordenada_de_eventos: 
        card_data = {
            'id': evento['id'],
            'date_end': evento['DATE_END'],
            'type': evento['TYPE'],
            'prioridad': evento['PRIORIDAD'],
            'dep_pref': evento['DEP_PREF'],
            'arr_pref': evento['ARR_PREF'],
            'titles': evento['TITLES'],
            'place': evento['PLACE'],
            'descriptions': evento['DESCRIPTIONS'],
            'user': evento['USER'],
            # Você pode adicionar mais campos, se necessário
        }
        cards_store.append(card_data)
    return data_conc, dia_semana_atual, dia_mês_atual, card_tarefa, cards_store

@app.callback(
    Output('type_event', 'options'),
    Input('modal-tarefa', 'is_open')
)
def update_data(is_open):
    
    if is_open:
       
        
        names = ['CCO Standards','Cargas', 'Clientes VIPs' , 'Delivery/Redelivery', 'Embarques Especiais', 'Eventos' ,'Fretamento', 'Evento','Inauguração de Bases', 'Manuteção','Outros', 'Safety', 'Voos Especiais']
        return [{'label': i, 'value': i} for i in names]
    else:
        raise PreventUpdate
    

@app.callback(
    [Output('offcanvas-backdrop', 'is_open'),
     Output('offcanvas-backdrop', 'children')],
    [Input('open-offcanvas-backdrop', 'n_clicks'),
     Input('lista-de-eventos', 'data')],
    [State('offcanvas-backdrop', 'is_open'),
     State('div-mes', 'children'),
     State('div-ano', 'children')],
    prevent_initial_call=True
)
def update_and_toggle_offcanvas(n_clicks, lista_de_eventos, is_open, mes, ano):  
    # Verifique se o botão foi pressionado
    print(is_open)
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    mes = meses.index(mes) + 1

    # Obtenha os eventos para o mês e ano selecionados
    eventos_do_mes = [evento for evento in lista_de_eventos if int(evento['DATE_END'][3:5]) == mes and int(evento['DATE_END'][6:]) == ano]
    card_tarefa = []

         
                
    # Se não houver eventos no mês selecionado
    if not eventos_do_mes:
        no_event_card = dbc.Card(
            [
                dbc.Row(
                    [
                    html.H3('Não há eventos nesse mês.')
                    ],
                    className="g-0 d-flex align-items-center",
                    style={'margin-top' : '45px'}
                )
            ],
            className="mb-3",
            style={"maxWidth": "1200px", 'background-color' : '#272626'}
        )
        return not is_open, [no_event_card]
    
    # Se houver eventos no mês selecionado
    else:
        for evento in eventos_do_mes:

            new_card = dbc.Card(
                [
                    dbc.Row(
                        [
                            dbc.Col(html.H4(evento['DATE_END'],
                                            style={'font-weight': 'bold',
                                                    'text-align': 'center',
                                                    'font-size': '14px'}),
                                    width=3),

                            dbc.Col(
                                dbc.CardBody(
                                    [
                                        html.H4(f"{evento['TYPE']} {evento['PRIORIDADE']}",
                                                style={'font-weight': 'bold',
                                                        'margin-top': '-10px',
                                                        'font-size': '14px',
                                                        'color': 'tomato',
                                                        'margin-top':'3px'}),
                                                        
                                        html.H4(evento['TITLES'],
                                                style={'font-weight': 'bold',
                                                        'margin-top': '-10px',
                                                        'font-size': '13px',
                                                        'margin-top':'5px'}),

                                        html.H4(f"Dep/Pref: {evento['DEP_PREF']} - Arr/Pref: {evento['ARR_PREF']}",
                                                style={'font-weight': 'bold',
                                                        'margin-top': '-2px',
                                                        'font-size': '12px'}),

                                        html.P(evento['PLACE'],
                                                style={'margin-top': '-4px',
                                                        'font-size': '12px',
                                                        'color': 'gray'}),
                                        html.P(evento['DESCRIPTIONS']),
                                        html.P(f"Event Creat: {evento['USER']}",
                                                style={'margin-top': '-4px',
                                                        'font-size': '10px',
                                                        'color': 'gray'}),

                                    ]
                                ),
                                md=9
                            ),


                        ],
                        className="g-0 d-flex align-items-center",
                        style={'border-bottom': '1px solid white', }
                    )
                ], className="mb-3",
                style={"maxWidth": "1200px",
                       "Width": "1000px",
                        'background-color': '#272626'}, )
            card_tarefa.append(new_card)
        return not is_open, card_tarefa

@app.callback(
    Output('lista-de-eventos', 'data'),
    Output('latest-timestamp', 'children'),
    [Input('modal-tarefa', 'is_open'),
    Input('okay-delet', 'n_clicks'),
    Input('interval-component', 'n_intervals')],
    [State('lista-de-eventos', 'data')],
    prevent_initial_call=True
)
def update_store_data(is_open, delete_clicks, n_intervals, current_data):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    data = delete_clicks
    clean_data = [x if x is not None else 0 for x in data]
    summed_value = sum(clean_data)
    now = datetime.datetime.now()
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    a = f"Last updated: {date_time_str}"
    updated_data = seacher_banco_sql()
    # Se modal-tarefa é fechado, se um evento é deletado, ou se o intervalo é acionado:
    if 'modal-tarefa' in changed_id and not is_open:
        return updated_data, a
 
    elif 'okay-delet' in changed_id and  summed_value > 0:
        return updated_data, a
    
    elif summed_value > 0: 
        return updated_data, a
    
    return dash.no_update, a


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)