import pandas as pd
import pyodbc

#===================================================================================================
def seacher_banco_sql():
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query =  """ select* from (
    select ROW_NUMBER() OVER (PARTITION BY convert(varchar,DATE_END,102) ,year(convert(date,DATE_END,103))  ,	MONTH(convert(date,DATE_END,103))  ,	DAY(convert(date,DATE_END,103)) ,
	  TITLES,	PLACE,	DEP_PREF,	ARR_PREF,	DESCRIPTIONS,	[TYPE],PRIORIDAD ORDER BY DATE_END,[TYPE],ACION) dupl,

    [USER],convert(varchar,DATE_END,102) DATE_END,year(convert(date,DATE_END,103)) ANO ,	MONTH(convert(date,DATE_END,103)) MES ,	DAY(convert(date,DATE_END,103)) DIA,
	  TITLES,	PLACE,	DEP_PREF,	ARR_PREF,	DESCRIPTIONS,	[TYPE],	ACION,PRIORIDAD, [KEY], UPDATETIME from dbo.TB_CALENDER_CCO with(nolock))a

    where dupl =1
    and acion = 'INSERT'"""
    cursor.execute(sql_query)

    resultados = []
    for row in cursor.fetchall():
        USER = row.USER
        DATE_END = row.DATE_END
        TITLES = row.TITLES
        PLACE = row.PLACE
        DEP_PREF = row.DEP_PREF
        ARR_PREF = row.ARR_PREF
        DESCRIPTIONS = row.DESCRIPTIONS
        TYPE = row.TYPE
        ACION = row.ACION
        PRIORIDAD = row.PRIORIDAD
        KEY = row.KEY
        UPDATETIME = row.UPDATETIME
        DIA = row.DIA
        MES = row.MES
        ANO = row.ANO
          # Insira o nome da coluna que você deseja armazenar na variável

        resultados.append((USER, DATE_END, TITLES, PLACE, DEP_PREF, ARR_PREF, DESCRIPTIONS, TYPE, ACION,PRIORIDAD, KEY, UPDATETIME,DIA,MES,ANO))

 #   for USERNAME, PASSWORD, TYPE in resultados:
#        print(f'Coluna1: {coluna1}, Coluna2: {coluna2}')
 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['USER', 'DATE_END', 'TITLES', 'PLACE', 'DEP_PREF', 'ARR_PREF', 'DESCRIPTIONS', 'TYPE', 'ACION', 'PRIORIDAD', 'KEY', 'UPDATETIME','DIA','MES','ANO'])
    df['id'] = df.groupby('DATE_END').cumcount()
    df['id'].astype(int)
    df['PRIORIDADE'] = df['PRIORIDAD'].apply(lambda x: '🔴' if x == "1" else ('🟡' if x == "2" else '🟢'))
    store_data = df.to_dict('records')
    
    return store_data

  #===================================================================================================
def acesso_banco_sql():
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query ="SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN WHERE DEP ='CCO'"
    cursor.execute(sql_query)
    resultados = []
    for row in cursor.fetchall():
        USERNAME = row.USERNAME
        NAME = row.NAME
        PASSWORD = row.PASSWORD
        TYPE = row.TYPE
        EMAIL = row.EMAIL
        DEP = row.DEP
        ADD = row.ADD
        DEL = row.DEL
        VIEW = row.VIEW
          # Insira o nome da coluna que você deseja armazenar na variável

        resultados.append((USERNAME,NAME,PASSWORD,TYPE,EMAIL,DEP,ADD,DEL,VIEW))
 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['USERNAME','NAME','PASSWORD','TYPE','EMAIL','DEP','ADD','DEL','VIEW'])
    store_data = df
    
    return store_data

