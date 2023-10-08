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
from PILOT_app import * 
from PILOT_sql import *
from PILOT_convert import *
import plotly.express as px
import time
# Substitua por suas credenciais e função de busca SQL




style_box={'margin-top':'10px','margin-right':'0px'}
           #'margin-left':'10px','text-align':'center','margin-right':'2px'}

style_font_p={'backgroundColor': 'rgb(26, 61, 114)','color':'white','width':'95px','font-size':'14px'}
style_font={'backgroundColor': 'rgb(26, 61, 114)','color':'white','text-align':'center','font-size':'14px'}

style_profile_p = {'color':'black','margin-top':'0px','borderRadius':'5px','text-align':'center','display':'inline-block','font-size':'14px'}
style_profile = {'color':'black','margin-top':'0px','borderRadius':'5px','text-align':'center'}

PLOTLY_LOGO = "assets/azul-logo.png"
app.title = 'Elevação de Nível'
app.index_string = '''
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


initial_data = global_database()

app.layout = html.Div([
 html.Div([
    dcc.Store(id='data-store', data=initial_data),
      # Inicializar dcc.Store com dados
    dcc.Interval(
        id='interval-component',
        interval=24*60*60000,  # em milissegundos (24 minutos aqui como exemplo)
        n_intervals=0
    ),
]),
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
            dbc.Input(type="search", placeholder="Search", id="search_text"),

            ],
            width={"size": 6, "offset": 2}),
            dbc.Col([
                dbc.Button("Search", color="primary", className="ms-2", n_clicks=0, id='seach_pes')]
            ),
        ]),
    ], className="g-0 ms-auto flex-nowrap mt-3 mt-md-0", align="center"), style={'margin-top': '2%'}),
    html.Div(id='info_search',style={'margin-top': '5px', 'display':'flex','justify-content': 'center','align-items':'center', 'font-size':'10px', 'color':'gray'}),

    html.Div([            dcc.Loading(
                id="loading-1",
                type="default",
                children=    html.Div(id='result_search', style={'margin': '5%'})
            ),],style={'margin top':'20px'}),
            

     dbc.Modal([
        dbc.ModalHeader(id='modal-header'),
        dbc.ModalBody([
             dbc.Row([

                    html.Div(id='modal-body'),

                ]),
        ]),

    ], id="modal", backdrop="static", fullscreen=True, centered=True,scrollable=False),
])
@app.callback(
    Output('data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=True  # Impede que este callback seja disparado na inicialização do aplicativo
)
def update_data(n):
    # Gerar novos dados e atualizar
    new_data = global_database()
    print('etap1')
    return new_data 


@app.callback(
    [Output('info_search', 'children'),Output('result_search', 'children')],
    [Input('seach_pes', 'n_clicks'),Input('data-store', 'data')],
    [State('search_text', 'value')]
)
def import_dados_sql(n_clicks, database, search,):
    table = ''
    if n_clicks > 0:
        
        search_upper = search.upper()

        if not search_upper:
            return 'Insera um NOME ou RE valido'
        
        result = pd.DataFrame(database)
        print('etap2')
        df_result = result
        if result.empty:
            return 'Não localizado, tente novamente'

        # Primeiro, procurar na coluna NOME
        df_result = result[result['NAME'].str.contains(search_upper, na=False)]
    
        # Se nada for encontrado, procurar na coluna RE
        if df_result.empty:
            df_result = result[result['RE'].str.contains(search, na=False)]

        if df_result.empty:
            return '**Não localizado, tente novamente**'
        info = "Click em um nome e aguarde a abertura do cartão do tripulante."
        df_result['NAME'] = df_result['NAME'].apply(lambda x: f"{x}")
        time.sleep(7)
        table = DataTable(
            id='table',
            data=df_result.to_dict('records'),
            columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_result[['RE','NAME','RANK']].columns],
            markdown_options={"link_target": "_blank"},
            style_cell={'textAlign': 'left','fontSize':'15px'},
            sort_action="native",
            style_cell_conditional=[
                {'textAlign': 'left','backgroundColor': 'rgb(220, 220, 220)'}            ],
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
        return info, table
    else:
        return '',''

@app.callback(
    [Output("modal", "is_open"), Output("modal-header", "children"),Output("modal-body", "children")],
    [Input("table", "active_cell")],
    [State("modal", "is_open"), State("table", "data"),State('data-store', 'data')],
    prevent_initial_call=True
)

def toggle_modal(active_cell, is_open, table_data, data_store):
    ctx = dash.callback_context

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    #print(f"Triggered ID: {triggered_id}")

    database_ = pd.DataFrame(data_store)
    database = database_.loc[(database_['RANK'] ==  'FO')]


    if triggered_id == 'close':
        return False, "", None 

    if active_cell and active_cell['column_id'] == 'NAME' :

        clicked_name = table_data[active_cell['row']]['NAME']
        re_value = table_data[active_cell['row']]['RE']
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
 


        linha = active_cell['row']      
        df_data =  pd.DataFrame(table_data)

        df = df_data.iloc[[linha]]




        lista_2 = ['DOCUMENTTYPE', 'DOCUMENTNUMBER','ISSUEDATE', 'EXPIRYDATE', 'VALIDADE', 'STATUS']
        df_tb2 = ajuste_base(df,lista_2)
        df_tb2.rename(columns={'DOCUMENTTYPE': 'DOCUMENTOS', 'DOCUMENTNUMBER': 'TIPO','ISSUEDATE': 'EXPEDIÇÃO','EXPIRYDATE': 'EXPIRAÇÃO'}, inplace=True)
        df_tb2_ = df_tb2[df_tb2['DOCUMENTOS'] != 'BRAZILIAN NATIONAL DOCUMENT']


        lista_3 = ['TIPO', 'ANO', 'DIAS']
        df_tb3_ = ajuste_base(df,lista_3)
        df_tb3 = df_tb3_.sort_values(['TIPO','ANO'],ascending=False)


        lista_4 = ['REPORTES', 'DECADAS', 'QUANTIDADE']
        df_tb4 = ajuste_base(df,lista_4)      
        df_tb4.rename(columns={'DECADAS': 'ANO'}, inplace=True)

        df_tb5 = df[['REPROVA_REGULAMENTO','MEDIA_REGULAMENTOS','QUANT_REPROVACOES_SISTEMAS',
                           'MEDIA_PROVAS_SISTEMAS']].fillna(0)
        df_tb5.rename(columns={ 'REPROVA_REGULAMENTO': 'REPROVA REGULAMENTO',
                               'MEDIA_REGULAMENTOS': 'MÉDIA REGULAMENTOS','QUANT_REPROVACOES_SISTEMAS': 'QUANT REPROVAÇÕES SISTEMAS','MEDIA_PROVAS_SISTEMAS':'MÉDIA PROVAS SISTEMAS'}, inplace=True)
        
        df_tb6 = df[['QUANT_SESSOES','QUANT_REPROVACOES_SIMULADOR']].fillna(0)
        df_tb6.rename(columns={'QUANT_REPROVACOES_SIMULADOR': 'QUANT REPROVAÇÕES SIMULADOR','QUANT_SESSOES':'QUANT SESSÕES'}, inplace=True)
        
        df_tb7 = df[['QNT_REPROVAS_FAO','QUANT_REP_SIST_PSI']].fillna(0)
        df_tb7.rename(columns={'QNT_REPROVAS_FAO': 'QUANT REPROVAS FAO', 'QUANT_REP_SIST_PSI': 'QUANT REP SIST PSI'}, inplace=True)
        try:
            vistob = df_tb2.loc[(df_tb2['DOCUMENTOS'] == 'VISA') & (df_tb2['TIPO'] == 'B1B2')]
            visto_tur = vistob['EXPIRAÇÃO'].iloc[0]
        except:
            visto_tur = '--'
                
        try:
            vistoc = df_tb2.loc[(df_tb2['DOCUMENTOS'] == 'VISA') & (df_tb2['TIPO'] == 'C1D')]
            visto_work = vistoc['EXPIRAÇÃO'].iloc[0]
        except:
            visto_work = '--'

        try:
            passaport_ = df_tb2.loc[(df_tb2['DOCUMENTOS'] == 'PASSPORT') ]
            passaport = passaport_['TIPO'].iloc[0]
        except:
            passaport = '--'

        try:        
            vacina_g = df_tb2.loc[(df_tb2['DOCUMENTOS'] == 'YFV') & (df_tb2['TIPO'] == 'YFV')]
            vacina = vacina_g['VALIDADE'].iloc[0]
        except:
            vacina = '--' 

        try:      
            english = df_tb2.loc[(df_tb2['DOCUMENTOS'] == 'ENGLISH LEVEL ICAO') ]
            english_n = english['TIPO'].iloc[0]
        except:
            english_n = '--'

        
        try:      
            cpf = df_tb2.loc[(df_tb2['DOCUMENTOS'] == 'BRAZILIAN NATIONAL DOCUMENT') ]
            cpf_n = cpf['TIPO'].iloc[0]
        except:
            cpf_n = '--'    
        try: 
            list_ser = ['SENORIDADE']
            
            senoridade_base = ajuste_base(df,list_ser)     


            senoridade = senoridade_base['SENORIDADE'].iloc[0]
        except:
            senoridade = '--'  



  #========================================
  # ==> CONFIGURAÇÃO DOS GRAFICOS BARRA 1
        df_graph_1 = 'ANO_ALUNO','MEDIA_AP','MEDIA_CM','MEDIA_VA','MEDIA_VM','MEDIA_LI','MEDIA_TD','MEDIA_CS','MEDIA_CT','MEDIA_CO'
        df_graph1 = ajuste_base(df,df_graph_1) 
        colunas_fixas1 = ['ANO_ALUNO']  # Definidas fora da função
        grupos_colunas1 = ['MEDIA_AP','MEDIA_CM','MEDIA_VA','MEDIA_VM','MEDIA_LI','MEDIA_TD','MEDIA_CS','MEDIA_CT','MEDIA_CO']
        
        df_graph_1_px = empilhar_colunas(df_graph1, grupos_colunas1, colunas_fixas1)

        fig = px.histogram(df_graph_1_px, x='ANO_ALUNO', y='NOTA',title="MÉDIA POR COMPETÊNCIA",
                    color='TIPO', barmode='group',text_auto='.3s',nbins=20,
                    histfunc='avg',color_discrete_sequence=px.colors.qualitative.Prism,
                    height=200,)
        fig.update_traces(textfont_size=13, textangle=0, textposition="outside", cliponaxis=False)
        fig.update_layout(margin=dict(t=20, b=5, l=5, r=5),
            plot_bgcolor='rgba(255,255,255,1)',  # Fundo branco
            #paper_bgcolor='rgba(255,255,255,1)',  # Fundo do papel branco
            xaxis_title="",  # Remover título do eixo x
            yaxis_title="",  # Remover título do eixo y
            xaxis_showticklabels=True,  # Ocultar rótulos do eixo x
            yaxis_showticklabels=False,  # Ocultar rótulos do eixo y
            xaxis_visible=True,  # Ocultar eixo x
            yaxis_visible=True,  # Ocultar eixo y
            width=1000,  # Largura do gráfico
            height=200,  # Altura do gráfico
            showlegend=True,  # Ocultar legenda
            font=dict(
                size=8,  # Tamanho da fonte dos números
            )
        )
        fig.update_xaxes(showticklabels=True)

  #==========================================> CONFIGURAÇÃO DOS GRAFICOS BARRA 2

        lista_2 = ['ANO_ALUNO','MEDIA_AP','MEDIA_CM','MEDIA_VA','MEDIA_VM','MEDIA_LI','MEDIA_TD','MEDIA_CS','MEDIA_CT','MEDIA_CO']
        df_tb2 = ajuste_base(database,lista_2)

        colunas_fixas2 = ['ANO_ALUNO']  # Definidas fora da função
        grupos_colunas2 = ['MEDIA_AP','MEDIA_CM','MEDIA_VA','MEDIA_VM','MEDIA_LI','MEDIA_TD','MEDIA_CS','MEDIA_CT','MEDIA_CO'] 

        df_graph_2_px = empilhar_colunas(df_tb2, grupos_colunas2, colunas_fixas2)
        df_graph_2_mean = df_graph_2_px.groupby(['ANO_ALUNO','TIPO'])['NOTA'].mean().reset_index()
        df_graph_2_mean2 = pd.DataFrame(df_graph_2_mean)
        fig_cop = px.histogram(df_graph_2_mean2, x='ANO_ALUNO', y='NOTA',title="MÉDIA POR COMPETÊNCIA GRUPO COPILOTOS",
                    color='TIPO', barmode='group',text_auto='.3s',nbins=20,
                    histfunc='avg',color_discrete_sequence=px.colors.qualitative.Prism,
                    height=200,)
        fig_cop.update_traces(textfont_size=13, textangle=0, textposition="outside", cliponaxis=False)
        fig_cop.update_layout(margin=dict(t=20, b=5, l=5, r=5),
            plot_bgcolor='rgba(255,255,255,1)',  # Fundo branco
            #paper_bgcolor='rgba(255,255,255,1)',  # Fundo do papel branco
            xaxis_title="",  # Remover título do eixo x
            yaxis_title="",  # Remover título do eixo y
            xaxis_showticklabels=True,  # Ocultar rótulos do eixo x
            yaxis_showticklabels=False,  # Ocultar rótulos do eixo y
            xaxis_visible=True,  # Ocultar eixo x
            yaxis_visible=True,  # Ocultar eixo y
            width=1000,  # Largura do gráfico
            height=200,  # Altura do gráfico
            showlegend=True,  # Ocultar legenda
            font=dict(
                size=8,  # Tamanho da fonte dos números
            )
        )
        fig_cop.update_xaxes(showticklabels=True)
 
  #==========================================> CONFIGURAÇÃO DOS GRAFICOS LINHA


        lista_3 = ['ANO_PROV', 'MEDIA', 'TIPO_P']
        df_tb3_ = ajuste_base(df,lista_3).sort_values('ANO_PROV')


        fig_line_teo = px.line(df_tb3_, x="ANO_PROV", y="MEDIA",text="MEDIA",title="MÉDIAS TEORICO", color='TIPO_P')
        fig_line_teo.update_traces(textposition="top center",textfont_size=13,)
        fig_line_teo.update_layout(margin=dict(t=20, b=5, l=5, r=5),
                    plot_bgcolor='rgba(255,255,255,1)',  # Fundo branco
                    #paper_bgcolor='rgba(255,255,255,1)',  # Fundo do papel branco
                    xaxis_title="",  # Remover título do eixo x
                    yaxis_title="",  # Remover título do eixo y
                    yaxis_showticklabels=False,  # Ocultar rótulos do eixo y
                    yaxis=dict(
                    range=[df_tb3_['MEDIA'].min()-10, df_tb3_['MEDIA'].max()+10], 
                            ),
                    width=1000,  # Largura do gráfico
                    height=200,
                    font=dict(
                    size=8,  # Tamanho da fonte dos números
                ))


  #==========================================> CONFIGURAÇÃO DOS GRAFICOS LINHA 2
        df_graph_4 = ['ANO_ALUNO','MEDIA_TOTAL']
        df_graph4 = ajuste_base(database,df_graph_4)
        df_graph4_ = df_graph4.groupby('ANO_ALUNO')['MEDIA_TOTAL'].mean().reset_index().round(3)

        fig_line_cop = px.line(df_graph4_, x="ANO_ALUNO", y="MEDIA_TOTAL",text="MEDIA_TOTAL",title="MÉDIA SESSÕES GRUPO COPILOTOS")
        fig_line_cop.update_traces(textposition="top center",textfont_size=13,)
        fig_line_cop.update_layout(margin=dict(t=20, b=5, l=5, r=5),
                    plot_bgcolor='rgba(255,255,255,1)',  # Fundo branco
                    #paper_bgcolor='rgba(255,255,255,1)',  # Fundo do papel branco
                    xaxis_title="",  # Remover título do eixo x
                    yaxis_title="",  # Remover título do eixo y
                    yaxis_showticklabels=False,  # Ocultar rótulos do eixo y
                    yaxis=dict(
                    range=[df_graph4_['MEDIA_TOTAL'].min()-1, df_graph4_['MEDIA_TOTAL'].max()+1], 
                            ),
                            width=1000,  # Largura do gráfico
                            height=200,
                            font=dict(
                    size=8,  # Tamanho da fonte dos números
                ))
  #==========================================> CONFIGURAÇÃO DOS GRAFICOS LINHA 3
        df_graph_5 = ['ANO_ALUNO','MEDIA_TOTAL']
        df_graph5 = ajuste_base(df,df_graph_5)
        df_graph5_ = df_graph5.groupby('ANO_ALUNO')['MEDIA_TOTAL'].mean().reset_index().round(3)

        fig_line = px.line(df_graph5_, x="ANO_ALUNO", y="MEDIA_TOTAL",text="MEDIA_TOTAL",title="MÉDIA SESSÕES")
        fig_line.update_traces(textposition="top center",textfont_size=13,)
        fig_line.update_layout(margin=dict(t=20, b=5, l=5, r=5),
                    plot_bgcolor='rgba(255,255,255,1)',  # Fundo branco
                    #paper_bgcolor='rgba(255,255,255,1)',  # Fundo do papel branco
                    xaxis_title="",  # Remover título do eixo x
                    yaxis_title="",  # Remover título do eixo y
                    yaxis_showticklabels=False,  # Ocultar rótulos do eixo y
                    yaxis=dict(
                    range=[df_graph4_['MEDIA_TOTAL'].min()-0.2, df_graph4_['MEDIA_TOTAL'].max()+0.5], 
                            ),
                            width=1000,  # Largura do gráfico
                            height=200,
                            font=dict(
                    size=8,  # Tamanho da fonte dos números
                ))
        
        vazio = '--'
        if gend_value == 'MALE':
            img_url = rf"assets\male.jpg"
        
        else:
            img_url = rf"assets\female.jpg"  # substitua pelo seu caminho de imagem padrão

        tab1_content = html.Div([
            dbc.Card([
            dbc.Row([
            dbc.Col([            
                html.P([dbc.Card([html.Strong('CANAC: ')],outline=True,style=style_font), f'{anac_value}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Documento: ')],style=style_font), f'{hab_value}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Admissão: ')],style=style_font), f'{azul_value}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Tempo Azul: ')],style=style_font), f'{azuly_value}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Base: ')],style=style_font), f'{base_value}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Senioridade: ')],style=style_font), f'{senoridade}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Extrato de Pesquisa ANAC: ')],style=style_font), dbc.NavLink("LICENÇAS E HABILITAÇÕES",href=f"https://sistemas.anac.gov.br/consultadelicencas/imp_licencas.asp?nf={anac_value}&cpf={cpf_n}",target="_blank",style={'color':'blue'})],style=style_profile),  
                ],
             width=4, style=style_box),
            dbc.Col([            
                html.P([dbc.Card([html.Strong('Aniversário: ')],style=style_font), f'{bith_value}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Idade: ')],style=style_font), f'{year_value}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Genero: ')],style=style_font), f'{gend_value}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Telefone: ')],style=style_font), f'{phone_value}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Email: ')],style=style_font), f'{email_value}'],style=style_profile),],
             width=4, style=style_box), 
            dbc.Col([            
                html.P([dbc.Card([html.Strong('Nível de Inglês: ')],style=style_font), f'{english_n}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Passaporte: ')],style=style_font), f'{passaport}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Visto B1/B2: ')],style=style_font), f'{visto_tur}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Visto C1: ')],style=style_font), f'{visto_work}'],style=style_profile),
                html.P([dbc.Card([html.Strong('Vacina Febre Amarela: ')],style=style_font), f'{vacina}'],style=style_profile),

                ],
             width=4, style=style_box),
                    ]),
                    ],style={'margin-top':"10px",'height':'500px'}),])
        


        tab2_content = html.Div([
            dbc.Card([
    
                html.Div([
                    DataTable(
            id='table2',
            data=df_tb2_.to_dict('records'),
            columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_tb2_.columns],
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
            id='table3',
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
        
        tab5_content = html.Div([
            dbc.Card([
    
                html.Div([
                    DataTable(
            id='table5',
            data=df_tb5.to_dict('records'),
            columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_tb5.columns],
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
            ),            
            dbc.Card([dbc.Row([dcc.Graph(figure=fig_line_teo)],style={'height':'200px'})],style={'margin-top':'5px'}),


                    ], style={'margin-left':'10px','margin-right':'10px','margin-top': '10px'}),
                    ],style={'height':'500px'}),
                    ],style={'margin-top':"10px"})

        tab6_content = html.Div([
            dbc.Card([
    
                html.Div([
                    DataTable(
            id='table6',
            data=df_tb6.to_dict('records'),
            columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_tb6.columns],
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
            ),                    
            

                dbc.Card([dbc.Row([dcc.Graph(figure=fig)],style={'height':'200px'})],style={'margin-top':'5px'}),
                dbc.Card([dbc.Row([dcc.Graph(figure=fig_cop)],style={'height':'200px'})],style={'margin-top':'5px'}),
                dbc.Card([dbc.Row([dcc.Graph(figure=fig_line)],style={'height':'200px'})],style={'margin-top':'5px'}),
                dbc.Card([dbc.Row([dcc.Graph(figure=fig_line_cop)],style={'height':'200px'})],style={'margin-top':'5px'}),

                    
                    ], style={'margin-left':'10px','margin-right':'10px','margin-top': '10px'}),
                    ],style={'height':'920px','width':'1230px'}),
                    ],style={'margin-top':"10px"})
        tab7_content = html.Div([
            dbc.Card([
    
                html.Div([
                    DataTable(
            id='table7',
            data=df_tb7.to_dict('records'),
            columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_tb7.columns],
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
            ),

                    
                    ], style={'margin-left':'10px','margin-right':'10px','margin-top': '10px'}),
                    ],style={'height':'500px','width':'1230px'}),
                    ],style={'margin-top':"10px"})
        
        modal_body_content = dbc.Row([
                dbc.Col([
                    dbc.Card([
                        html.Img(src=img_url, height="200px",width='300px', className="img-fluid rounded-start",style={
                                'display': 'block',
                                'margin-left': 'auto',
                                'margin-right': 'auto',
                                'margin-top': '6px',
                            }),
                        dbc.CardBody([
                        dbc.Row([ html.P([dbc.Card([html.Strong('Tripulante: ')],style=style_font_p), f'{clicked_name}'],style=style_profile_p)]),
                        dbc.Row([dbc.Col([ html.P([dbc.Card([html.Strong('Warname: ')],style=style_font_p), f'{funcao_value}'],style=style_profile_p)], width=6),
                         dbc.Col([html.P([dbc.Card([html.Strong('RE: ')],style=style_font_p), f'{re_value}'],style=style_profile_p)], width=6)]),
                        dbc.Row([dbc.Col([ html.P([dbc.Card([html.Strong('Função: ')],style=style_font_p), f'{adm_value}'],style=style_profile_p)], width=6),
                         dbc.Col([html.P([dbc.Card([html.Strong('Grupo Hab: ')],style=style_font_p), f'{famhab_value}'],style=style_profile_p)], width=6),
                    ]),

                           

                        ], className="card-text" )
                    ],style={'height':'550px'})
                ], width=3),
                dbc.Col([
                    dbc.Tabs([
                            dbc.Tab(tab1_content,label='Dados', tab_id='info_tab'),
                            dbc.Tab(tab2_content,label='Documentos', tab_id='info_tab1'),
                            dbc.Tab(tab3_content,label='Historico Disciplinar', tab_id='info_tab2'),
                            dbc.Tab(tab4_content,label='Reportes', tab_id='info_tab3'),
                            dbc.Tab(tab5_content,label='AVA Teórico', tab_id='info_tab4'),   
                            dbc.Tab(tab6_content,label='AVA Simulador', tab_id='info_tab5'),
                            dbc.Tab(tab7_content,label='Reprova Elevação', tab_id='info_tab6'),                              
                    ], id='tabs', active_tab='info_tab'),
                    html.Div(id='tab_content')
                ], width=9),
            ])

        return True, "Elevação de nivel - Profile", modal_body_content

        

    return is_open, "", None


if __name__ == "__main__":
    app.run_server(debug=True, port=8080)