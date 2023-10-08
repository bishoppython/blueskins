import pandas as pd
from PILOT_sql import *
# Criando um DataFrame de exemplo

def acesso_banco_sql():
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query ="SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN"
    cursor.execute(sql_query)

    resultados = []
    for row in cursor.fetchall():
        USERNAME = row.USERNAME
        NAME = row.NAME  # Insira o nome da coluna que você deseja armazenar na variável
        PASSWORD = row.PASSWORD
        TYPE = row.TYPE
        EMAIL = row.EMAIL  # Insira o nome da coluna que você deseja armazenar na variável


        resultados.append((USERNAME,NAME,PASSWORD,TYPE,EMAIL))

 #   for USERNAME, PASSWORD, TYPE in resultados:
#        print(f'Coluna1: {coluna1}, Coluna2: {coluna2}')
 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['USERNAME','NAME', 'PASSWORD', 'TYPE','EMAIL'])
    key = pd.DataFrame(df)

  #===================================================================================================
def conversor_sql_(database):
    df = database

    # Agrupando por 'chave'
    grouped = df.groupby('RE').apply(lambda x: x.drop('RE', axis=1).reset_index(drop=True)).reset_index()

    # Reshaping o DataFrame para ter uma coluna única para cada combinação de chave e valor
    reshaped_df = grouped.pivot(index='RE', columns='level_1')

    # Renomeando as colunas para facilitar a identificação
    reshaped_df.columns = [f"{col[0]}_{col[1]+1}" for col in reshaped_df.columns]

    # Resetando o índice para tornar 'chave' uma coluna novamente
    reshaped_df.reset_index(inplace=True)
    store_data = pd.DataFrame(reshaped_df)

    return store_data

  #===================================================================================================
def ajuste_base(base,lista):
    def empilhar_colunas(df, nomes_base):
        df_final = pd.DataFrame()
        
        for nome_base in nomes_base:
            # Encontre todas as colunas que começam com o nome_base
            colunas_selecionadas = [col for col in df.columns if col.startswith(nome_base)]
            colunas_selecionadas.sort()
            
            # Empilhe os valores dessas colunas em uma única coluna
            df_temp = df.melt(id_vars=[], value_vars=colunas_selecionadas, value_name=f"{nome_base}")\
                    .drop(columns=['variable'])\
                    .reset_index(drop=True)
            
            # Adicione ao DataFrame final
            if df_final.empty:
                df_final = df_temp
            else:
                df_final = pd.concat([df_final, df_temp[f"{nome_base}"]], axis=1)


        return df_final


    # Empilhar as colunas correspondentes
    df_final = empilhar_colunas(base, lista)
    df = pd.DataFrame(df_final).dropna()
    return df


  #===================================================================================================
def global_database():
        profile = seacher_banco_sql()
        document = conversor_sql_(document_inicial())
        reports = conversor_sql_(inss_dm_abs_aluno())
        medias = conversor_sql_(media_ano_aluno())
        media_geral = conversor_sql_(media_geral_aluno())
        hist_disc = conversor_sql_(hist_disc_aluno())    
        avaliacao = elevacao_inicial()
        senoridade = conversor_sql_(senoridade_inicial())
        sessoes = sessoes_inicial()
        teorica = conversor_sql_(media_teorica())
        

        result = profile.merge(document,on='RE', how='left').merge(medias, on='RE', how='left').merge(media_geral, on='RE', how='left').merge(reports,  on='RE', how='left').merge(hist_disc,  on='RE', how='left').merge(avaliacao,  on='RE', how='left').merge(senoridade,  on='RE', how='left').merge(sessoes,  on='RE', how='left').merge(teorica,  on='RE', how='left')      
        df = result.to_dict('records')
        print('store-func')
        return df
  #===================================================================================================


def empilhar_colunas(df, grupos_colunas, colunas_fixas):
    df_final = pd.DataFrame()

    for col in grupos_colunas:
        df_temp = df[colunas_fixas + [col]].copy()
        df_temp['TIPO'] = col
        df_temp.rename(columns={col: 'NOTA'}, inplace=True)

        # Adicione ao DataFrame final
        df_final = pd.concat([df_final, df_temp], axis=0).reset_index(drop=True)

    return df_final