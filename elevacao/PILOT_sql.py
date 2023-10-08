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
    sql_query =  """SELECT DISTINCT [NAME],cast(RE as varchar) RE,WARNAME,BIRTHDATE,EFFECTIVEDATE,EMAIL,PHONE,GENDER,CANAC,RANK,FLEET,FLEET_FAMILY,BASE,
        concat(FLOOR(DATEDIFF(DAY, CONVERT(varchar,BIRTHDATE, 103), GETDATE()) / 365.25),',',FLOOR((DATEDIFF(DAY, CONVERT(varchar,BIRTHDATE, 103), GETDATE()) % 365.25) / 30)) AS BIRTHE 
        ,concat(FLOOR(DATEDIFF(DAY, CONVERT(varchar,EFFECTIVEDATE, 103), GETDATE()) / 365.25),',',FLOOR((DATEDIFF(DAY, CONVERT(varchar,EFFECTIVEDATE, 103), GETDATE()) % 365.25) / 30)) AS YEAR_AZUL
        FROM  [DWINTELIGENCIA].[ELEVACAO].[TB_MATRIZ_ELEVACAO_DADOS] WITH (NOLOCK)

		WHERE RANK IN ('CA','FO','IN')
        """
    cursor.execute(sql_query)

    resultados = []
    for row in cursor.fetchall():
        NAME = row.NAME
        RE = row.RE
        WARNAME = row.WARNAME
        BIRTHDATE = row.BIRTHDATE
        EFFECTIVEDATE = row.EFFECTIVEDATE
        EMAIL = row.EMAIL
        PHONE = row.PHONE
        GENDER = row.GENDER
        CANAC = row.CANAC
        RANK = row.RANK
        FLEET = row.FLEET
        FLEET_FAMILY = row.FLEET_FAMILY
        BASE = row.BASE
        BIRTHE = row.BIRTHE
        YEAR_AZUL = row.YEAR_AZUL

          # Insira o nome da coluna que você deseja armazenar na variável
  


        resultados.append((NAME, RE, WARNAME, BIRTHDATE, EFFECTIVEDATE, EMAIL, PHONE, GENDER, CANAC, RANK, FLEET, FLEET_FAMILY, BASE, BIRTHE, YEAR_AZUL
))

 #   for USERNAME, PASSWORD, TYPE in resultados:
#        print(f'Coluna1: {coluna1}, Coluna2: {coluna2}')
 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['NAME', 'RE', 'WARNAME', 'BIRTHDATE', 'EFFECTIVEDATE', 'EMAIL', 'PHONE', 'GENDER', 'CANAC', 'RANK', 'FLEET', 'FLEET_FAMILY', 'BASE', 'BIRTHE', 'YEAR_AZUL'])
    df['RE'] = df['RE'].astype(str)
    store_data = df.replace('nan','0')
    
    return store_data

    #===================================================================================================


    #===================================================================================================
def document_inicial():
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query ="""SELECT  RE,DOCUMENTTYPE,DOCUMENTNUMBER,ISSUEDATE,EXPIRYDATE,VALIDADE from (SELECT  CASE WHEN ROW_NUMBER() OVER ( PARTITION BY RE,DOCUMENTTYPE ORDER BY ISSUEDATE desc) = 1 AND DOCUMENTTYPE ='BRAZILIAN NATIONAL DOCUMENT' THEN 1 
 WHEN ROW_NUMBER() OVER ( PARTITION BY RE,DOCUMENTTYPE,DOCUMENTNUMBER ORDER BY ISSUEDATE desc) = 1  AND DOCUMENTTYPE !='BRAZILIAN NATIONAL DOCUMENT' THEN 1
WHEN DOCUMENTTYPE ='BRAZILIAN NATIONAL DOCUMENT' THEN 2
ELSE 2 END VALIDADOR,
	
	RE, UPPER( DOCUMENTTYPE) DOCUMENTTYPE
            ,REPLACE(REPLACE(CASE WHEN DOCUMENTNUMBER like '%C_D%' THEN 'C1D' 
            WHEN DOCUMENTNUMBER like '%B1B2%' THEN 'B1B2' 
            WHEN DOCUMENTNUMBER like '%YFV%' THEN 'YFV' 

            ELSE DOCUMENTNUMBER END ,'.',''),'-','') DOCUMENTNUMBER,
            ISSUEDATE, EXPIRYDATE,
                    CASE WHEN CAST(EXPIRYDATE AS DATE)>= GETDATE() THEN 'SIM' ELSE 'NÃO' END VALIDADE 
                    FROM [DWINTELIGENCIA].[Trip].[TB_CREW_DOCUMENTTYPE_FULL]
        WHERE DOCUMENTTYPE  NOT IN ( 'ANAC Website PC','ANAC Website PLA','ANAC code','IFR License','IFR License')) A

		WHERE VALIDADOR = 1"""
    cursor.execute(sql_query)

    resultados = []
    for row in cursor.fetchall():
        RE = row.RE # Insira o nome da coluna que você deseja armazenar na variável
        DOCUMENTTYPE = row.DOCUMENTTYPE
        DOCUMENTNUMBER = row.DOCUMENTNUMBER
        ISSUEDATE = row.ISSUEDATE
        EXPIRYDATE = row.EXPIRYDATE
        VALIDADE = row.VALIDADE


        resultados.append((RE,DOCUMENTTYPE,DOCUMENTNUMBER,ISSUEDATE,EXPIRYDATE,VALIDADE))

    conn.commit()
    conn.close()

    df = pd.DataFrame(resultados, columns=['RE','DOCUMENTTYPE','DOCUMENTNUMBER','ISSUEDATE','EXPIRYDATE','VALIDADE'])
    df['STATUS'] = df['VALIDADE'].apply(lambda x: '✔️' if x == "SIM" else '❌')
    df['RE'] = df['RE'].astype(str)
    store_data = df.replace('nan','0')
    return store_data

    #===================================================================================================
