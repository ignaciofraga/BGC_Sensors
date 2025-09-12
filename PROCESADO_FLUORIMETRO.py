# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 14:47:40 2022

@author: ifraga
"""

import FUNCIONES_PROCESADO_FLUORIMETRO
import FUNCIONES_GRAFICOS_FLUORIMETRO

                               

directorio_general           = 'C:/Users/Nacho/Desktop/02-TRABAJO/IEO/02-PROYECTOS/02_PLANES_COMPLEMENTARIOS/SENSORES BIOGEOQUIMICOS/FLUORIMETRO_EMS/PROCESADO'

#fecha_despliegue             = '20250116' # Formato YYYY/MM/DD
fecha_despliegue             = '20250314' # Formato YYYY/MM/DD
#fecha_despliegue             = '20250516' # Formato YYYY/MM/DD
archivo_config_despliegue    = None                            
archivo_config_recuperacion  = None

tipo_dato_representa         = 'filtrado' #'filtrado'


directorio_trabajo = directorio_general + '/' + fecha_despliegue

#datos_fluorimetro = FUNCIONES_PROCESADO_FLUORIMETRO.lectura_archivo_fluorimetro(directorio_trabajo,archivo_config_despliegue,archivo_config_recuperacion)

#datos_filtrados_fluorimetro = FUNCIONES_PROCESADO_FLUORIMETRO.filtrado_datos_fluorimetro(directorio_trabajo)

datos_perfilador = FUNCIONES_PROCESADO_FLUORIMETRO.lectura_datos_perfilador(directorio_trabajo)

# FUNCIONES_PROCESADO_FLUORIMETRO.combina_fluorimetro_perfilador(directorio_trabajo)

listado_variables = ['CHLA','TRYP','CDOM']
listado_unidades  = ['\u03bcg/L','ppb','ppb']

#listado_variables = ['TRYP']
#listado_unidades  = ['ppb']

#FUNCIONES_GRAFICOS_FLUORIMETRO.graficos_perfiles(directorio_trabajo,listado_variables,listado_unidades,tipo_dato_representa)

#FUNCIONES_GRAFICOS_FLUORIMETRO.gif_evolucion_perfiles(directorio_trabajo,listado_variables,tipo_dato_representa)

#FUNCIONES_GRAFICOS_FLUORIMETRO.serie_temporal(directorio_trabajo,listado_variables,listado_unidades,tipo_dato_representa)

#FUNCIONES_GRAFICOS_FLUORIMETRO.serie_temporal_perfiles(directorio_trabajo,listado_variables,tipo_dato_representa,fecha_despliegue)

#FUNCIONES_GRAFICOS_FLUORIMETRO.serie_temporal_perfiles_lluvia(directorio_general,directorio_trabajo,listado_variables,tipo_dato_representa,fecha_despliegue)

