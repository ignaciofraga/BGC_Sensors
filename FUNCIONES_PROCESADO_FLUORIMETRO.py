# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 14:47:40 2022

@author: ifraga
"""
import pandas
import datetime
import numpy
from scipy.io import loadmat
from pathlib import Path
import os

#### DATOS 
                               
directorio_trabajo           = 'C:/Users/Nacho/Desktop/02-TRABAJO/IEO/02-PROYECTOS/02_PLANES_COMPLEMENTARIOS/SENSORES BIOGEOQUIMICOS/FLUORIMETRO_EMS/PROCESADO/20250116'
#directorio_trabajo           = 'C:/Users/ifraga/Desktop/02-PROYECTOS/02_PLANES_COMPLEMENTARIOS/SENSORES BIOGEOQUIMICOS/FLUOROMETRO_SEABIRD/PROCESADO/20250116'
archivo_fluorimetro_bruto    = directorio_trabajo + '/Datos_fluorimetro_20250116.dat'
archivo_config_despliegue    = directorio_trabajo + '/Tran1.log'                             
archivo_config_recuperacion  = directorio_trabajo + '/Tran1.log'



###########################################################################
#### FUNCION PARA CALCULAR LOS SEGUNDOS TRANSCURRIDOS ENTRE DOS FECHAS ####
###########################################################################

def delta_tiempo_segundos(fecha_inicio,fecha_fin):
    dt  = (fecha_fin - fecha_inicio).days*86400 + (fecha_fin - fecha_inicio).seconds
    return dt




################################################################
#### FUNCION PARA LEER EL ARCHIVO CON DATOS DEL FLUORIMETRO ####
################################################################

def lectura_archivo_fluorimetro(directorio_trabajo,archivo_config_despliegue,archivo_config_recuperacion):

    ### BUSCA EL ARCHIVO DEL FLUORIMETRO
    directorio_datos          = directorio_trabajo + '/DATOS'
    listado_archivos          = [f for f in os.listdir(directorio_datos) if f.endswith('.dat')]    
    archivo_fluorimetro_bruto = listado_archivos[0]

    ### LECTURA ARCHIVO FLUORIMETRO###
    archivo_fluorimetro =  directorio_datos + '/' + archivo_fluorimetro_bruto
    columnas          = ["tiempo","registro","mvCF1","mvCF2","mvCF3","Batt_volt"]
    datos_fluorimetro = pandas.read_csv(archivo_fluorimetro,skiprows=4,names=columnas,parse_dates=['tiempo']) 

    ### CONVERSION DE VOLTAJES A UNIDADES CORRESPONDIENTES ###
    datos_fluorimetro['CDOM'] = (datos_fluorimetro['mvCF1']/1000-0.0181)*107.0687
    datos_fluorimetro['TRYP'] = (datos_fluorimetro['mvCF2']/1000-0.253)*1100.449
    datos_fluorimetro['CHLA'] = (datos_fluorimetro['mvCF3']/1000-0.0416)*25.0367
    
    ### ELIMINA SALTOS TEMPORALES ###
    # Busca saltos temporales
    datos_fluorimetro['fechas'] = datos_fluorimetro['tiempo'].dt.date
    listado_fechas  = datos_fluorimetro['fechas'].unique()
    listado_incrementos =[1]*len(listado_fechas)
    for ifecha in range(1,len(listado_fechas)):
        listado_incrementos[ifecha] =  (listado_fechas[ifecha] - listado_fechas[ifecha - 1]).days
    
    # Asigna un índice io_valido 1 para los datos correltivos, 0 para los que tienen saltos temporales
    indice_elimina         = [i for i in range(len(listado_incrementos)) if listado_incrementos[i] > 1]
    listado_fechas_validas = listado_fechas[0:indice_elimina[0]]
    datos_fluorimetro['io_valido'] = 0
    for ivalida in range(len(listado_fechas_validas)):
        datos_fluorimetro['io_valido'][datos_fluorimetro['fechas']==listado_fechas_validas[ivalida]] = 1
        
    datos_eliminados = datos_fluorimetro[datos_fluorimetro['io_valido']==0]
    if datos_eliminados.shape[0] > 0:
        print('Salto temporal en los datos. Registros eliminados')
    
    # Recorta los datos, manteniendo sólo aquellos que tienen io_valido = 1
    datos_fluorimetro = datos_fluorimetro[datos_fluorimetro['io_valido']==1]
    datos_fluorimetro = datos_fluorimetro.drop(['io_valido','fechas'], axis=1)
    
    ### CORRECCION DE LA DERIVA TEMPORAL ###
    # Realiza la correccion si se dispone de los archivos de configuracion
    if archivo_config_despliegue and archivo_config_recuperacion:
        # Lectura de los archivos de configuracion (despliegue y recuperacion)
        df_config_despliegue           = pandas.read_csv(archivo_config_despliegue, names=['tiempo','equipo','id','estado','tiempo_datalogger','tiempo_pc','e1','e2'],parse_dates=['tiempo','tiempo_datalogger','tiempo_pc'])
        df_puesta_hora_despliegue      = df_config_despliegue[df_config_despliegue['estado']=='Clock set']
        
        tiempo_puesta_hora_datalogger_despliegue   = datetime.datetime.strptime(df_puesta_hora_despliegue['tiempo_datalogger'].iloc[-1]+ '000', '%Y-%m-%d %H:%M:%S.%f')
        tiempo_puesta_hora_real_despliegue         = datetime.datetime.strptime(df_puesta_hora_despliegue['tiempo_pc'].iloc[-1]+ '000', '%Y-%m-%d %H:%M:%S.%f')
        
        df_config_recuperacion         = pandas.read_csv(archivo_config_recuperacion, names=['tiempo','equipo','id','estado','tiempo_datalogger','tiempo_pc','e1','e2'],parse_dates=['tiempo','tiempo_datalogger','tiempo_pc'])
        df_puesta_hora_recuperacion    = df_config_despliegue[df_config_recuperacion['estado']=='Clock set']
        
        tiempo_puesta_hora_datalogger_recuperacion = datetime.datetime.strptime(df_puesta_hora_recuperacion['tiempo_datalogger'].iloc[-1]+ '000', '%Y-%m-%d %H:%M:%S.%f')
        tiempo_puesta_hora_real_recuperacion       = datetime.datetime.strptime(df_puesta_hora_recuperacion['tiempo_pc'].iloc[-1]+ '000', '%Y-%m-%d %H:%M:%S.%f')
        
        ##
        tiempo_puesta_hora_datalogger_recuperacion = tiempo_puesta_hora_datalogger_recuperacion + datetime.timedelta(days=15)
        tiempo_puesta_hora_real_recuperacion       = tiempo_puesta_hora_real_recuperacion + datetime.timedelta(days=15)
        ##
        
        # Calcula la deriva temporal del reloj interno y el offset inicial
        offset_inicio  = delta_tiempo_segundos(tiempo_puesta_hora_real_despliegue,tiempo_puesta_hora_datalogger_despliegue)
        
        deriva_segundos  = delta_tiempo_segundos(tiempo_puesta_hora_real_recuperacion,tiempo_puesta_hora_datalogger_recuperacion) - offset_inicio
        dt_segundos_real = delta_tiempo_segundos(tiempo_puesta_hora_real_despliegue,tiempo_puesta_hora_real_recuperacion)
        pte_recta_tiempo = deriva_segundos/dt_segundos_real
        
        # Corrige las fechas. Asume un offset inicial y una variación lineal de la deriva. 
        tiempo_inicio_corregido = datos_fluorimetro['tiempo'].iloc[0] + datetime.timedelta(seconds=offset_inicio + delta_tiempo_segundos(tiempo_puesta_hora_datalogger_despliegue,datos_fluorimetro['tiempo'].iloc[0])* pte_recta_tiempo)
        tiempo_final_corregido  = datos_fluorimetro['tiempo'].iloc[-1] + datetime.timedelta(seconds=offset_inicio + delta_tiempo_segundos(tiempo_puesta_hora_datalogger_despliegue,datos_fluorimetro['tiempo'].iloc[-1])* pte_recta_tiempo)
        num_pasos_tiempo        = datos_fluorimetro.shape[0]
        
        datos_fluorimetro['tiempo_corregido']  = pandas.date_range(start=tiempo_inicio_corregido, end=tiempo_final_corregido, periods=num_pasos_tiempo)
    
    else:
        # En caso contrario, considerar el tiempo registrado como bueno
        datos_fluorimetro['tiempo_corregido']      = datos_fluorimetro['tiempo']

    ### Convierte los tiempos a segundos (para futura comparacion)
    datos_fluorimetro['tiempo_secs'] = datos_fluorimetro['tiempo_corregido'].astype('int64')

    ### EXPORTA UN ARCHIVO CON LOS DATOS LEIDOS
    archivo_exporta =  directorio_trabajo + '/Datos_brutos_fluorimetro'
    datos_fluorimetro.to_pickle(archivo_exporta)

    return datos_fluorimetro


##################################################################
#### FUNCION PARA FILTRAR SPIKES EN LOS DATOS DEL FLUORIMETRO ####
##################################################################

def filtrado_datos_fluorimetro(directorio_trabajo):
    
    # Lectura datos
    archivo_fluorimetro =  directorio_trabajo + '/Datos_brutos_fluorimetro'
    datos_fluorimetro = pandas.read_pickle(archivo_fluorimetro)
    
    listado_variables           = ['CHLA','TRYP','CDOM']
    listado_maximos             = [20,10,40]
    listado_num_datos_intervalo = [30,30,20]
    listado_delta_spike         = [2,3,1.5]
    listado_num_datos_smooth    = [3,3,3]


    for ivariable in range(len(listado_variables)):
        
        datos_brutos = datos_fluorimetro[listado_variables[ivariable]]
        
        # Filtrado valor maximo
        cond_max          = (datos_brutos > listado_maximos[ivariable])
        datos_brutos      = numpy.where(cond_max, numpy.nan, datos_brutos)

        # Filtrado spikes
        media_movil       = pandas.Series(datos_brutos).rolling(listado_num_datos_intervalo[ivariable],center=True,min_periods=1).mean(numeric_only=True)
        cond_delta        = (numpy.abs(datos_brutos-media_movil) > listado_delta_spike[ivariable])
        datos_filtrados   = numpy.where(cond_delta, numpy.nan, datos_brutos)

        # Suavizado
        datos_promedio    = pandas.Series(datos_filtrados).rolling(listado_num_datos_smooth[ivariable]).mean()

        # Almacena los datos generados en el dataframe
        nombre_variable_filtrado  = listado_variables[ivariable] + '_filtrado'

        nombre_variable_suavizado = listado_variables[ivariable] + '_smooth'

        datos_fluorimetro[nombre_variable_filtrado] = datos_filtrados
        datos_fluorimetro[nombre_variable_suavizado] = datos_promedio

    # Elimina variables no utilizadas, para optimizar el almacenado
    df_exporta = datos_fluorimetro[['tiempo_corregido','tiempo_secs','CHLA_filtrado','TRYP_filtrado','CDOM_filtrado','CHLA_smooth','TRYP_smooth','CDOM_smooth']]

    # Guarda los resultados en un pickle
    archivo_resultados = directorio_trabajo + '/Datos_filtrados_fluorimetro'
    df_exporta.to_pickle(archivo_resultados)

    return df_exporta


#################################################################################
#### FUNCION PARA LEER LOS DATOS DEL PERFILADOR (MATLAB) Y GENERAR UN PICKLE ####
#################################################################################

def lectura_datos_perfilador(directorio_trabajo):


    ### LECTURA DE LOS DATOS DEL PERFILADOR
    # Comprueba si está disponible un pickle con los datos del perfilador
    archivo_perfilador_pickle = directorio_trabajo + '/Datos_perfilador'
    archivo_almacena = Path(archivo_perfilador_pickle) 

    if archivo_almacena.exists():
        
        print('Datos del perfilador ya disponibles, no es necesaria su lectura de nuevo')
        datos_perfilador  = pandas.read_pickle(archivo_perfilador_pickle)
        
    # En caso contrario lee el archivo de matlab y guarda el pickle (por si se utiliza de nuevo)
    else:
        
        # Busca el archivo con datos del perfilador
        directorio_datos          = directorio_trabajo + '/DATOS'
        listado_archivos          = [f for f in os.listdir(directorio_datos) if f.endswith('.mat')]    
        archivo_matlab_perfilador = listado_archivos[0]
        
        # Importa el archivo con datos del perfilador
        archivo_matlab_perfilador = directorio_trabajo + '/DATOS/' +  archivo_matlab_perfilador
        datos = loadmat(archivo_matlab_perfilador)
        
        # Contruye un dataframe con los valores importados
        datos_perfilador = pandas.DataFrame(columns=('Fecha','Netapa','Press','Sal','Temp'))
        for i in range(datos['Fecha03'].shape[0]):
           datos_perfilador.loc[i] = [datos['Fecha03'][i][0],datos['Netapa03'][i][0],datos['Press03'][i][0],datos['Sal03'][i][0],datos['Temp03'][i][0]]
        
        # Convierte las fechas a formato entendibles en python
        datos_perfilador['tiempo'] = pandas.to_datetime(datos_perfilador['Fecha']-719529, unit='D')
        
        # Añade columna con datos en segundos (para futura comparacion)
        datos_perfilador['tiempo_secs'] = datos_perfilador['tiempo'].astype('int64')
        
        
        ### PRE-PROCESADO DATOS PERFILADOR
        # Elimina los datos del perfilador en las etapas de descenso y superficie
        listado_etapas_validas = [2,3,4]
        datos_perfilador = datos_perfilador[datos_perfilador['Netapa'].isin(listado_etapas_validas)]
        
        # Genera un identificador de los perfiles realizador
        iperfil = 0
        datos_perfilador['id_perfil'] = 0
        for idato in range(1,datos_perfilador.shape[0]):
            if (abs(datos_perfilador['Press'].iloc[idato] - datos_perfilador['Press'].iloc[idato-1])) > 2:
                iperfil = iperfil + 1
            datos_perfilador.iat[idato,datos_perfilador.columns.get_loc('id_perfil')] = iperfil
        
        # Exporta la informacion como un pickle
        datos_perfilador.to_pickle(archivo_perfilador_pickle)  

    return datos_perfilador

################################################################################
#### FUNCION PARA COMBINAR LOS DATOS DEL FLUORIMETRO CON LOS DEL PERFILADOR ####
################################################################################

def combina_fluorimetro_perfilador(directorio_trabajo):

    ### COMPRUEBA SI YA EXISTE UN ARCHIVO CON LOS DATOS COMBINADOS
    archivo_datos_combinado = directorio_trabajo + '/Datos_combinados_fluorimetro'         
    archivo                 = Path(archivo_datos_combinado)
    if archivo.exists():
        print('Archivo disponible con los datos de perfilador y fluorímetro combinados')
    
    else:

    ### COMBINA LOS DATOS DE AMBOS SENSORES
        
        print('NO está disponible el archivo con la combinación de sensores. Procesado en curso')
    
        ### LECTURA DE LOS DATOS DEL PERFILADOR
        # Comprueba si está disponible un pickle con los datos del perfilador
        archivo_perfilador_pickle = directorio_trabajo + '/Datos_perfilador'
        archivo_almacena = Path(archivo_perfilador_pickle) 
    
        if archivo_almacena.exists():
            datos_perfilador  = pandas.read_pickle(archivo_perfilador_pickle)
            
        # En caso contrario lee el archivo de matlab y guarda el pickle (por si se utiliza de nuevo)
        else:
            
            print('DATOS DEL PERFILADOR NO DISPONIBLES')
        
            
        ### LECTURA DE LOS DATOS DE FLUORIMETRO 
        # Comprueba si están disponibles los datos del fluorímetro filtrados
        archivo_datos_filtrados = directorio_trabajo + '/Datos_filtrados_fluorimetro'
        archivo                 = Path(archivo_datos_filtrados)
        if archivo.exists():
            datos_fluorimetro = pandas.read_pickle(archivo_datos_filtrados)
            print('Datos filtrados disponibles, se utilizarán en el procesado')
    
        # En caso contrario, lee los datos sin filtrar
        else:   
            
            datos_fluorimetro    = pandas.read_pickle(directorio_trabajo + '/' + '/Datos_brutos_fluorimetro')
            print('Procesado realizado con datos brutos, los datos filtrados NO están disponibles')    
        
            
        
        ### COMBINA LOS DATOS DE AMBOS SENSORES
        
        # Para optimizar el procesado, elimina los datos de los rangos temporales en que no están operando ambos sensores
        # Elimina los datos del fluorimetro anteriores al primer perfil (depliegue en seco)
        datos_fluorimetro = datos_fluorimetro[datos_fluorimetro['tiempo_corregido']>=datos_perfilador['tiempo'].iloc[0]]
        # Elimina los datos del perfilador posteriores al último registros del fluorímetro
        datos_perfilador = datos_perfilador[datos_perfilador['tiempo']<=datos_fluorimetro['tiempo_corregido'].iloc[-1]]
        
        
        # Genera un dataframe vacío con las variables del fluorimetro + los datos del perfilador a combinar
        listado_variables_fluorimetro = datos_fluorimetro.columns.to_list()
        listado_variables_extendido   = listado_variables_fluorimetro + ['temperatura','salinidad','presion','id_perfil','etapa_perfilador']
        df_combinado = pandas.DataFrame(columns=listado_variables_extendido)
        
        # Itera uno a uno los perfiles realizados
        listado_perfiles = datos_perfilador['id_perfil'].unique()
        for iperfil in range(len(listado_perfiles)):

            # Extrae un subset con los datos del perfilador correspondientes a cada perfil            
            df_perfil = datos_perfilador[datos_perfilador['id_perfil']==listado_perfiles[iperfil]]
            
            # Dentro de cada perfil, itera entre los diferentes registros
            for idato_perfilador in range(df_perfil.shape[0]-1):
                
                # Extrae un dataset con los datos del fluorímetro entre dos registros consecutivos del perfilador
                subset_fluorimetro = datos_fluorimetro[(datos_fluorimetro['tiempo_secs']>=df_perfil['tiempo_secs'].iloc[idato_perfilador]) & (datos_fluorimetro['tiempo_secs']<df_perfil['tiempo_secs'].iloc[idato_perfilador+1])]
                
                # Interpola linealmente entre los dos registros del perfilador y asigna los valores a los datos del fluorímetro
                # Añade datos de temperatura
                subset_fluorimetro = subset_fluorimetro.assign(temperatura = list(numpy.linspace(df_perfil['Temp'].iloc[idato_perfilador],df_perfil['Temp'].iloc[idato_perfilador+1],subset_fluorimetro.shape[0])))
            
                # Añade datos de salinidad
                subset_fluorimetro = subset_fluorimetro.assign(salinidad = list(numpy.linspace(df_perfil['Sal'].iloc[idato_perfilador],df_perfil['Sal'].iloc[idato_perfilador+1],subset_fluorimetro.shape[0])))
            
                # Añade datos de presion
                subset_fluorimetro = subset_fluorimetro.assign(presion = list(numpy.linspace(df_perfil['Press'].iloc[idato_perfilador],df_perfil['Press'].iloc[idato_perfilador+1],subset_fluorimetro.shape[0])))
            
                # Asigna el perfil y el número de etapa del dato inicial del perfilador
                # Añade el identificador del perfil
                subset_fluorimetro = subset_fluorimetro.assign(id_perfil = df_perfil['id_perfil'].iloc[idato_perfilador])
            
                # Añade el número de etapa del perfil
                subset_fluorimetro = subset_fluorimetro.assign(etapa_perfilador = df_perfil['Netapa'].iloc[idato_perfilador])
            
            
                # Concatena el subset con los datos combinados al dataframe inicial
                df_combinado = pandas.concat([df_combinado, subset_fluorimetro])
            
            
            porcentaje_procesado = int(100*iperfil/len(listado_perfiles))
            print(porcentaje_procesado,'% procesado')
        
        # Exporta un pickle
        df_combinado.to_pickle(archivo_datos_combinado) 
        
        
        
        