def comp_sessao_aluno():
    
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query ="""SELECT RE,cast(CONCAT(YEAR(CONVERT(DATE, DATA, 103)),'-',FORMAT(MONTH(CONVERT(DATE, DATA, 103)),'00'),'-',FORMAT(DAY(CONVERT(DATE, DATA, 103)),'00')) as date) DATA
    ,SESSAO,TIPO_TREINAMENTO,AP,CM,VA,VM,LI,TD,CS,CT,CO,MEDIA_ALUNO FROM [DWINTELIGENCIA].[ELEVACAO].[TB_MATRIZ_COMP_SESSAO_ALUNO] WITH (NOLOCK)"""
    cursor.execute(sql_query)

    resultados = []
    for row in cursor.fetchall():
        RE = row.RE # Insira o nome da coluna que você deseja armazenar na variável
        DATA = row.DATA
        SESSAO = row.SESSAO
        TIPO_TREINAMENTO = row.TIPO_TREINAMENTO
        AP = row.AP
        CM = row.CM
        VA = row.VA
        VM = row.VM
        LI = row.LI
        TD = row.TD
        CS = row.CS
        CT = row.CT
        CO = row.CO
        MEDIA_ALUNO = row.MEDIA_ALUNO


        resultados.append((RE,DATA,SESSAO,TIPO_TREINAMENTO,AP,CM,VA,VM,LI,TD,CS,CT,CO,MEDIA_ALUNO))


 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['RE','DATA','SESSAO','TIPO_TREINAMENTO','AP','CM','VA','VM','LI','TD','CS','CT','CO','MEDIA_ALUNO'])
    df['RE'] = df['RE'].astype(str)
    store_data = df.replace('nan','0')
    return store_data
  #===================================================================================================
def media_ano_aluno():
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query ="""SELECT RE,ANO_ALUNO,MEDIA_AP,MEDIA_CM,MEDIA_VA,MEDIA_VM,MEDIA_LI,MEDIA_TD,MEDIA_CS,MEDIA_CT,MEDIA_CO,MEDIA_TOTAL FROM 
    [DWINTELIGENCIA].[ELEVACAO].[TB_MATRIZ_MEDIA_ANO_ALUNO] WITH (NOLOCK) """
    cursor.execute(sql_query)

    resultados = []
    for row in cursor.fetchall():
        RE = row.RE
        ANO_ALUNO = row.ANO_ALUNO
        MEDIA_AP = row.MEDIA_AP
        MEDIA_CM = row.MEDIA_CM
        MEDIA_VA = row.MEDIA_VA
        MEDIA_VM = row.MEDIA_VM
        MEDIA_LI = row.MEDIA_LI
        MEDIA_TD = row.MEDIA_TD
        MEDIA_CS = row.MEDIA_CS
        MEDIA_CT = row.MEDIA_CT
        MEDIA_CO = row.MEDIA_CO
        MEDIA_TOTAL = row.MEDIA_TOTAL


        resultados.append((RE,ANO_ALUNO,MEDIA_AP,MEDIA_CM,MEDIA_VA,MEDIA_VM,MEDIA_LI,MEDIA_TD,MEDIA_CS,MEDIA_CT,MEDIA_CO,MEDIA_TOTAL))


 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['RE','ANO_ALUNO','MEDIA_AP','MEDIA_CM','MEDIA_VA','MEDIA_VM','MEDIA_LI','MEDIA_TD','MEDIA_CS','MEDIA_CT','MEDIA_CO','MEDIA_TOTAL'])
    df['RE'] = df['RE'].astype(str)
    store_data = df.replace('nan','0')
    return store_data

  #===================================================================================================
