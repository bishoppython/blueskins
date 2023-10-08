import dash
from dash import Dash, Input, Output, State, callback_context, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import ALL
from dash import html, dcc
import pyodbc
from dash.exceptions import PreventUpdate
import pandas as pd
from dash_table import DataTable
# from app import app
from elevacao.PILOT_app import * 
from elevacao.PILOT_sql import *
#from sql_2 import *
#from sql_3 import *
# Substitua por suas credenciais e função de busca SQL




style_box={'margin-top':'10px','margin-left':'10px','text-align':'center'}

style_font_p={'backgroundColor': 'rgb(26, 61, 114)','color':'white','width':'95px'}
style_font={'color':'rgb(26, 61, 114)' ,'text-align':'center','text-align':'center',}

style_profile_p = {'color':'black','margin-top':'0px','borderRadius':'5px','text-align':'center','display':'inline-block'}
style_profile = {'color':'black','margin-top':'0px','borderRadius':'5px','text-align':'center'}

PLOTLY_LOGO = "assets/azul-logo.png"
pilot.title = 'Calculo Matriz'
pilot.index_string = '''
<!DOCTYPE html>
<html lang="pt-BR">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

perfile = seacher_banco_sql()
document = document_inicial()
elevacao = matriz_elevacao_inicial()
treinamento = comp_sessao_aluno()
medias = media_ano_aluno()
medias_geral = media_geral_aluno()

# Unindo todos os DataFrames pela chave "RE"



pilot.layout = html.Div([

 dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="40px")),
                    ],
                    align="center",
                    className="g-0",
                ),
           
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]
    ),
    color="info",
    dark=True,
),
    html.Div(dbc.Row([
        dbc.Row([dbc.Col([
            dbc.Input(type="search", placeholder="Search", id="search_text")],
            width={"size": 6, "offset": 2}),
            dbc.Col([
                dbc.Button("Search", color="primary", className="ms-2", n_clicks=0, id='seach_pes')]
            ),
        ]),
    ], className="g-0 ms-auto flex-nowrap mt-3 mt-md-0", align="center"), style={'margin-top': '2%'}),
    html.Div(id='result_search', style={'margin': '5%'}),
     dbc.Modal([
        dbc.ModalHeader(id='modal-header'),
        dbc.ModalBody(id='modal-body'),

    ], id="modal", backdrop="static", fullscreen=True, centered=True,scrollable=False),
])

@app.callback(
   Output('result_search', 'children'),
    [Input('seach_pes', 'n_clicks')],
    [State('search_text', 'value')]
)
def import_dados_sql(n_clicks, search):
    if n_clicks > 0:
        search_upper = search.upper()
        perfil = seacher_banco_sql()
        elevacao = matriz_elevacao_inicial()
        document_inicial = document_inicial()
        treinamento = comp_sessao_aluno()

        result = perfil.merge(document_inicial, on='RE', how='left')\
        .merge(elevacao, on='RE', how='left')\
        .merge(treinamento, on='RE', how='left')

        df_result = result


        if result.empty:
            return 'Sem resultados'

        # Primeiro, procurar na coluna NOME
        df_result = result[result['NAME'].str.contains(search_upper, na=False)]


        # Se nada for encontrado, procurar na coluna RE
        if df_result.empty:
            df_result = result[result['RE'].str.contains(search, na=False)]

        if df_result.empty:
            return 'Sem resultados'

        df_result['NAME'] = df_result['NAME'].pilotly(lambda x: f"{x}")
        
        return DataTable(
            id='table',
            data=df_result.to_dict('records'),
            columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_result[['RE','NAME','RANK']].columns],
            markdown_options={"link_target": "_blank"},
            style_cell={'textAlign': 'left'},
            sort_action="native",
            style_cell_conditional=[
                {'textAlign': 'left','backgroundColor': 'rgb(220, 220, 220)'}            ],
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'textAlign': 'left',
            },
            style_header={
                'backgroundColor': 'rgb(26, 61, 114)',
                    'color': 'white',
                
            },
            style_as_list_view=True,
            )
       
    else:
        return ''

@app.callback(
    [Output("modal", "is_open"), Output("modal-header", "children"), Output("modal-body", "children")],
    [Input("table", "active_cell")],
    [State("modal", "is_open"), State("table", "data")],
     #,State("data-store", "data")],
    prevent_initial_call=True
)

def toggle_modal(active_cell, is_open, table_data):

    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    print(f"Triggered ID: {triggered_id}")
    re_recib = table_data[active_cell['row']]['RE']
    print(f"re: {re_recib}")
    document = document_inicial()
    document1 = document[document['RE'] == re_recib	]
    print(document1)
    print(document)
    print(re_recib)
    if triggered_id == 'close':
        return False, "", None 
        
    if active_cell:
        
        if active_cell['column_id'] == 'NAME':
            re_recib = table_data[active_cell['row']]['RE']
    

            re_value = table_data[active_cell['row']]['RE']
            clicked_name = table_data[active_cell['row']]['NAME']
            funcao_value = table_data[active_cell['row']]['WARNAME']
            adm_value = table_data[active_cell['row']]['RANK']
            hab_value = table_data[active_cell['row']]['FLEET']
            famhab_value = table_data[active_cell['row']]['FLEET_FAMILY']
            bith_value = table_data[active_cell['row']]['BIRTHDATE']
            year_value = table_data[active_cell['row']]['BIRTHE']
            azul_value = table_data[active_cell['row']]['EFFECTIVEDATE']        
            azuly_value = table_data[active_cell['row']]['YEAR_AZUL']
            base_value = table_data[active_cell['row']]['BASE']  
            phone_value = table_data[active_cell['row']]['PHONE']   
            email_value = table_data[active_cell['row']]['EMAIL']  
            gend_value = table_data[active_cell['row']]['GENDER']  
            anac_value = table_data[active_cell['row']]['CANAC']  

            #img_url = rf"assets\{re_value}.png"
            df = pd.DataFrame(table_data)

            print(df)                 
            
            df_tb2 = document1[['DOCUMENTTYPE','ISSUEDATE','EXPIRYDATE','VALIDAD']].drop_duplicates().sort_values('DOCUMENTTYPE')
            df_tb3 = df[['QUANT_REPORTES','QUNT_FALTA_N_JUSTIFICADA','ENTROU_NO_INSS']].drop_duplicates()
            df_tb4 = df[['DATA','SESSAO','TIPO_TREINAMENTO','AP','CM','VA','VM','LI','TD','CS','CT','CO','MEDIA_ALUNO']].drop_duplicates().sort_values(['DATA','SESSAO'],ascending = False)
           # df_tb5 = medias_df[['ANO_ALUNO','MEDIA_AP','MEDIA_CM','MEDIA_VA','MEDIA_VM','MEDIA_LI','MEDIA_TD','MEDIA_CS','MEDIA_CT','MEDIA_CO','MEDIA_TOTAL']].drop_duplicates().sort_values('ANO_ALUNO',ascending = False)
          #  df_tb6 = medias_geral_df[['RE','MEDIA_AP_G','MEDIA_CM_G','MEDIA_VA_G','MEDIA_VM_G','MEDIA_LI_G','MEDIA_TD_G','MEDIA_CS_G','MEDIA_CT_G','MEDIA_CO_G','MEDIA_TOTAL_G']].drop_duplicates()
            
            if gend_value == 'MALE':
                img_url = rf"assets\male.jpg"
           
            else:
                img_url = rf"assets\female.jpg"  # substitua pelo seu caminho de imagem padrão

            tab1_content = html.Div([
                dbc.Card([
                dbc.Row([
                dbc.Col([            
                    html.P([dbc.Card([html.Strong('CANAC: ')],outline=True,style=style_font), f'{anac_value}'],style=style_profile),
                    html.P([dbc.Card([html.Strong('Habilitação: ')],style=style_font), f'{hab_value}'],style=style_profile),
                    html.P([dbc.Card([html.Strong('Admissão: ')],style=style_font), f'{azul_value}'],style=style_profile),
                    html.P([dbc.Card([html.Strong('Tempo Azul: ')],style=style_font), f'{azuly_value}'],style=style_profile),
                    html.P([dbc.Card([html.Strong('Base: ')],style=style_font), f'{base_value}'],style=style_profile),],
                width=4, style=style_box),
                dbc.Col([            
                    html.P([dbc.Card([html.Strong('Aniversário: ')],style=style_font), f'{bith_value}'],style=style_profile),
                    html.P([dbc.Card([html.Strong('Idade: ')],style=style_font), f'{year_value}'],style=style_profile),
                    html.P([dbc.Card([html.Strong('Genero: ')],style=style_font), f'{gend_value}'],style=style_profile),
                    html.P([dbc.Card([html.Strong('Telefone: ')],style=style_font), f'{phone_value}'],style=style_profile),
                    html.P([dbc.Card([html.Strong('Email: ')],style=style_font), f'{email_value}'],style=style_profile),],
                width=4, style=style_box), 
                        ]),
                        ],style={'margin-top':"10px",'height':'500px'}),])
            
            tab2_content = html.Div([
                dbc.Card([
        
                    html.Div([
                        DataTable(
                id='table2',
                data=df_tb2.to_dict('records'),
                columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_tb2.columns],
                markdown_options={"link_target": "_blank"},
                style_cell={'textAlign': 'left','fontSize':'14px'},
                sort_action="native",
                style_cell_conditional=[
                    {'textAlign': 'left',
                    # 'backgroundColor': 'rgb(220, 220, 220)'
                    }            ],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                
                },
                style_header={
                    'backgroundColor': 'rgb(26, 61, 114)',
                        'color': 'white',
                    
                },
                style_as_list_view=True,
                )
                        
                        ], style={'margin-left':'10px','margin-right':'10px','margin-top': '10px'}),
                        ],style={'height':'500px'}),
                        ],style={'margin-top':"10px"})
            
            tab3_content = html.Div([
                            dbc.Card([
                    
                                html.Div([
                                    DataTable(
                            id='table3',
                            data=df_tb3.to_dict('records'),
                            columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_tb3.columns],
                            markdown_options={"link_target": "_blank"},
                            style_cell={'textAlign': 'left','fontSize':'14px'},
                            sort_action="native",
                            style_cell_conditional=[
                                {'textAlign': 'left',
                                # 'backgroundColor': 'rgb(220, 220, 220)'
                                }            ],
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto',
                            
                            },
                            style_header={
                                'backgroundColor': 'rgb(26, 61, 114)',
                                    'color': 'white',
                                
                            },
                            style_as_list_view=True,
                            )
                                    
                                    ], style={'margin-left':'10px','margin-right':'10px','margin-top': '10px'}),
                                    ],style={'height':'500px'}),
                                    ],style={'margin-top':"10px"})
            tab4_content = html.Div([
                            dbc.Card([
                    
                                html.Div([
                                    DataTable(
                            id='table4',
                            data=df_tb4.to_dict('records'),
                            columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_tb4.columns],
                            markdown_options={"link_target": "_blank"},
                            style_cell={'textAlign': 'left','fontSize':'14px'},
                            sort_action="native",
                            style_cell_conditional=[
                                {'textAlign': 'left',
                                # 'backgroundColor': 'rgb(220, 220, 220)'
                                }            ],
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto',
                            
                            },
                            style_header={
                                'backgroundColor': 'rgb(26, 61, 114)',
                                    'color': 'white',
                                
                            },
                            style_as_list_view=True,
                            )
                                    
                                    ], style={'margin-left':'10px','margin-right':'10px','margin-top': '10px'}),
                                    ],style={'height':'500px'}),
                                    ],style={'margin-top':"10px"})
           

            modal_body_onctent = dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.Img(src=img_url, height="200px",width='300px', className="img-fluid rounded-start",style={
                                    'display': 'block',
                                    'margin-left': 'auto',
                                    'margin-right': 'auto',
                                    'margin-top': '6px',
                                }),
                            dbc.CardBody([
                                html.P([dbc.Card([html.Strong('Tripulante: ')],style=style_font_p), f'{clicked_name}'],style=style_profile_p),
                                html.P([dbc.Card([html.Strong('Warname: ')],style=style_font_p), f'{funcao_value}'],style=style_profile_p),
                                html.P([dbc.Card([html.Strong('RE: ')],style=style_font_p), f'{re_value}'],style=style_profile_p),
                                html.P([dbc.Card([html.Strong('Função: ')],style=style_font_p), f'{adm_value}'],style=style_profile_p),
                                html.P([dbc.Card([html.Strong('Grupo Hab: ')],style=style_font_p), f'{famhab_value}'],style=style_profile_p),
                            ], className="card-text" )
                        ],style={'height':'550px'})
                    ], width=3),
                    dbc.Col([
                        dbc.Tabs([
                            dbc.Tab(tab1_content,label='Dados', tab_id='info_tab'),
                            dbc.Tab(tab2_content,label='Habilitação', tab_id='Hab_tab'),
                            dbc.Tab(tab3_content,label='Reportes', tab_id='Rep_tab'),
                            dbc.Tab(tab4_content,label='Competências', tab_id='Rep1_tab'),
                            dbc.Tab(tab4_content,label='Média Anual', tab_id='Rep2_tab'),
                            dbc.Tab(tab4_content,label='Média Geral', tab_id='Rep3_tab'),
                            dbc.Tab(tab3_content,label='Reportes', tab_id='Rep4_tab'),
                        ], id='tabs', active_tab='info_tab'),
                        html.Div(id='tab_content')
                    ], width=9),
                ])

        return True, "Elevação de nivel - Profile",modal_body_onctent
    return is_open, "", ""


if __name__ == "__main__":
    pilot.run_server(debug=True, port=8080)