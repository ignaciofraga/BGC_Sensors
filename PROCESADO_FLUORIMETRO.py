# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 14:47:40 2022

@author: ifraga
"""
import pandas
import datetime
import matplotlib.pyplot as plt
import FUNCIONES_PROCESADO_FLUORIMETRO
import FUNCIONES_GRAFICOS_FLUORIMETRO

                               

directorio_general           = 'C:/Users/Nacho/Desktop/02-TRABAJO/IEO/02-PROYECTOS/02_PLANES_COMPLEMENTARIOS/SENSORES BIOGEOQUIMICOS/FLUORIMETRO_EMS/PROCESADO'

#fecha_despliegue             = '20250116' # Formato YYYY/MM/DD
#fecha_despliegue             = '20250314' # Formato YYYY/MM/DD
fecha_despliegue             = '20250516' # Formato YYYY/MM/DD
archivo_config_despliegue    = None                            
archivo_config_recuperacion  = None

tipo_dato_representa         = 'filtrado' #'filtrado'


directorio_trabajo = directorio_general + '/' + fecha_despliegue

datos_fluorimetro = FUNCIONES_PROCESADO_FLUORIMETRO.lectura_archivo_fluorimetro(directorio_trabajo,archivo_config_despliegue,archivo_config_recuperacion)

#datos_filtrados_fluorimetro = FUNCIONES_PROCESADO_FLUORIMETRO.filtrado_datos_fluorimetro(directorio_trabajo)

#datos_perfilador = FUNCIONES_PROCESADO_FLUORIMETRO.lectura_datos_perfilador(directorio_trabajo)

# FUNCIONES_PROCESADO_FLUORIMETRO.combina_fluorimetro_perfilador(directorio_trabajo)

#listado_variables = ['CHLA','TRYP','CDOM']
#listado_unidades  = ['\u03bcg/L','ppb','ppb']

#listado_variables = ['TRYP']
#listado_unidades  = ['ppb']

#FUNCIONES_GRAFICOS_FLUORIMETRO.graficos_perfiles(directorio_trabajo,listado_variables,listado_unidades,tipo_dato_representa)

#FUNCIONES_GRAFICOS_FLUORIMETRO.gif_evolucion_perfiles(directorio_trabajo,listado_variables,tipo_dato_representa)

#FUNCIONES_GRAFICOS_FLUORIMETRO.serie_temporal(directorio_trabajo,listado_variables,listado_unidades,tipo_dato_representa)

#FUNCIONES_GRAFICOS_FLUORIMETRO.serie_temporal_perfiles(directorio_trabajo,listado_variables,tipo_dato_representa,fecha_despliegue)

#FUNCIONES_GRAFICOS_FLUORIMETRO.serie_temporal_perfiles_lluvia(directorio_general,directorio_trabajo,listado_variables,tipo_dato_representa,fecha_despliegue)

archivo_excel = directorio_trabajo + '/DatosDiscretos_May2025.xlsx'

datos_discretos = pandas.read_excel(archivo_excel,skiprows=2,nrows=8,parse_dates=['fecha'])

datos_discretos['tiempo'] = None

dt_intervalo = 120

for idato in range(datos_discretos.shape[0]):
    datos_discretos['tiempo'].iloc[idato] = datos_discretos['fecha'].iloc[idato]
    datos_discretos['tiempo'].iloc[idato] = datos_discretos['tiempo'].iloc[idato].replace(hour=(datos_discretos['hora local'].iloc[idato].hour-0))
    datos_discretos['tiempo'].iloc[idato] = datos_discretos['tiempo'].iloc[idato].replace(minute=datos_discretos['hora local'].iloc[idato].minute)
    
    
    t_superior = datos_discretos['tiempo'].iloc[idato] + datetime.timedelta(seconds=dt_intervalo)
    t_inferior = datos_discretos['tiempo'].iloc[idato] - datetime.timedelta(seconds=dt_intervalo)


    subset_fluorimetro = datos_fluorimetro[(datos_fluorimetro['tiempo']>=t_inferior) & (datos_fluorimetro['tiempo']<t_superior)]

    if subset_fluorimetro.shape[0] >0:

        datos_discretos['CDOM'].iloc[idato] = subset_fluorimetro.loc[:, 'CDOM'].mean()
        datos_discretos['Tryp (corr)'].iloc[idato] = subset_fluorimetro.loc[:, 'TRYP'].mean()
        datos_discretos['Chla'].iloc[idato] = subset_fluorimetro.loc[:, 'CHLA'].mean()
        datos_discretos['Tryp (raw)'].iloc[idato] = subset_fluorimetro.loc[:, 'mvCF2'].mean()

#fig, ax = plt.subplots(figsize=(20/2.54, 20/2.54))
#ax.plot(subset_fluorimetro['tiempo'],subset_fluorimetro['CDOM'],'ro',markersize = 3,label='Observado')