def media_geral_aluno():
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query ="""SELECT RE,MEDIA_AP MEDIA_AP_G,MEDIA_CM MEDIA_CM_G,MEDIA_VA MEDIA_VA_G,MEDIA_VM 
        MEDIA_VM_G,MEDIA_LI MEDIA_LI_G,MEDIA_TD MEDIA_TD_G,MEDIA_CS MEDIA_CS_G,MEDIA_CT MEDIA_CT_G,MEDIA_CO MEDIA_CO_G,MEDIA_TOTAL MEDIA_TOTAL_G
        FROM [DWINTELIGENCIA].[ELEVACAO].[TB_MATRIZ_COMP_MEDIA_ALUNO] WITH (NOLOCK)"""
    cursor.execute(sql_query)

    resultados = []
    for row in cursor.fetchall():
        RE = row.RE
        MEDIA_AP_G = row.MEDIA_AP_G
        MEDIA_CM_G = row.MEDIA_CM_G
        MEDIA_VA_G = row.MEDIA_VA_G
        MEDIA_VM_G = row.MEDIA_VM_G
        MEDIA_LI_G = row.MEDIA_LI_G
        MEDIA_TD_G = row.MEDIA_TD_G
        MEDIA_CS_G = row.MEDIA_CS_G
        MEDIA_CT_G = row.MEDIA_CT_G
        MEDIA_CO_G = row.MEDIA_CO_G
        MEDIA_TOTAL_G = row.MEDIA_TOTAL_G


        resultados.append((RE,MEDIA_AP_G,MEDIA_CM_G,MEDIA_VA_G,MEDIA_VM_G,MEDIA_LI_G,MEDIA_TD_G,MEDIA_CS_G,MEDIA_CT_G,MEDIA_CO_G,MEDIA_TOTAL_G))


 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['RE','MEDIA_AP_G','MEDIA_CM_G','MEDIA_VA_G','MEDIA_VM_G','MEDIA_LI_G','MEDIA_TD_G','MEDIA_CS_G','MEDIA_CT_G','MEDIA_CO_G','MEDIA_TOTAL_G'])
    df['RE'] = df['RE'].astype(str)
    store_data = df.replace('nan','0')
    return store_data

  #===================================================================================================

def converor_sql_(database):
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
def inss_dm_abs_aluno():
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query ="""(SELECT  RE, TIPO, CAST(YEAR(DATA_INICIAL)AS VARCHAR) AS ANO, COUNT(DIAS_AFASTADO) AS DIAS
        FROM (SELECT DISTINCT 'INSS' AS TIPO,DATA_INICIAL,DIAS_AFASTADO,RE
        FROM [DWINTELIGENCIA].[ELEVACAO].[TB_MATRIZ_ELEVACAO_INSS] WITH (NOLOCK))A
        WHERE DATA_INICIAL IS NOT NULL
        GROUP BY RE, TIPO,CAST(YEAR(DATA_INICIAL)AS VARCHAR))


        UNION ALL

        (SELECT  RE, TIPO, CAST(YEAR([DATA_FNJ])AS VARCHAR) AS ANO, COUNT([QUNT_FALTA_N_JUSTIFICADA]) AS DIAS
        FROM (SELECT DISTINCT 'FALTA INJUSTIFICADO' AS TIPO,[DATA_FNJ],[QUNT_FALTA_N_JUSTIFICADA],RE
        FROM [DWINTELIGENCIA].[ELEVACAO].[TB_MATRIZ_ELEVACAO_INICIAL_DADOS] WITH (NOLOCK))A
        WHERE [DATA_FNJ] IS NOT NULL
        GROUP BY RE, TIPO,CAST(YEAR([DATA_FNJ])AS VARCHAR))
        
        		        UNION ALL

        (SELECT  RE, TIPO, CAST(YEAR([DATA_DM])AS VARCHAR) AS ANO, COUNT([QUANT_DM]) AS DIAS
        FROM (SELECT DISTINCT 'DISPENSA MÉDICA' AS TIPO,[DATA_DM],[QUANT_DM],RE
        FROM [DWINTELIGENCIA].[ELEVACAO].[TB_MATRIZ_ELEVACAO_INICIAL_DADOS]  WITH (NOLOCK))A
        WHERE [DATA_DM] IS NOT NULL

        GROUP BY RE, TIPO,CAST(YEAR([DATA_DM])AS VARCHAR))
        """
    cursor.execute(sql_query)

    resultados = []
    for row in cursor.fetchall():
        RE = row.RE
        TIPO = row.TIPO
        ANO = row.ANO
        DIAS = row.DIAS
        resultados.append((RE,TIPO,ANO,DIAS))


 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['RE','TIPO','ANO','DIAS'])
    df['RE'] = df['RE'].astype(str)
    store_data = df.replace('nan','0')
    return store_data
  #===================================================================================================
