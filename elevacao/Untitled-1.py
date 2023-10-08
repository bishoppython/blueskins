from PILOT_convert import *
from PILOT_sql import *

df = global_database()
df = pd.DataFrame(df)

lista_6 = ['QUANT_SESSOES','QUANT_REPROVACOES_SIMULADOR']

#df_tb6 = ajuste_base(df,lista_6) 
print(df['QUANT_SESSOES1'])