def hist_disc_aluno():
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query ="""
        (SELECT DISTINCT RE,SUM(QUANTIDADE) QUANTIDADES, CAST(YEAR(DTA) AS VARCHAR) DECADAS , UPPER(REPORTES) REPORTES
        FROM(SELECT DISTINCT RE, CAST(QUANT_REPORTES AS INT) QUANTIDADE, CONVERT(DATE,[DATA_REPORTES],103) DTA, TIPO_REPORTES AS REPORTES
        FROM [DWINTELIGENCIA].[ELEVACAO].[TB_MATRIZ_ELEVACAO_INICIAL_DADOS] WITH (NOLOCK)) A
        GROUP BY RE, CAST(YEAR(DTA) AS VARCHAR),REPORTES
        HAVING SUM(QUANTIDADE) IS NOT NULL)

        UNION

        (SELECT DISTINCT RE,SUM(QUANTIDADE) QUANTIDADE, CAST(YEAR(DTA) AS VARCHAR) ANO, UPPER([ELOGIOS_AGRADECIMENTOS]) ELOGIOS_AGRADECIMENTOS
        FROM(SELECT DISTINCT RE, CAST(QUANT_ELOGIOS AS INT) QUANTIDADE, CONVERT(DATE,[DATA_ELOGIOS],103) DTA, [ELOGIOS_AGRADECIMENTOS] 
        FROM [DWINTELIGENCIA].[ELEVACAO].[TB_MATRIZ_ELEVACAO_INICIAL_DADOS] WITH (NOLOCK)) A
        GROUP BY RE, CAST(YEAR(DTA) AS VARCHAR),[ELOGIOS_AGRADECIMENTOS]
        HAVING SUM(QUANTIDADE) IS NOT NULL)
        """
    cursor.execute(sql_query)

    resultados = []
    for row in cursor.fetchall():
        RE = row.RE
        QUANTIDADES = row.QUANTIDADES
        DECADAS = row.DECADAS
        REPORTES = row.REPORTES
        resultados.append((RE,QUANTIDADES,DECADAS,REPORTES))


 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['RE','QUANTIDADES','DECADAS','REPORTES'])
    df['RE'] = df['RE'].astype(str)
    store_data = df.replace('nan','0')
    return store_data

  #===================================================================================================
def elevacao_inicial():
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query ="""SELECT DISTINCT 
        [RE]
        ,[QUANT_REPROVACOES_SIMULADOR] 
        ,[REPROVA_REGULAMENTO] 
        ,[MEDIA_REGULAMENTOS] 
        ,[QUANT_REPROVACOES_SISTEMAS] 
        ,[MEDIA_PROVAS_SISTEMAS]  
        ,[QNT_REPROVAS_FAO] 
        ,[QUANT_REP_SIST_PSI] 
        FROM [DWINTELIGENCIA].[ELEVACAO].[TB_MATRIZ_ELEVACAO_INICIAL] WITH (NOLOCK)
        """
    cursor.execute(sql_query)
    
    resultados = []
    for row in cursor.fetchall():
        RE = row.RE
        QUANT_REPROVACOES_SIMULADOR = row.QUANT_REPROVACOES_SIMULADOR
        REPROVA_REGULAMENTO = row.REPROVA_REGULAMENTO
        MEDIA_REGULAMENTOS = row.MEDIA_REGULAMENTOS
        QUANT_REPROVACOES_SISTEMAS = row.QUANT_REPROVACOES_SISTEMAS
        MEDIA_PROVAS_SISTEMAS = row.MEDIA_PROVAS_SISTEMAS
        QNT_REPROVAS_FAO = row.QNT_REPROVAS_FAO
        QUANT_REP_SIST_PSI = row.QUANT_REP_SIST_PSI


        resultados.append((RE,QUANT_REPROVACOES_SIMULADOR,REPROVA_REGULAMENTO,MEDIA_REGULAMENTOS,QUANT_REPROVACOES_SISTEMAS,
                           MEDIA_PROVAS_SISTEMAS,QNT_REPROVAS_FAO,QUANT_REP_SIST_PSI))


 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['RE','QUANT_REPROVACOES_SIMULADOR','REPROVA_REGULAMENTO','MEDIA_REGULAMENTOS','QUANT_REPROVACOES_SISTEMAS',
                           'MEDIA_PROVAS_SISTEMAS','QNT_REPROVAS_FAO','QUANT_REP_SIST_PSI'])
    df['RE'] = df['RE'].astype(str)
    store_data = df.replace('nan','0')
    return store_data

  #===================================================================================================
def senoridade_inicial():
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query ="""SELECT DISTINCT RE, SENORIDADE FROM  [DWINTELIGENCIA].[Trip].[TB_CREW_SENORIDADE] WITH (NOLOCK)
        WHERE SENORIDADE IS NOT NULL

        """
    cursor.execute(sql_query)
    
    resultados = []
    for row in cursor.fetchall():
        RE = row.RE
        SENORIDADE = row.SENORIDADE


        resultados.append((RE,SENORIDADE))


 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['RE','SENORIDADE'])
    df['RE'] = df['RE'].astype(str)
    store_data = df.replace('nan','0')
    return store_data
  #===================================================================================================
def sessoes_inicial():
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query ="""SELECT [RE], COUNT([RE]) AS [QUANT_SESSOES]  
    FROM [DWINTELIGENCIA].[ELEVACAO].[TB_ELEVACAO_NIVEL_SIMULADOR] --ORDER BY RE ASC
    GROUP BY RE
        """
    cursor.execute(sql_query)
    
    resultados = []
    for row in cursor.fetchall():
        RE = row.RE
        QUANT_SESSOES = row.QUANT_SESSOES


        resultados.append((RE,QUANT_SESSOES))


 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['RE','QUANT_SESSOES'])
    df['RE'] = df['RE'].astype(str)
    store_data = df.replace('nan','0')
    return store_data

  #===================================================================================================
def media_teorica():
    conn = pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',
                        Server='SQL19BI\SQL19BI',
                        Database='DWINTELIGENCIA',
                        UID='etl_io_crp',
                        PWD='gq2F83Fj*d0*Sq6')
    #df = pd.read_sql("SELECT * FROM DWINTELIGENCIA.DBO.TB_USER_LOGIN",conn)

    cursor = conn.cursor()
    sql_query ="""--MEDIA PROVAS REGULAMENTOS
    SELECT DISTINCT RE, YEAR(CONVERT(DATE, D_DATA, 103)) AS [ANO_PROV], AVG(CONVERT(FLOAT,NOTA)) AS MEDIA
	,'REGULAMENTOS' AS  TIPO_P
	--SELECT *
	FROM [DWINTELIGENCIA].[ELEVACAO].[TB_ELEVACAO_SOLO_MAPEADO]
	WHERE RECORD_ITEM IN ('AVALIAÇÃO EAD - REGULAMENTOS / RVSM / PBN PERIÓDICO',
	'REGULAMENTOS / RVSM / PBN PERIÓDICO - AVALIAÇÃO', 'RTA - CAT II / RVSM / PBN - INICIAL - AVALIAÇÃO',
	'REGULAMENTOS E RVSM INICIAL PILOTOS - AVALIAÇÃO')
	GROUP BY RE, YEAR(CONVERT(DATE, D_DATA, 103))

	union

	-- MEDIA PROVAS SISTEMAS
	SELECT DISTINCT RE,  YEAR(CONVERT(DATE, D_DATA, 103)) AS [ANO_SIST/DIF],  AVG(CONVERT(FLOAT, NOTA)) AS MEDIA
		,'SISTEMAS' AS  TIPO_P 
	FROM [DWINTELIGENCIA].[ELEVACAO].[TB_ELEVACAO_SOLO_MAPEADO]
	WHERE --RE IN (19985) AND 
	RECORD_ITEM LIKE '%SISTEMAS%' OR RECORD_ITEM LIKE '%DIFERENÇA%' AND NOTA <> NULL
	GROUP BY RE, YEAR(CONVERT(DATE, D_DATA, 103))
        """
    cursor.execute(sql_query)
    
    resultados = []
    for row in cursor.fetchall():
        RE = row.RE
        ANO_PROV = row.ANO_PROV
        MEDIA = row.MEDIA
        TIPO_P = row.TIPO_P

        resultados.append((RE,ANO_PROV,MEDIA,TIPO_P))


 
    conn.commit()
    conn.close()
    df = pd.DataFrame(resultados, columns=['RE','ANO_PROV','MEDIA','TIPO_P'])
    df['RE'] = df['RE'].astype(str)
    store_data = df.replace('nan','0')
    return store_data