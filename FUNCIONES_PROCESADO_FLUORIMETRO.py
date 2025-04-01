# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 14:47:40 2022

@author: ifraga
"""
import pandas
import datetime
import numpy
import matplotlib.pyplot as plt
import math
import scipy
import os
import imageio.v3 as iio
import seaborn

def delta_tiempo_segundos(fecha_inicio,fecha_fin):
    dt  = (fecha_fin - fecha_inicio).days*86400 + (fecha_fin - fecha_inicio).seconds
    return dt

# #### DATOS 
archivo_fluorimetro          = 'D:/DATOS/Desktop/Nacho/TRABAJO/IEO/02-PROYECTOS/02_PLANES_COMPLEMENTARIOS/SENSORES BIOGEOQUIMICOS/FLUORIMETRO_SEABIRD/PROCESADO/CR300Series_Datos.dat'
tiempo_zero_inicio           = datetime.datetime(2025,1,30,12,10,5)
tiempo_zero_final_real       = datetime.datetime(2025,2,10,14,6,7)
tiempo_zero_final_datalogger = datetime.datetime(2025,2,10,14,5,7)
offset_tiempo         = 30
#test = pandas.read_csv(archivo_aft,skiprows=0,nrows=1)

# Lectura archivo
columnas  = ["tiempo","registro","mvCF1","mvCF2","mvCF3","Batt_volt"]
datos     = pandas.read_csv(archivo_fluorimetro,skiprows=4,names=columnas,parse_dates=['tiempo'],nrows=500) 

# Convierte registros de voltaje a unidades
datos['CDOM'] = (datos['mvCF1']-0.0181)*107.0687
datos['TRYP'] = (datos['mvCF2']-0.253)*1100.449
datos['CHLA'] = (datos['mvCF3']-0.0416)*25.0367

# Busca saltos temporales
datos['fechas'] = datos['tiempo'].dt.date
listado_fechas  = datos['fechas'].unique()
listado_incrementos =[1]*len(listado_fechas)
for ifecha in range(1,len(listado_fechas)):
    listado_incrementos[ifecha] =  (listado_fechas[ifecha] - listado_fechas[ifecha - 1]).days


indice_elimina         = [i for i in range(len(listado_incrementos)) if listado_incrementos[i] > 1]
if len(indice_elimina) > 0:
    listado_fechas_validas = listado_fechas[0:indice_elimina[0]]
    datos['valida'] = 0
    for ivalida in range(len(listado_fechas_validas)):
        datos['valida'][datos['fechas']==listado_fechas_validas[ivalida]] = 1


# Corrige la deriva temporal del reloj interno
deriva_segundos  = delta_tiempo_segundos(tiempo_zero_final_real,tiempo_zero_final_datalogger)
dt_segundos_real = delta_tiempo_segundos(tiempo_zero_inicio,tiempo_zero_final_real)
pte_recta_tiempo = deriva_segundos/dt_segundos_real

# Fecha de inicio de la medida corregida
tiempo_inicio_corregido = datos['tiempo'].iloc[0] + datetime.timedelta(seconds=delta_tiempo_segundos(tiempo_zero_inicio,datos['tiempo'].iloc[0])* pte_recta_tiempo)
tiempo_final_corregido  = datos['tiempo'].iloc[-1] + datetime.timedelta(seconds=delta_tiempo_segundos(tiempo_zero_inicio,datos['tiempo'].iloc[-1])* pte_recta_tiempo)
num_pasos_tiempo        = datos.shape[0]

datos['tiempo_corregido']  = pandas.date_range(start=tiempo_inicio_corregido, end=tiempo_final_corregido, periods=num_pasos_tiempo)
#tiempo_final = datos['fecha'].iloc[-1]

####

datos['id_perfil'] = None

for idato in range(20,50):
    #datos.iloc[idato].at['id_perfil'] = 1
    datos.iat[idato, datos.columns.get_loc('id_perfil')] = 1

for idato in range(100,130):
    datos.iat[idato, datos.columns.get_loc('id_perfil')] = 2
    
for idato in range(300,330):
    datos.iat[idato, datos.columns.get_loc('id_perfil')] = 3


variable = 'CDOM'
multiplo = 10
multiplos_prof = 2

directorio_trabajo = 'D:/DATOS/Desktop/Nacho/TRABAJO/IEO/02-PROYECTOS/02_PLANES_COMPLEMENTARIOS/SENSORES BIOGEOQUIMICOS/FLUORIMETRO_SEABIRD/PROCESADO'
directorio_imagenes = directorio_trabajo + '/FIGURAS'
os.makedirs(directorio_imagenes, exist_ok=True)
archivo_gif = directorio_imagenes + '/Evolucion_' + variable + '.gif'
# Busca los perfiles disponibles
perfiles = [x for x in datos['id_perfil'].unique() if x is not None]




maximo_perfil_variable = []
minimo_perfil_variable = []

for iperfil in range(len(perfiles)):
    df_perfil = datos[datos['id_perfil']==perfiles[iperfil]]
    
    df_perfil['prof'] = None
    for idato in range(df_perfil.shape[0]):
        df_perfil.iat[idato, df_perfil.columns.get_loc('prof')] = idato
        
    maximo_perfil_variable = maximo_perfil_variable + [max(df_perfil[variable])]
    minimo_perfil_variable = minimo_perfil_variable + [min(df_perfil[variable])]
    
# Rangos de variación
val_min_var = int(multiplo * round(float(min(minimo_perfil_variable))/multiplo)) - multiplo
val_max_var = int(multiplo * round(float(max(maximo_perfil_variable))/multiplo)) + multiplo

val_min_prof = 0
val_max_prof = 35

    
listado_figuras = []

for iperfil in range(len(perfiles)):
    df_perfil = datos[datos['id_perfil']==perfiles[iperfil]]
    
    df_perfil['prof'] = None
    for idato in range(df_perfil.shape[0]):
        df_perfil.iat[idato, df_perfil.columns.get_loc('prof')] = idato
    
    nombre_archivo = directorio_imagenes + '/perfil_' + str(iperfil) + '_' + variable + '.png'
    listado_figuras = listado_figuras + [nombre_archivo]
    
    fig, ax = plt.subplots(figsize=(20/2.54, 20/2.54))

    # Textos
    #ax.set_title('Perfil ' + variable + ' ' + df_perfil['tiempo'].iloc[0].strftime('%Y-%m-%d') , fontsize=16)
    ax.text(0.75, 0.9, 'Fecha:'+ df_perfil['tiempo'].iloc[0].strftime('%d/%m/%y'), transform=ax.transAxes, fontsize=14)
    ax.text(0.75, 0.82, 'Hora:'+ df_perfil['tiempo'].iloc[0].strftime('%H:%M:%S'), transform=ax.transAxes, fontsize=14)
    #Representacion
    ax.grid(True)
    
    #ax = seaborn.relplot(data=df_perfil,x="CDOM", y="prof",hue="CDOM", palette="ch:r=-.5,l=.75")
    ax.plot(df_perfil['CDOM'],df_perfil['prof'],'ro',markersize = 3,label='Observado')
    ax.set_xlim(val_min_var,val_max_var)
    ax.set_ylim(val_min_prof,val_max_prof)
    ax.set_yticks(list(numpy.arange(val_min_prof,val_max_prof,multiplos_prof)))
    ax.set_xlabel(variable, fontsize=16)
    ax.set_ylabel('Profundidad (m)', fontsize=16)
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.invert_yaxis()
    # Guardado de la imagen
    fig.savefig(nombre_archivo)   # save the figure to file
    plt.close(fig)


imagenes = []
for iarchivo in listado_figuras:
    imagenes.append(iio.imread(iarchivo))
iio.imwrite(archivo_gif, imagenes, duration = 0.5)



# Evolución temporal fondo

datos_fondo = datos[datos['id_perfil'].isnull()]


nombre_archivo = directorio_imagenes + '/Evolucion_fondo_' + variable + '.png'



#Representacion

#fig, ax = plt.subplots(figsize = (12,6))    
#fig     = seaborn.relplot(data=datos_fondo,x="tiempo_corregido", y=variable ,hue=variable, palette="ch:r=-.5,l=.75")


#x_dates = emp['12monthsEnding'].dt.strftime('%Y-%m-%d').sort_values().unique()
#ax.set_xticklabels(labels=x_dates, rotation=45, ha='right')

ax = seaborn.relplot(data=datos_fondo,x="tiempo_corregido", y=variable ,hue=variable, palette="ch:r=-.5,l=.75",height=8.27, aspect=11.7/8.27)
ax.set(xlabel='Tiempo', ylabel=variable)






    # #ax = fig.add_subplot(111)
    # ax.text(0.5, 0.75, df_perfil['tiempo'].iloc[0].strftime('%Y-%m-%d %H:%M:%S'), transform=ax.transAxes, fontsize=14)
    
    # #plt.text(0.5, 0.5, df_perfil['tiempo'].iloc[0].strftime('%Y-%m-%d %H:%M:%S'), horizontalalignment='center')

    # figura_perfil = fig.add_axes([0.075, 0.075, 0.85, 0.85] ,xlim=(val_min_var, val_max_var),ylim=(0,val_max_prof))
    # figura_perfil.grid(False)
    # figura_perfil.plot(df_perfil['CDOM'],df_perfil['prof'],'ro',markersize = 3,label='Observado')
    # figura_perfil.set_xlabel(variable)
    # figura_perfil.set_ylabel('Profundidad (m)')
    # plt.gca().invert_yaxis()

    # fig.savefig(nombre_archivo)   # save the figure to file
    # plt.close(fig)

# test = pandas.date_range(start = datos['fecha'][0],end = datos['fecha'][-1])

# test2 = pandas.timedelta_range("1 Day", periods=3, freq="100000D", unit="s")
# time_range = pandas.date_range('2016-12-02T11:00:00.000Z', '2017-06-06T07:00:00.000Z', freq='H')

# archivo_tsg       = 'C:/Users/ifraga/Desktop/02-PROYECTOS/01_RADIALES/CONTINUO_LURA/SCRIPTS PROCESADO/TSG_02-12-2022.cnv'
# archivo_optodo    = 'C:/Users/ifraga/Desktop/02-PROYECTOS/01_RADIALES/CONTINUO_LURA/SCRIPTS PROCESADO/oximetro_20221202.txt'
# archivo_pco2      = 'C:/Users/ifraga/Desktop/02-PROYECTOS/01_RADIALES/CONTINUO_LURA/PRUEBAS 11ENERO/datafile_20230111_100807.txt'

# archivo_estaciones = 'C:/Users/ifraga/Desktop/02-PROYECTOS/01_RADIALES/CONTINUO_LURA/PRUEBAS 11ENERO/Estaciones.xlsx'
# #fecha_salida       = datetime.date(2022,12,2)
# fecha_salida       = datetime.date(2023,1,11)
# directorio_salida  = 'C:/Users/ifraga/Desktop/02-PROYECTOS/01_RADIALES/CONTINUO_LURA/PRUEBAS 11ENERO'




# base_datos     = 'termosalinografos'
# usuario        = 'ignacio'
# contrasena     ='1gn4c10'
# puerto         = '5432'
# direccion_host = '172.20.0.202'



# FUNCION PARA GENERAR TABLA EN LAS QUE GUARDAR INFORMACIÓN DEL AFT EN LA BD CENTOLO\termosalinografos 
def genera_tabla_ph_centolo(datos_conexion):
    
    # TABLA PARA ALMACENAR DATOS DEL AFT
    
    conn = psycopg2.connect(host = datos_conexion['host'][0],database=datos_conexion['base_datos'][0], user=datos_conexion['usuario'][0], password=datos_conexion['contrasena'][0], port=datos_conexion['puerto'][0])
    cursor = conn.cursor()
    
    nombre_tabla = 'ph_aft_datos'
    
    # Borra la table si ya existía
    instruccion_sql = 'DROP TABLE IF EXISTS ' + nombre_tabla + ' CASCADE;'
    cursor.execute(instruccion_sql)
    conn.commit()
    
    # Crea la tabla de nuevo
    listado_variables = ('(fecha TIMESTAMP WITHOUT TIME ZONE,'
    'latitude NUMERIC (6, 4),'
    'longitude NUMERIC (6, 4),'
    'geometry GEOMETRY (GEOMETRY, 4326) DEFAULT NULL,'    
    'temperatura_aft NUMERIC (6, 4),'
    'salinidad_tsg NUMERIC (6, 4),'
    'pH NUMERIC (6, 5)'
    ) 
    
    listado_unicidades = (', UNIQUE (fecha))')
    
    instruccion_sql = 'CREATE TABLE IF NOT EXISTS ' + nombre_tabla + ' ' + listado_variables + ' ' + listado_unicidades
    cursor.execute(instruccion_sql)
    conn.commit()
    cursor.close()
    conn.close()
    
# FUNCION PARA GENERAR TABLA EN LAS QUE GUARDAR INFORMACIÓN DEL pCO2 EN LA BD CENTOLO\termosalinografos    
def genera_tabla_pco2_centolo(datos_conexion):
    
    
    # TABLA PARA ALMACENAR DATOS DEL pCO2
    
    conn = psycopg2.connect(host = datos_conexion['host'][0],database=datos_conexion['base_datos'][0], user=datos_conexion['usuario'][0], password=datos_conexion['contrasena'][0], port=datos_conexion['puerto'][0])
    cursor = conn.cursor()
    
    nombre_tabla = 'pco2_datos'
    
    # Borra la table si ya existía
    instruccion_sql = 'DROP TABLE IF EXISTS ' + nombre_tabla + ' CASCADE;'
    cursor.execute(instruccion_sql)
    conn.commit()
    
    # Crea la tabla de nuevo
    listado_variables = ('(fecha TIMESTAMP WITHOUT TIME ZONE,'
    'latitude NUMERIC (6, 4),'
    'longitude NUMERIC (6, 4),'
    'geometry GEOMETRY (GEOMETRY, 4326) DEFAULT NULL,'  
    'p_ndir NUMERIC (7, 3),'
    'p_in NUMERIC (7, 3),'
    'zero int,'
    'flush int,'
    'signal_raw int,'
    'signal_ref int,'
    't_gas NUMERIC (5, 3),'    
    'xco2_procesado NUMERIC (7, 3),'
    'pco2_procesado NUMERIC (7, 3)'
    ) 

    
    listado_unicidades = (', UNIQUE (fecha))')
    
    instruccion_sql = 'CREATE TABLE IF NOT EXISTS ' + nombre_tabla + ' ' + listado_variables + ' ' + listado_unicidades
    cursor.execute(instruccion_sql)
    conn.commit()
    cursor.close()
    conn.close()




## FUNCION DE LECTURA DE LOS DATOS DE ESTACIONES
def lectura_estaciones (archivo_estaciones,fecha_salida,df_datos_conexion_navalla):

    datos_estaciones = pandas.read_excel(archivo_estaciones)
    
    # Añade columna con tiempos
    datos_estaciones['tiempo_llegada']         = [None]*datos_estaciones.shape[0]
    datos_estaciones['tiempo_salida']          = [None]*datos_estaciones.shape[0]
    datos_estaciones['tiempo_muestreo']        = [None]*datos_estaciones.shape[0]
    datos_estaciones['tiempo_cierre_botella']  = [None]*datos_estaciones.shape[0]
    datos_estaciones['muestreo']            = [None]*datos_estaciones.shape[0]
    for idato in range(datos_estaciones.shape[0]):
        datos_estaciones['tiempo_llegada'][idato]   = datetime.datetime.combine(fecha_salida,datos_estaciones['Hora llegada'][idato])
        datos_estaciones['tiempo_salida'][idato]    = datetime.datetime.combine(fecha_salida,datos_estaciones['Hora salida'][idato])
        datos_estaciones['tiempo_muestreo'][idato]  = datetime.datetime.combine(fecha_salida,datos_estaciones['Hora continuo'][idato])
    
    ### Busca el instante de muestreo de cada estacion (tiempo de cierre de botella)
    con_engine         = 'postgresql://' + df_datos_conexion_navalla['usuario'][0] + ':' + df_datos_conexion_navalla['contrasena'][0] + '@' + df_datos_conexion_navalla['host'][0] + ':' + str(df_datos_conexion_navalla['puerto'][0]) + '/' + df_datos_conexion_navalla['base_datos'][0]
    conn_psql          = create_engine(con_engine)
    # recupera la tabla con los identificadores de cada estacion
    instruccion_SQL       = " SELECT * FROM estaciones WHERE programa = %(programa)s "  
    parametros_consulta   = {'programa': 3}
    df_estaciones_navalla = pandas.read_sql_query(instruccion_SQL, con=conn_psql, params=parametros_consulta)
    # Recupera la tabla con las salidas realizadas
    instruccion_SQL       = " SELECT * FROM salidas_muestreos"  
    df_salidas_navalla    = pandas.read_sql_query(instruccion_SQL, con=conn_psql)
    df_recorte            = df_salidas_navalla[ (df_salidas_navalla['programa'] == 3) & (df_salidas_navalla['tipo_salida'] == 'MENSUAL') & (df_salidas_navalla['fecha_salida'] == fecha_salida) ]
    if df_recorte.shape[0] > 0:
        id_salida             = df_recorte['id_salida'].iloc[0]
        # Recupera la información de los muestreos disponibles para la salida correspondiente
        instruccion_SQL        = " SELECT * FROM muestreos_discretos"  
        df_muestreos_discretos = pandas.read_sql_query(instruccion_SQL, con=conn_psql)
        df_muestreos_discretos = df_muestreos_discretos[df_muestreos_discretos['salida_mar'] == int(id_salida)]
        
        # En caso de disponer de muestreos de la salida correspondiente, busca las horas de cierre
        if df_muestreos_discretos.shape[0] > 0:
            datos_estaciones['id_estacion']            = [None]*datos_estaciones.shape[0]
            # Compara el nombre de cada estación para encontrar el identificador correspondiente
            for idato in range(datos_estaciones.shape[0]):
                for iestacion in range(df_estaciones_navalla.shape[0]):
                    if str(datos_estaciones['Estación'][idato]).upper() == df_estaciones_navalla['nombre_estacion'][iestacion]:
                        datos_estaciones['id_estacion'][idato] =  df_estaciones_navalla['id_estacion'][iestacion]
                # Busca la hora de cierre de la botella a partir del identificador de la botella
                for imuestreo in range(df_muestreos_discretos.shape[0]):
                    if df_muestreos_discretos['estacion'].iloc[imuestreo] == datos_estaciones['id_estacion'][idato] and df_muestreos_discretos['prof_referencia'].iloc[imuestreo] == 0 :
                        try:
                            datos_estaciones['tiempo_cierre_botella'][idato] = datetime.datetime.combine(df_muestreos_discretos['fecha_muestreo'].iloc[imuestreo],df_muestreos_discretos['hora_muestreo'].iloc[imuestreo])
                        except:
                            datos_estaciones['tiempo_cierre_botella'][idato] = None
                        datos_estaciones['muestreo'][idato] = df_muestreos_discretos['muestreo'].iloc[imuestreo] 
    
    conn_psql.dispose()
    
    return datos_estaciones




## FUNCION DE LECTURA DEL ARCHIVO BRUTO DEL AFT
def lectura_aft(archivo_aft):

    # Parámetros (extraídos del manual/aportados por fabricante)
    to               = datetime.datetime(1904,1,1)
    max_bits_rt      = 4096
    
    # Abre el archivo como lectura
    lectura_archivo = open(archivo_aft, "r")  
    datos_archivo = lectura_archivo.readlines()
    
    # Itera en cada una de las líneas
    for ilinea in range(len(datos_archivo)):
        
        texto_linea = datos_archivo[ilinea]
    
        # Lee parametros del AFT
        if texto_linea[0:5] == 'Cal1:' :
            mol_abs_a_434 = float(texto_linea[6:-1])
        if texto_linea[0:5] == 'Cal2:' :
            mol_abs_b_434= float(texto_linea[6:-1])
        if texto_linea[0:5] == 'Cal3:' :
            mol_abs_a_578= float(texto_linea[6:-1])
        if texto_linea[0:5] == 'Cal4:' :
            mol_abs_b_578= float(texto_linea[6:-1])       
        if texto_linea[0:5] == 'Cal5:' :
            temp_offset = float(texto_linea[6:-1])
        if texto_linea[0:10] == '  #Blanks=' : 
            texto_blancos    = ((texto_linea.split('='))[1].split('=')[0])
            num_blancos      = int(texto_blancos)
        if texto_linea[0:16] == '  #Measurements=' : 
            texto_blancos    = ((texto_linea.split('='))[1].split('=')[0])
            num_muestras     = int(texto_blancos)       
        if texto_linea[0:5] == ':Data' :
            num_lineas_cabecera = ilinea + 3
    
    lectura_archivo.close()
        
    # Genera un listado con las variables a leer
    listado_variables = ['tipo_medida','dt_sec','temp_signal']
    for irepeticion in range(1,28):
        listado_variables = listado_variables + ['434ref'+str(irepeticion)] + ['434sig'+str(irepeticion)] + ['578ref'+str(irepeticion)] + ['578sig'+str(irepeticion)]
    listado_variables = listado_variables + ['int_temp','bat','signal']
    
    # Lee los datos como un dataframe
    dataframe_datos_aft = pandas.read_csv(archivo_aft, sep='\s+', header=None,skiprows=num_lineas_cabecera)
    dataframe_datos_aft.columns = listado_variables
    
    # Elimina la ultima fila (sin datos)
    dataframe_datos_aft = dataframe_datos_aft[:-1]
    
    # Determina los tiempos de medida y las temperaturas
    dataframe_datos_aft['tiempo']      = [None]*dataframe_datos_aft.shape[0]
    dataframe_datos_aft['temperatura_aft'] = [None]*dataframe_datos_aft.shape[0]
    for idato in range(dataframe_datos_aft.shape[0]):
        dataframe_datos_aft['tiempo'].iloc[idato]      =  to + datetime.timedelta(seconds=int(dataframe_datos_aft['dt_sec'].iloc[idato]))  
        rt = ( dataframe_datos_aft['temp_signal'].iloc[idato]/ (max_bits_rt - dataframe_datos_aft['temp_signal'].iloc[idato]) )* 17400
        dataframe_datos_aft['temperatura_aft'].iloc[idato] =  1/(0.0010183 + 0.000241 * math.log(rt) + 0.00000015 * math.log(rt)**3 ) - 273.15  
        dataframe_datos_aft['temperatura_aft'].iloc[idato] = dataframe_datos_aft['temperatura_aft'].iloc[idato] + temp_offset
               
    # Genera un dataframe con las constantes del AFT
    parametros_AFT = pandas.DataFrame([[mol_abs_a_434,mol_abs_b_434,mol_abs_a_578,mol_abs_b_578,temp_offset,num_blancos,num_muestras]], columns=['mol_abs_a_434','mol_abs_b_434','mol_abs_a_578','mol_abs_b_578','temp_offset','num_blancos','num_muestras'])
    
    return dataframe_datos_aft,parametros_AFT





## FUNCION PARA PROCESAR ARCHIVOS BRUTOS DEL AFT Y DEVOLVER VALORES DE PH
def procesado_aft(dataframe_datos_tsg,dataframe_datos_aft,parametros_AFT,num_descartes):

    # Asigna la salinidad y las coordenadas de cada medida a partir de los datos del TSG 
    dataframe_datos_aft['salinidad'] = [None]*dataframe_datos_aft.shape[0]
    for idato in range(dataframe_datos_aft.shape[0]):
        dif_tiempos                             = numpy.asarray(abs(dataframe_datos_aft['tiempo'][idato] - dataframe_datos_tsg['tiempo']))
        indice_posicion                         = numpy.argmin(dif_tiempos)       
        dataframe_datos_aft['salinidad'][idato] = dataframe_datos_tsg['salinidad'][indice_posicion]
 
    # Parametros
    num_rep_blancos  = parametros_AFT['num_blancos'][0]
    num_rep_ph       = parametros_AFT['num_muestras'][0]-num_descartes
    
    dataframe_datos_aft['pH_procesado'] = [None]*dataframe_datos_aft.shape[0]
    
    for imedida in range(dataframe_datos_aft.shape[0]):
        
        ## PROCESADO DE LOS BLANCOS
        
        # Determina el ratio en cada longitud de onda
        sig_434 = numpy.zeros(num_rep_blancos)
        ref_434 = numpy.zeros(num_rep_blancos)
        sig_578 = numpy.zeros(num_rep_blancos)
        ref_578 = numpy.zeros(num_rep_blancos)
        
        ratio_434 = numpy.zeros(num_rep_blancos)
        ratio_578 = numpy.zeros(num_rep_blancos)
        for iblanco in range(num_rep_blancos):
            sig_434 [iblanco] = dataframe_datos_aft['434sig'+str(iblanco+1)][imedida]
            ref_434 [iblanco] = dataframe_datos_aft['434ref'+str(iblanco+1)][imedida]
            sig_578 [iblanco] = dataframe_datos_aft['578sig'+str(iblanco+1)][imedida]
            ref_578 [iblanco] = dataframe_datos_aft['578ref'+str(iblanco+1)][imedida]        
            
            ratio_434[iblanco] = (dataframe_datos_aft['434sig'+str(iblanco+1)][imedida])/(dataframe_datos_aft['434ref'+str(iblanco+1)][imedida])
            ratio_578[iblanco] = (dataframe_datos_aft['578sig'+str(iblanco+1)][imedida])/(dataframe_datos_aft['578ref'+str(iblanco+1)][imedida])
                    
        # Encuentra los 3 puntos del blanco con menor desviación
        desv_434 = numpy.zeros(num_rep_blancos)
        desv_578 = numpy.zeros(num_rep_blancos)
        for iblanco in range(num_rep_blancos):
            vector_temporal_434 = numpy.delete(ratio_434, iblanco)
            desv_434[iblanco]   = numpy.nanstd(vector_temporal_434,ddof=1)
            vector_temporal_578 = numpy.delete(ratio_578, iblanco)    
            desv_578[iblanco]   = numpy.nanstd(vector_temporal_578,ddof=1)
                    
        indice_elimina_434 = numpy.argmax(desv_434)
        indice_elimina_578 = numpy.argmax(desv_578)
        
        sig_434_reducido    = numpy.delete(sig_434, indice_elimina_434)
        ref_434_reducido    = numpy.delete(ref_434, indice_elimina_434)
        sig_578_reducido    = numpy.delete(sig_578, indice_elimina_578)
        ref_578_reducido    = numpy.delete(ref_578, indice_elimina_578)
        
        io434ref            = numpy.mean(ref_434_reducido)
        io434sig            = numpy.mean(sig_434_reducido)
        io578ref            = numpy.mean(ref_578_reducido)
        io578sig            = numpy.mean(sig_578_reducido)
    
        
        ## PROCESADO DEL PH
        
        # Predimensiona
        abs_434 = numpy.zeros(num_rep_ph)
        abs_578 = numpy.zeros(num_rep_ph) 
        
        hi_indicador      = numpy.zeros(num_rep_ph)
        i_indicador       = numpy.zeros(num_rep_ph) 
        conc_indicador    = numpy.zeros(num_rep_ph)
        
        ph_temporal           = []
        conc_temporal         = []
        
        # Determina  absortividades molares   
        ea_434 = parametros_AFT['mol_abs_a_434'][0] + 28.7533 * (25 - dataframe_datos_aft['temperatura_aft'][imedida])
        ea_578 = parametros_AFT['mol_abs_a_578'][0] 
        eb_434 = parametros_AFT['mol_abs_b_434'][0] - 7.6338  * (25 - dataframe_datos_aft['temperatura_aft'][imedida])
        eb_578 = parametros_AFT['mol_abs_b_578'][0] + 73.7198 * (25 - dataframe_datos_aft['temperatura_aft'][imedida])      
        
        e1     = ea_578/ea_434
        e2     = eb_578/ea_434
        e3     = eb_434/ea_434
        
        # Calcula absorbancias, concentraciones y pka de cada repeticion
        for irepeticion in range(num_rep_ph):
            abs_434[irepeticion]  = -math.log((dataframe_datos_aft['434sig'+str(irepeticion+num_rep_blancos + num_descartes+1)][imedida]/dataframe_datos_aft['434ref'+str(irepeticion+num_rep_blancos + num_descartes+1)][imedida])*(io434ref/io434sig),10)
            abs_578[irepeticion]  = -math.log((dataframe_datos_aft['578sig'+str(irepeticion+num_rep_blancos + num_descartes+1)][imedida]/dataframe_datos_aft['578ref'+str(irepeticion+num_rep_blancos + num_descartes+1)][imedida])*(io578ref/io578sig),10)
     
            hi_indicador[irepeticion] = ((abs_434[irepeticion]*eb_578) - (abs_578[irepeticion]*eb_434))/((ea_434*eb_578) - (eb_434*ea_578))
            i_indicador[irepeticion]  = ((abs_578[irepeticion]*ea_434) - (abs_434[irepeticion]*ea_578))/((ea_434*eb_578) - (eb_434*ea_578))
           
            conc_indicador[irepeticion] = hi_indicador[irepeticion] + i_indicador[irepeticion]
            
            # Calcula el pH solo si la concentracion de indicador está en un intervalo determinado
            if conc_indicador[irepeticion]> 10**(-5) and conc_indicador[irepeticion] < 8*10**(-5): 
            
            
                salinidad_factor   =  conc_indicador[irepeticion]*35/(3.78*(10**-4)) + (1+conc_indicador[irepeticion]/(3.78*(10**-4)))*dataframe_datos_aft['salinidad'][imedida]
                pka                = -241.462 + 7085.72/(dataframe_datos_aft['temperatura_aft'][imedida]+273.15) + 43.8332*math.log(dataframe_datos_aft['temperatura_aft'][imedida]+273.15) - 0.0806406*(dataframe_datos_aft['temperatura_aft'][imedida]+273.15) - 0.3238*(salinidad_factor**0.5)+0.0807*salinidad_factor - 0.01157*(salinidad_factor**1.5)+0.000694*(salinidad_factor**2) + 0.6367
                ratio_absorbancias = abs_578[irepeticion]/abs_434[irepeticion]
                coef               = (ratio_absorbancias-e1)/(e2-ratio_absorbancias*e3)
                ph_temporal        = ph_temporal + [pka + math.log(coef,10)] 
                conc_temporal      = conc_temporal + [conc_indicador[irepeticion]]
                
                
        # Construye las regresiones [conc,ph] de las repeticiones que superan el umbra, utilizando 3,4 y 5 puntos
        # Regresiones con 3 puntos
        if len(ph_temporal) >=3:
            
            num_reg_3_ptos = len(ph_temporal) - 2
            
            ph_3ptos = numpy.zeros(num_reg_3_ptos)
            r2_3ptos = numpy.zeros(num_reg_3_ptos)
     
            for ireg3 in range(num_reg_3_ptos):
            
                valores_ph        = ph_temporal[(0+ireg3):(3+ireg3)]
                valores_indicador = conc_temporal[(0+ireg3):(3+ireg3)]         
        
                #slope, ph_3ptos[ireg3], r2_3ptos[ireg3], p, se  = scipy.stats.linregress(valores_indicador, valores_ph)
                res  = scipy.stats.linregress(valores_indicador, valores_ph)
                
                r2_3ptos[ireg3] = res.rvalue**2
                ph_3ptos[ireg3] = res.intercept
                
            r2_total = r2_3ptos
            ph_total = ph_3ptos
                
        # Regresiones con 4 puntos
        if len(ph_temporal) >=4:
            
            num_reg_4_ptos = len(ph_temporal) - 3
            
            ph_4ptos = numpy.zeros(num_reg_4_ptos)
            r2_4ptos = numpy.zeros(num_reg_4_ptos)
     
            for ireg4 in range(num_reg_4_ptos):
            
                valores_ph        = ph_temporal[(0+ireg4):(4+ireg4)]
                valores_indicador = conc_temporal[(0+ireg4):(4+ireg4)]         
            
                res  = scipy.stats.linregress(valores_indicador, valores_ph)
                
                r2_4ptos[ireg4] = res.rvalue**2
                ph_4ptos[ireg4] = res.intercept
                
            r2_total = numpy.concatenate((r2_3ptos,r2_4ptos))
            ph_total = numpy.concatenate((ph_3ptos,ph_4ptos))
     
        # Regresiones con 5 puntos
        if len(ph_temporal) >=5:
            
            num_reg_5_ptos = len(ph_temporal) - 4
            
            ph_5ptos = numpy.zeros(num_reg_5_ptos)
            r2_5ptos = numpy.zeros(num_reg_5_ptos)
     
            for ireg5 in range(num_reg_5_ptos):
            
                valores_ph        = ph_temporal[(0+ireg5):(5+ireg5)]
                valores_indicador = conc_temporal[(0+ireg5):(5+ireg5)]         
            
                res  = scipy.stats.linregress(valores_indicador, valores_ph)
                
                r2_5ptos[ireg5] = res.rvalue**2
                ph_5ptos[ireg5] = res.intercept
     
            r2_total = numpy.concatenate((r2_3ptos,r2_4ptos,r2_5ptos))
            ph_total = numpy.concatenate((ph_3ptos,ph_4ptos,ph_5ptos))
     
    
        # Encuentra el mejor ajuste [conc,ph] y asigna el valor de pH procesado
        indice_mejor_ajuste = numpy.argmax(r2_total)
        dataframe_datos_aft['pH_procesado'][imedida] = ph_total[indice_mejor_ajuste]
        
    # Genera un dataframe con variables y unidades
    listado_variables        = ['temperatura_aft','salinidad','pH_procesado']
    listado_unidades         = ['degC','PSU','uds']
    dataframe_variables_aft  = pandas.DataFrame(list(zip(listado_variables, listado_unidades)),columns =['variable','unidades'])
          
    return dataframe_datos_aft,dataframe_variables_aft



## FUNCION PARA ASIGNAR COORDENADAS A CADA MEDIDA DEL AFT
def coordenadas_aft(dataframe_datos_tsg,dataframe_datos_aft):

    # Asigna las coordenadas y temperatura de cada medida a partir de los datos del TSG 
    dataframe_datos_aft['latitude']  = numpy.zeros(dataframe_datos_aft.shape[0])
    dataframe_datos_aft['longitude'] = numpy.zeros(dataframe_datos_aft.shape[0])
    dataframe_datos_aft['temperatura_tsg'] = numpy.zeros(dataframe_datos_aft.shape[0])
    for idato in range(dataframe_datos_aft.shape[0]):
        dif_tiempos     = numpy.asarray(abs(dataframe_datos_aft['tiempo'][idato] - dataframe_datos_tsg['tiempo']))
        indice_posicion = numpy.argmin(dif_tiempos)
        
        dataframe_datos_aft['latitude'][idato]        = dataframe_datos_tsg['latitude'][indice_posicion]
        dataframe_datos_aft['longitude'][idato]       = dataframe_datos_tsg['longitude'][indice_posicion]
        dataframe_datos_aft['temperatura_tsg'][idato] = dataframe_datos_tsg['temperatura_tsg'][indice_posicion]   

    return dataframe_datos_aft



# FUNCION PARA BUSCAR LA ESTACION ASOCIADA A CADA MEDIDA DE pH
def estaciones_aft(dataframe_datos_aft,dataframe_estaciones,dataframe_datos_pco2,dataframe_datos_optodo):
    
    dataframe_datos_aft['pCO2_procesado'] = numpy.zeros(dataframe_datos_aft.shape[0])
    dataframe_datos_aft['reg_pCO2']   = numpy.zeros(dataframe_datos_aft.shape[0])
    dataframe_datos_aft['oxigeno']    = numpy.zeros(dataframe_datos_aft.shape[0])
    
    # Asocia a cada medida la estación correspondiente (o MAR si no tiene ninguna)
    dataframe_datos_aft['estacion'] = ['MAR']*dataframe_datos_aft.shape[0]
       
    for imedida in range(dataframe_datos_aft.shape[0]):
        for iestacion  in range(dataframe_estaciones.shape[0]):
            
            if dataframe_estaciones['tiempo_llegada'][iestacion] <= dataframe_datos_aft['tiempo'][imedida] and dataframe_estaciones['tiempo_salida'][iestacion] >= dataframe_datos_aft['tiempo'][imedida]:
                
                dataframe_datos_aft['estacion'][imedida] = dataframe_estaciones['Estación'][iestacion]
            
    # Asocia a cada medida el valor de pCO2y O2 en ese instante
    for imedida in range(dataframe_datos_aft.shape[0]):

        if dataframe_datos_pco2 is not None:
            dif_tiempos        = numpy.asarray(abs(dataframe_datos_aft['tiempo'][imedida] - dataframe_datos_pco2['tiempo']))
            indice_posicion    = numpy.argmin(dif_tiempos)
            dataframe_datos_aft['pCO2_procesado'][imedida] = dataframe_datos_pco2['pCO2_procesado'][indice_posicion]
            dataframe_datos_aft['reg_pCO2'][imedida]   = dataframe_datos_pco2['flag'][indice_posicion]
        
        dif_tiempos        = numpy.asarray(abs(dataframe_datos_aft['tiempo'][imedida] - dataframe_datos_optodo['tiempo']))
        indice_posicion    = numpy.argmin(dif_tiempos)
        dataframe_datos_aft['oxigeno'][imedida] = dataframe_datos_optodo['oxigeno'][indice_posicion]
            
    # Calcula para cada estacion el pH medio y la desviacion estandar
    
    dataframe_estaciones['ph_procesado_media'] = [None]*dataframe_estaciones.shape[0]
    dataframe_estaciones['ph_procesado_desv']  = [None]*dataframe_estaciones.shape[0]
    for iestacion in range(dataframe_estaciones.shape[0]):
    
        valores_pH  = dataframe_datos_aft['pH_procesado'][dataframe_datos_aft['estacion']==dataframe_estaciones['Estación'][iestacion]]
        if len(valores_pH)>0:
            dataframe_estaciones['ph_procesado_media'][iestacion] = valores_pH.mean()
            dataframe_estaciones['ph_procesado_desv'][iestacion] = valores_pH.std()   
                   
    return dataframe_datos_aft,dataframe_estaciones






# ## FUNCION LECTURA DEL ARCHIVO DEL TSG 
def lectura_tsg(archivo_tsg):

    # Predimensiona el listado de variables
    listado_variables = []
    listado_unidades  = []
    
    # Lectura del archivo linea a linea
    lectura_archivo = open(archivo_tsg, "r")  
    datos_archivo = lectura_archivo.readlines()
    
    for ilinea in range(len(datos_archivo)):
        
        texto_linea = datos_archivo[ilinea]
    
        # Lectura instante de comienzo
        if texto_linea[0:14] == '# start_time =' : 
            fecha_txt        = ((texto_linea.split('= '))[1].split('[')[0])
            fecha_inicio_TSG = datetime.datetime.strptime(fecha_txt, '%b %d %Y %H:%M:%S ') 
    
        # Lectura de variables registradas
        if texto_linea[0:6] == '# name' :
            texto_variable    = ((texto_linea.split('= '))[1].split(':')[0])
            listado_variables = listado_variables + [texto_variable]
            
            try:
                texto_unidades    = ((texto_linea.split('['))[1].split(']')[0])
            except:
                texto_unidades    = None
            listado_unidades  = listado_unidades + [texto_unidades]
            
        # Identificacion del numero de lineas en la cabecera
        if texto_linea[0:5] == '*END*' :
            num_lineas_cabecera = ilinea + 1
            
    lectura_archivo.close()
    
    # Lee los datos como un dataframe
    dataframe_datos_tsg = pandas.read_csv(archivo_tsg, sep='\s+', header=None,skiprows=num_lineas_cabecera)
    dataframe_datos_tsg.columns = listado_variables
    
    # Añade columna con tiempos
    dataframe_datos_tsg['tiempo'] = [None]*dataframe_datos_tsg.shape[0]
    for idato in range(dataframe_datos_tsg.shape[0]):
        dataframe_datos_tsg['tiempo'][idato] = fecha_inicio_TSG + datetime.timedelta(seconds=dataframe_datos_tsg['timeM'][idato]*60)
    
    # Genera un dataframe con variables y unidades
    dataframe_variables_tsg = pandas.DataFrame(list(zip(listado_variables, listado_unidades)),columns =['variable','unidades'])

    # Cambia el nombre de la columna con los datos de temperatura
    dataframe_datos_tsg = dataframe_datos_tsg.rename(columns={'t090c': 'temperatura_tsg'})

    return dataframe_datos_tsg,dataframe_variables_tsg





## FUNCION LECTURA ARCHIVO OPTODO
def lectura_optodo(archivo_optodo):

    # Abre el archivo modo lectura
    lectura_archivo = open(archivo_optodo, "r")  
    datos_archivo = lectura_archivo.readlines()
    
    # Identifica las variables medidas y las unidades utilizadas
    listado_variables = (datos_archivo[2]).split(";")
    del listado_variables[-1]
    listado_unidades  = (datos_archivo[3]).split(";")
    del listado_unidades[-1]
    
    # Cierra el archivo
    lectura_archivo.close()
    
    # Lee el archivo como un dataframe
    dataframe_datos_optodo = pandas.read_csv(archivo_optodo, decimal='.', skiprows=4 , sep=";", header=None)
    
    # Elimina ultima columna (todo NaN)
    dataframe_datos_optodo.drop(dataframe_datos_optodo.columns[len(dataframe_datos_optodo.columns)-1], axis=1, inplace=True)
    
    # Asigna encabezados
    dataframe_datos_optodo.columns = listado_variables
    
    # Modifica tiempos
    dataframe_datos_optodo['tiempo'] = [None]*dataframe_datos_optodo.shape[0]
    for idato in range(dataframe_datos_optodo.shape[0]):
        texto_registro                          = dataframe_datos_optodo['Date'][idato] + ' '  +  (dataframe_datos_optodo['Time'][idato]).split(".")[0]
        dataframe_datos_optodo['tiempo'][idato] = datetime.datetime.strptime(texto_registro, '%Y-%m-%d %H:%M:%S')

    # Genera un dataframe con variables y unidades
    dataframe_variables_optodo = pandas.DataFrame(list(zip(listado_variables, listado_unidades)),columns =['variable','unidades'])


    return dataframe_datos_optodo,dataframe_variables_optodo






## FUNCION LECTURA ARCHIVO PCO2
def lectura_pco2(archivo_pco2):

    # Abre el archivo modo lectura
    lectura_archivo = open(archivo_pco2, "r")  
    datos_archivo = lectura_archivo.readlines()
    
    # Identifica las variables medidas y las unidades utilizadas
    listado_variables = (datos_archivo[2]).split(";")
    del listado_variables[-1]
    listado_unidades  = (datos_archivo[3]).split(";")
    del listado_unidades[-1]
    
    # Cierra el archivo
    lectura_archivo.close()
    
    # Lee el archivo como un dataframe
    dataframe_datos_pco2 = pandas.read_csv(archivo_pco2, decimal=',', skiprows=4 , sep=";", header=None)
    
    # Elimina ultima columna (todo NaN)
    dataframe_datos_pco2.drop(dataframe_datos_pco2.columns[len(dataframe_datos_pco2.columns)-1], axis=1, inplace=True)
    
    # Asigna encabezados
    dataframe_datos_pco2.columns = listado_variables
    
    # Modifica tiempos
    dataframe_datos_pco2['tiempo'] = [None]*dataframe_datos_pco2.shape[0]
    for idato in range(dataframe_datos_pco2.shape[0]):

        texto_registro                        = dataframe_datos_pco2['Date'][idato] + ' '  +  dataframe_datos_pco2['Time'][idato]
        dataframe_datos_pco2['tiempo'][idato] = datetime.datetime.strptime(texto_registro, '%Y-%m-%d %H:%M:%S')
        
        dataframe_datos_pco2['Date'][idato]   = dataframe_datos_pco2['tiempo'][idato].date()
    
    # Genera un dataframe con variables y unidades
    dataframe_variables_pco2 = pandas.DataFrame(list(zip(listado_variables, listado_unidades)),columns =['variable','unidades'])
        
    return dataframe_datos_pco2,dataframe_variables_pco2



## FUNCION PROCESADO ARCHIVO PCO2
def procesado_pco2(dataframe_datos_pco2,dataframe_variables_pco2,df_datos_tsg,dataframe_calibraciones):

    # Correccion 2 haces
    dataframe_datos_pco2['S2beam'] = dataframe_datos_pco2['Signal_raw']/dataframe_datos_pco2['Signal_ref']
    
    # Determina el intervalo de tiempo entre medidas consecutivas
    dt_medida = (dataframe_datos_pco2['tiempo'].iloc[1] - dataframe_datos_pco2['tiempo'].iloc[0]).total_seconds()
    
    ## Identifica las horas en las que se producen los zeros y recorta un sub-set con esos datos
    dataframe_zeros = dataframe_datos_pco2[dataframe_datos_pco2['Zero']== 1]
    
    # Determina el intervalo de tiempo entre dos medidas consecutivas
    dataframe_zeros['dt'] = numpy.zeros(dataframe_zeros.shape[0])
    for idato in range(dataframe_zeros.shape[0]-1):
        dataframe_zeros['dt'].iloc[idato] = (dataframe_zeros['tiempo'].iloc[idato+1] - dataframe_zeros['tiempo'].iloc[idato]).total_seconds()
    
    # Identifica dónde acaba cada tanda de zeros buscando dt entre dos zeros consecutivos, superiores al intervalo de medida
    indices_saltos = dataframe_zeros.index[dataframe_zeros['dt']>dt_medida].tolist()
    
    # Busca los índices en que se producen esos saltos y recupera la hora correspondiente
    indices_inicio_zeros = [0] + [x+1 for x in indices_saltos]
    indices_final_zeros  = indices_saltos + [dataframe_zeros.shape[0]-1] 
    
    horas_inicio_zeros = dataframe_zeros['tiempo'].iloc[indices_inicio_zeros]
    horas_final_zeros  = dataframe_zeros['tiempo'].iloc[indices_final_zeros]
    
    # Genera dos listados de valores, uno con las fechas y otro con los zeros, para luego interpolar
    tiempos_zeros = []
    valores_zeros = []
        
    # Determina el promedio de los zeros durante cada intervalo
    zero_promedio = numpy.zeros(len(horas_inicio_zeros))
    for izero in range(len(indices_inicio_zeros)):
        # Extrae los valores de cada intervalo
        valores_senal = dataframe_zeros['S2beam'][indices_inicio_zeros[izero]:indices_final_zeros[izero]+1]
        # Elimina el primer valor (señal todavía elevada)
        valores_senal = valores_senal.drop(valores_senal.index[0])
        # Promedia el valor
        zero_promedio[izero] = numpy.mean(valores_senal)
    
        tiempos_zeros = tiempos_zeros + [horas_inicio_zeros.iloc[izero]] + [horas_final_zeros.iloc[izero]]
        valores_zeros = valores_zeros + [zero_promedio[izero]] + [zero_promedio[izero]]
        
        
    # Interpola los zeros
    dataframe_datos_pco2['S2beam_zero'] = [None]*dataframe_datos_pco2.shape[0]
    dataframe_datos_pco2['S2beam_zero'][dataframe_datos_pco2['tiempo']<tiempos_zeros[0]] =  valores_zeros[0]    
    dataframe_datos_pco2['S2beam_zero'][dataframe_datos_pco2['tiempo']>tiempos_zeros[-1]] =  valores_zeros[-1]    
    
    for idato in range(dataframe_datos_pco2.shape[0]):
        for izero in range(0,len(valores_zeros)-1):
            if dataframe_datos_pco2['tiempo'][idato] >= tiempos_zeros[izero] and dataframe_datos_pco2['tiempo'][idato] <= tiempos_zeros[izero+1]:
                dataframe_datos_pco2['S2beam_zero'][idato] = valores_zeros[izero] + ((dataframe_datos_pco2['tiempo'][idato]-tiempos_zeros[izero]).seconds)*(valores_zeros[izero+1]-valores_zeros[izero])/((tiempos_zeros[izero+1]-tiempos_zeros[izero]).seconds)
            
            
    # Determina los parámetros del sensor propios de cada paso de tiempo
    listado_variables = ['factor_f','k1','k2','k3','t0','p0']
    if dataframe_calibraciones.shape[0]==1: # Sólo 1 calibración, asigna los datos disponibles a todos los pasos de tiempo
        for ivariable in range(len(listado_variables)):
            dataframe_datos_pco2[listado_variables[ivariable]] = dataframe_calibraciones[listado_variables[ivariable]].iloc[0]
    else:
        for idato in range(dataframe_datos_pco2.shape[0]):
            for icalibracion in range(dataframe_calibraciones.shape[0]-1):
                if dataframe_datos_pco2['Date'].iloc[idato] >= dataframe_calibraciones['fecha_calibracion'].iloc[icalibracion]  and dataframe_datos_pco2['Date'].iloc[idato] <= dataframe_calibraciones['fecha_calibracion'].iloc[icalibracion+1]:
                    dt_calibraciones = (dataframe_calibraciones['fecha_calibracion'].iloc[icalibracion+1]-dataframe_calibraciones['fecha_calibracion'].iloc[icalibracion]).total_seconds()
                    for ivariable in range(len(listado_variables)):
                        dataframe_datos_pco2[listado_variables[ivariable]] = dataframe_calibraciones[listado_variables[ivariable]].iloc[icalibracion] + (dataframe_calibraciones[listado_variables[ivariable]].iloc[icalibracion+1]-dataframe_calibraciones[listado_variables[ivariable]].iloc[icalibracion])/dt_calibraciones*(dataframe_datos_pco2['Runtime'].iloc[idato])
                        
                    

        
    # Calcula la señal corregida con el drift
    dataframe_datos_pco2['Scorr'] = dataframe_datos_pco2['S2beam']/dataframe_datos_pco2['S2beam_zero']
    
    # Aplica el factor de transformación
    dataframe_datos_pco2['Sprocesado'] = dataframe_datos_pco2['factor_f']*(1-dataframe_datos_pco2['Scorr'])
    
    # Calcula xCO2 a partir de la curva de calibracion
    dataframe_datos_pco2['xCO2_procesado'] = (dataframe_datos_pco2['k3']*dataframe_datos_pco2['Sprocesado']**3+dataframe_datos_pco2['k2']*dataframe_datos_pco2['Sprocesado']**2+dataframe_datos_pco2['k1']*dataframe_datos_pco2['Sprocesado'])*(dataframe_datos_pco2['p0']*(dataframe_datos_pco2['T_gas']+273.15))/(dataframe_datos_pco2['t0']*dataframe_datos_pco2['p_NDIR'])
    dataframe_datos_pco2['xCO2_procesado'][dataframe_datos_pco2['xCO2_procesado']<0] = 0
    
    # Calcula pCO2 a partir de xCO2 y las presiones/temperaturas de medida
    dataframe_datos_pco2['pCO2_procesado'] = dataframe_datos_pco2['xCO2_procesado']*dataframe_datos_pco2['p_in']/1013.25
       
    # Añade la variable corregida al dataframe de variables
    dataframe_variables_pco2['pCO2_procesado'] = 'µatm'
    
    return dataframe_datos_pco2,dataframe_variables_pco2



## FUNCION PARA ASIGNAR FLAGS DE TIPO DE REGISTRO 
def flags_pco2(dataframe_datos_pco2):

    # Añade una unica columna con el tipo de medida 0=zero, 1=flush, 2=medida 
    dataframe_datos_pco2['flag'] = [None]*dataframe_datos_pco2.shape[0]
    
    dataframe_datos_pco2['flag'][dataframe_datos_pco2['Zero']==1]  = 0
    dataframe_datos_pco2['flag'][dataframe_datos_pco2['Flush']==1] = 1
    dataframe_datos_pco2['flag'][(dataframe_datos_pco2['Zero'] != 1) & (dataframe_datos_pco2['Flush'] != 1)] = 2

    return dataframe_datos_pco2

    
## FUNCION COMBINACION DATOS PCO2 y TSG
def coordenadas_pco2(dataframe_datos_pco2,df_datos_tsg):
    
    if df_datos_tsg.shape[0]>0:
        # Asigna a cada medida la posición y temperaturas correspondientes, obtenidas de los datos del TSG
        dataframe_datos_pco2['latitude']        = numpy.zeros(dataframe_datos_pco2.shape[0])
        dataframe_datos_pco2['longitude']       = numpy.zeros(dataframe_datos_pco2.shape[0])
        dataframe_datos_pco2['temperatura_tsg'] = numpy.zeros(dataframe_datos_pco2.shape[0])
        dataframe_datos_pco2['salinidad_tsg']   = numpy.zeros(dataframe_datos_pco2.shape[0])
        
        for idato_pco2 in range(dataframe_datos_pco2.shape[0]):
            dif_tiempos     = numpy.asarray(abs(dataframe_datos_pco2['tiempo'][idato_pco2] - df_datos_tsg['tiempo']))
            indice_posicion = numpy.argmin(dif_tiempos)
            
            dataframe_datos_pco2['latitude'][idato_pco2]        = df_datos_tsg['latitude'][indice_posicion]
            dataframe_datos_pco2['longitude'][idato_pco2]       = df_datos_tsg['longitude'][indice_posicion]
            dataframe_datos_pco2['temperatura_tsg'][idato_pco2] = df_datos_tsg['temperatura_tsg'][indice_posicion]   
            dataframe_datos_pco2['salinidad_tsg'][idato_pco2]   = df_datos_tsg['salinidad'][indice_posicion]
        

    return dataframe_datos_pco2




## FUNCION PARA EXTRAER LOS DATOS DE UNA VARIABLE EN LAS ESTACIONES MUESTREADAS
def extrae_datos_estaciones(directorio_salida,dataframe_estaciones,dataframe_datos_aft,dataframe_datos,variable,fecha_salida):

    # Busca las unidades de la variable
    if variable == 'pH_procesado':
        unidades = 'uds'
    if variable == 'oxigeno':
        unidades = '\u03BCmol/kg'
    if variable == 'salinidad':
        unidades = 'psu'
    if variable == 'pCO2_procesado':
        unidades = '\u03BCatm'
    if variable == 'temperatura_tsg':
        unidades = 'degC'
    
    # Genera columnas en el dataframe de estaciones para guardar la variable
    dataframe_estaciones[variable+'_media'] = [None]*dataframe_estaciones.shape[0]
    dataframe_estaciones[variable+'_desv']  = [None]*dataframe_estaciones.shape[0]
    
    
    # Crea imagen con tantos subplots como estaciones
    fig, axs = plt.subplots(dataframe_estaciones.shape[0],1)
    
    titulo  = 'Medidas ' + variable + ' salida ' + fecha_salida.strftime("%m/%d/%Y")
    axs[0].set_title(titulo)
        
    
    
    # Itera en cada estacion
    for iestacion  in range(dataframe_estaciones.shape[0]):
            
        # Encuentra la posicion (indice) del dataframe correspondiente a la llegada de la estacion
        dif_tiempos             = numpy.asarray(abs(dataframe_estaciones['tiempo_llegada'][iestacion] - dataframe_datos['tiempo']))
        indice_posicion_llegada = numpy.argmin(dif_tiempos)
    
        # Encuentra la posicion (indice) del dataframe correspondiente a la salida de la estacion
        dif_tiempos             = numpy.asarray(abs(dataframe_estaciones['tiempo_salida'][iestacion] - dataframe_datos['tiempo']))
        indice_posicion_salida  = numpy.argmin(dif_tiempos)
    
        # comprobacion por si no hay valores en la estacion buscada    
        if indice_posicion_llegada == indice_posicion_salida:
            dataframe_estaciones[variable+'_media'][iestacion] = None
            dataframe_estaciones[variable+'_desv'][iestacion]  = None
            
            axs[iestacion].set_yticks([])
            axs[iestacion].set_xticks([]) 
            
            textstr = ' La estacion ' + dataframe_estaciones['Estación'][iestacion] + ' no dispone de datos de ' + variable
            props = dict(boxstyle='round', facecolor='white', alpha=0.5)
            axs[iestacion].text(0.155, 0.5, textstr, transform=axs[iestacion].transAxes,fontsize=10,verticalalignment='center', bbox=props)
    
            
        else:
    
            # 
            if variable == 'pCO2_procesado':

                # Extrae los valores medidos en la estacion 
                valores_registrados     = dataframe_datos[variable][indice_posicion_llegada:indice_posicion_salida]
                tiempos_registro        = dataframe_datos['tiempo'][indice_posicion_llegada:indice_posicion_salida]
                tipo_medida             = dataframe_datos['flag'][indice_posicion_llegada:indice_posicion_salida]
           
                df_temp = pandas.DataFrame(list(zip(valores_registrados, tiempos_registro,tipo_medida)),columns =['valor','tiempo','tipo'])

                df_medidas = df_temp[df_temp['tipo']==2]
                axs[iestacion].plot(df_medidas['tiempo'],df_medidas['valor'],'-k',label='Medida')
                
                df_no_medidas = df_temp[df_temp['tipo']!=2]
                axs[iestacion].plot(df_no_medidas['tiempo'],df_no_medidas['valor'],'--k',label='Zero/Flush')                

                axs[iestacion].legend(loc='lower left')

            else:
    
                # Extrae los valores medidos en la estacion 
                valores_registrados     = dataframe_datos[variable][indice_posicion_llegada:indice_posicion_salida]
                tiempos_registro        = dataframe_datos['tiempo'][indice_posicion_llegada:indice_posicion_salida]
    
                # Representa los valores registrados en cada estación
                axs[iestacion].plot(tiempos_registro,valores_registrados,'k')

            # Extrae y representa el valor promedio
            dataframe_estaciones[variable+'_media'][iestacion] = valores_registrados.mean()
            dataframe_estaciones[variable+'_desv'][iestacion]  = valores_registrados.std()
   
            axs[iestacion].plot([tiempos_registro.iloc[0],tiempos_registro.iloc[-1]],[valores_registrados.mean(),valores_registrados.mean()],':k')    
                
            # Busca los valores de la variable en el instante de medida del pH
            if dataframe_datos_aft is not None:
                df_ph_estacion = dataframe_datos_aft[dataframe_datos_aft['estacion']==dataframe_estaciones['Estación'][iestacion]]
                #if df_ph_estacion.shape[0] > 0:
                axs[iestacion].plot(df_ph_estacion['tiempo'],df_ph_estacion[variable],'.r')    
    
            ### Ajusta formatos del grafico ###
            
            # Eje x sólo para los intervalos de tiempo de cada estacion
            axs[iestacion].set_xlim([min(tiempos_registro), max(tiempos_registro)])
            formato     = DateFormatter("%H:%M")
            axs[iestacion].xaxis.set_major_formatter(formato)
            
            # Eje y entre valores máximoy mínimo
            num_ticks   = 3
            dt_y        = (max(valores_registrados)-min(valores_registrados))/(num_ticks-1)
            axs[iestacion].yaxis.set_major_locator(plt.MaxNLocator(num_ticks))
            axs[iestacion].set_yticks(numpy.arange(min(valores_registrados), max(valores_registrados)+dt_y, step=dt_y))
            axs[iestacion].set_ylim([min(valores_registrados), max(valores_registrados)])
            
            # Recuadro con nombre de estacion y media
            textstr = '\n'.join((
                r'Estacion ' + (str(dataframe_estaciones['Estación'][iestacion])).upper(),
                r'$\mu=%.2f$' % (valores_registrados.mean(), ) + '  '  + '$\sigma=%.2f$' % (valores_registrados.std(), )))
            props = dict(boxstyle='round', facecolor='white', alpha=0.5)
            axs[iestacion].text(0.75, 0.95, textstr, transform=axs[iestacion].transAxes,fontsize=10,verticalalignment='top', bbox=props)
    
    # Adapta el tamaño de la imagen y el nombre de los ejes
    fig.set_size_inches(8, 12)
    texto_ejey   = variable + '(' + unidades + ')'
    fig.supylabel(texto_ejey)
    fig.supxlabel('Hora')
    fig.tight_layout(pad=1)
    
    # Guarda la imagen
    nombre_archivo = directorio_salida + '/' + variable + '_' + fecha_salida.strftime("%Y_%m_%d")+ '.png'
    fig.savefig(nombre_archivo, bbox_inches='tight')

    plt.close(fig)

    return dataframe_estaciones







## FUNCION PARA EXTRAER LOS DATOS DE UNA VARIABLE EN LAS ESTACIONES MUESTREADAS
def extrae_datos_botellero(df_datos_conexion_navalla,dataframe_estaciones,df_datos_tsg,df_datos_optodo,dataframe_datos_pco2):

    dataframe_botellero = dataframe_estaciones[['Estación','tiempo_cierre_botella','id_muestreo']]
    
    # Genera columnas en el dataframe de estaciones para guardar la variable
    dataframe_botellero['oxigeno_continuo']     = [None]*dataframe_estaciones.shape[0]
    dataframe_botellero['salinidad_continuo']   = [None]*dataframe_estaciones.shape[0]
    dataframe_botellero['temperatura_continuo'] = [None]*dataframe_estaciones.shape[0]
    dataframe_botellero['pCO2_continuo']        = [None]*dataframe_estaciones.shape[0]     
    dataframe_botellero['salinidad_roseta']     = [None]*dataframe_estaciones.shape[0]
    dataframe_botellero['temperatura_roseta']   = [None]*dataframe_estaciones.shape[0]  
    dataframe_botellero['oxigeno_roseta']       = [None]*dataframe_estaciones.shape[0]
     
    
    
    # Elimina las estaciones que no tienen hora de muestreo
    dataframe_botellero = dataframe_botellero.dropna(subset=['tiempo_cierre_botella'])[list(dataframe_botellero)]
    indices_dataframe    = numpy.arange(0,dataframe_botellero.shape[0],1,dtype=int)
    dataframe_botellero['id'] = indices_dataframe
    dataframe_botellero.set_index('id',drop=True,append=False,inplace=True)    
     
    if dataframe_botellero.shape[0] > 0:
        
        # Recupera los datos de la base de datos
        con_engine         = 'postgresql://' + df_datos_conexion_navalla['usuario'][0] + ':' + df_datos_conexion_navalla['contrasena'][0] + '@' + df_datos_conexion_navalla['host'][0] + ':' + str(df_datos_conexion_navalla['puerto'][0]) + '/' + df_datos_conexion_navalla['base_datos'][0]
        conn_psql          = create_engine(con_engine)
        instruccion_SQL    = " SELECT * FROM datos_discretos_fisica" 
        df_datos_fisica    = pandas.read_sql_query(instruccion_SQL, con=conn_psql)
        instruccion_SQL    = " SELECT * FROM datos_discretos_biogeoquimica" 
        df_datos_bgq       = pandas.read_sql_query(instruccion_SQL, con=conn_psql)
        conn_psql.dispose()
        
        # Busca la informacion de cada botella
        for ibotella in range(dataframe_botellero.shape[0]):
            
            # Comparacion con el tsg
            dif_tiempos     = numpy.asarray(abs(dataframe_botellero['tiempo_cierre_botella'][ibotella] - df_datos_tsg['tiempo']))
            indice_posicion = numpy.argmin(dif_tiempos)
    
            dataframe_botellero['salinidad_continuo'][ibotella]   = df_datos_tsg['salinidad'][indice_posicion]
            dataframe_botellero['temperatura_continuo'][ibotella] = df_datos_tsg['temperatura_tsg'][indice_posicion]
    
            # Comparacion con el optodo
            dif_tiempos     = numpy.asarray(abs(dataframe_botellero['tiempo_cierre_botella'][ibotella] - df_datos_optodo['tiempo']))
            indice_posicion = numpy.argmin(dif_tiempos)
            
            dataframe_botellero['oxigeno_continuo'][ibotella] = df_datos_optodo['oxigeno'][indice_posicion]
    
            
            # Comparacion con el sensor pCO2
            dif_tiempos     = numpy.asarray(abs(dataframe_botellero['tiempo_cierre_botella'][ibotella] - dataframe_datos_pco2['tiempo']))
            indice_posicion = numpy.argmin(dif_tiempos)
    
            dataframe_botellero['pCO2_continuo'][ibotella]   = dataframe_datos_pco2['pCO2_procesado'][indice_posicion]
    
            # Comparacion con la roseta   
            df_datos_fisica_botella    = df_datos_fisica[df_datos_fisica['muestreo']==dataframe_botellero['id_muestreo'][ibotella]]
            if df_datos_fisica_botella.shape[0]>0:
                dataframe_botellero['salinidad_roseta'][ibotella]   = df_datos_fisica_botella['salinidad_ctd'].iloc[0]
                dataframe_botellero['temperatura_roseta'][ibotella] = df_datos_fisica_botella['temperatura_ctd'].iloc[0]
                
            df_datos_bgq_botella    = df_datos_bgq[df_datos_bgq['muestreo']==dataframe_botellero['id_muestreo'][ibotella]]
            if df_datos_bgq_botella.shape[0]>0:            
                dataframe_botellero['oxigeno_roseta'][ibotella]     = df_datos_bgq_botella['oxigeno_ctd'].iloc[0]
     
        
    else:
        
        dataframe_botellero = None

    return dataframe_botellero


## FUNCION PARA EXTRAER LOS DATOS DEL CONTINUO EN EL MOMENTO DEL MUESTREO 
def extrae_datos_continuo(dataframe_estaciones,dataframe_datos_pco2,df_datos_optodo,df_datos_tsg):

    # Elimina las estaciones que no tienen hora de muestreo
    dataframe_continuo = dataframe_estaciones.dropna(subset=['tiempo_muestreo'])[list(dataframe_estaciones)]

    # Elimina la columna con datos medios de ph en cada estación
    try:
        dataframe_continuo = dataframe_continuo.drop(columns=['ph_procesado_media','ph_procesado_desv'])
    except:
        pass

    # Genera columnas en el dataframe de estaciones para guardar la variable
    dataframe_continuo['pCO2']        = [None]*dataframe_estaciones.shape[0]
    dataframe_continuo['O2']          = [None]*dataframe_estaciones.shape[0]
    dataframe_continuo['Salinidad']   = [None]*dataframe_estaciones.shape[0]
    dataframe_continuo['Temperatura'] = [None]*dataframe_estaciones.shape[0]    
          
    # Itera en cada estacion
    for iestacion  in range(dataframe_estaciones.shape[0]):
            
        # pCO2
        if dataframe_datos_pco2 is not None:
            dif_tiempos_pco2     = numpy.asarray(abs(dataframe_estaciones['tiempo_muestreo'][iestacion] - dataframe_datos_pco2['tiempo']))
            indice_posicion_pco2 = numpy.argmin(dif_tiempos_pco2)
    
            dataframe_continuo['pCO2'][iestacion] = dataframe_datos_pco2['pCO2_procesado'][indice_posicion_pco2]


        # O2
        dif_tiempos_o2     = numpy.asarray(abs(dataframe_estaciones['tiempo_muestreo'][iestacion] - df_datos_optodo['tiempo']))
        indice_posicion_o2 = numpy.argmin(dif_tiempos_o2)
    
        dataframe_continuo['O2'][iestacion] = df_datos_optodo['oxigeno'][indice_posicion_o2]
    
        
        # Sal
        dif_tiempos_sal     = numpy.asarray(abs(dataframe_estaciones['tiempo_muestreo'][iestacion] - df_datos_tsg['tiempo']))
        indice_posicion_sal = numpy.argmin(dif_tiempos_sal)
    
        dataframe_continuo['Salinidad'][iestacion] = df_datos_tsg['salinidad'][indice_posicion_sal]

        dataframe_continuo['Temperatura'][iestacion] = df_datos_tsg['temperatura_tsg'][indice_posicion_sal]
    
    
    return dataframe_continuo



## FUNCION PARA RECUPERAR DATOS DE LA BASE DE DATOS CENTOLO
def recupera_datos_centolo(df_datos_conexion,sensor,fecha_salida):
    
    # Genera datetimes de inicio y fin de la consulta a partir de la fecha de salida
    t_inicio = datetime.datetime.combine(fecha_salida,datetime.time(0,0,0))
    t_final  = datetime.datetime.combine(fecha_salida,datetime.time(23,59,0))
    
    # Conexion a la base de datos correspondiente
    con_engine         = 'postgresql://' + df_datos_conexion['usuario'][0] + ':' + df_datos_conexion['contrasena'][0] + '@' + df_datos_conexion['host'][0] + ':' + str(df_datos_conexion['puerto'][0]) + '/' + df_datos_conexion['base_datos'][0]
    conn_psql          = create_engine(con_engine)

    # Selecciona tabla a consultar según variable elegida
    if sensor == 'optodo':
        tabla_consulta             = 'lura_optodo'
        columna_fecha              = 'ofecha'
        nombre_original_variable   = ['bo2']
        nombre_modificado_variable = ['oxigeno']
    if sensor == 'tsg':
        tabla_consulta             = 'tsg_datos'        
        columna_fecha              = 'fecha'       
        nombre_original_variable   = ['sal00','t090c']
        nombre_modificado_variable = ['salinidad','temperatura_tsg']

    # Consulta los datos disponibles en la base de datos
    instruccion_SQL     = " SELECT * FROM " + tabla_consulta + " WHERE " + columna_fecha + " >= %(start)s AND " + columna_fecha + " <= %(end)s" 
    parametros_consulta = {'start': t_inicio, 'end': t_final}
    df_datos_centolo    = pandas.read_sql_query(instruccion_SQL, con=conn_psql, params=parametros_consulta)

    # Cierra conexion a base de datos
    conn_psql.dispose()

    # Reordena el dataframe según las fechas
    df_datos_centolo = df_datos_centolo.sort_values(by=[columna_fecha])
    
    # Cambia el nombre de las columnas correspondientes a la fecha/hora y la(s) variable(s) de medida
    df_datos_centolo = df_datos_centolo.rename(columns={columna_fecha: "tiempo"})
    for ivariable in range(len(nombre_original_variable)):
        df_datos_centolo = df_datos_centolo.rename(columns={nombre_original_variable[ivariable]: nombre_modificado_variable[ivariable]})
    
    # Re-define los índices para que esté ordenado según el tiempo
    indices_dataframe      = numpy.arange(0,df_datos_centolo.shape[0],1,dtype=int)
    df_datos_centolo['id'] = indices_dataframe
    df_datos_centolo.set_index('id',drop=True,append=False,inplace=True)
    
    return df_datos_centolo



## FUNCION PARA EXPORTAR LOS RESULTADOS A EXCEL
def exporta_resultados_excel(directorio_salida,fecha_salida,dataframe_datos_aft,dataframe_estaciones,dataframe_continuo,dataframe_datos_pco2,dataframe_botellero):
    
    archivo_excel = directorio_salida + '/CONTINUO_' + fecha_salida.strftime("%Y_%m_%d") + '.xlsx'
    writer = pandas.ExcelWriter(archivo_excel, engine='xlsxwriter')
    
    # DATOS DE pH
    if dataframe_datos_aft is not None:
        
        # Selecciona las columnas que interesa exportar del dataframe del AFT
        df_exporta = dataframe_datos_aft[["tiempo","latitude","longitude","estacion","pH_procesado","temperatura_aft","temperatura_tsg","salinidad","oxigeno",'pCO2_procesado']]
        
        # Genera un gráfico comparando las temperaturas del AFT y del TSG
        escala   = 0.0125
        min_temp = (1-escala)*min(min(df_exporta['temperatura_aft']),min(df_exporta['temperatura_tsg']))
        max_temp = (1+escala)*max(max(df_exporta['temperatura_aft']),max(df_exporta['temperatura_tsg']))
        
        fig, ax = plt.subplots()
            
        ax.set_xlim(min_temp, max_temp)
        ax.set_ylim(min_temp, max_temp)
        ax.set_xlabel('Temperatura TSG(ºC)', fontsize=10)
        ax.set_ylabel('Temperatura AFT(ºC)', fontsize=10)   
        plt.plot([min_temp,max_temp],[min_temp,max_temp],':k',linewidth=0.5)
        seaborn.scatterplot(data=df_exporta,x='temperatura_tsg', y='temperatura_aft', hue='estacion',sizes=(1, 8), linewidth=0.5, ax=ax)
        plt.grid(True)
        
        imagen_temp   = directorio_salida + '/TEMPERATURAS_' + fecha_salida.strftime("%Y_%m_%d") + '.png'
        plt.savefig(imagen_temp)
        plt.close('all')
        
        # Modifica los nombres de los encabezados para incluir las unidades
        df_exporta = df_exporta.rename(columns={"temperatura_aft": "temperatura AFT(degC)","temperatura_tsg": "temperatura tsg(degC)","salinidad": "salinidad(PSU)","oxigeno":"oxigeno optodo(µmol/kg)",'pCO2_procesado': 'pCO2(µatm)'})
               
        # Vuelca los datos de pH a una hoja Excel
#        writer = pandas.ExcelWriter(archivo_excel, engine='xlsxwriter')
        df_exporta.to_excel(writer, sheet_name='DATOS_pH')

        
        # Inserta el gráfico de temperaturas también en la excel
        #    workbook = writer.book
        worksheet = writer.sheets['DATOS_pH']
        worksheet.insert_image('N1', imagen_temp)
    

    
    
    # DATOS DEL MUESTREO CONTINUO
    
    # Elimina las columnas que no corresponden con el muestreo del continuo
    dataframe_continuo = dataframe_continuo.drop(columns=['Hora llegada','Hora salida','Prof (m)','Latitud','Longitud','tiempo_llegada','tiempo_salida','tiempo_muestreo','tiempo_cierre_botella','id_muestreo','id_estacion'])
    dataframe_continuo = dataframe_continuo.drop(columns=['oxigeno_media','oxigeno_desv','salinidad_media','salinidad_desv','pCO2_procesado_media','pCO2_procesado_desv','temperatura_tsg_media','temperatura_tsg_desv'])

    # Modifica los nombres de los encabezados para incluir las unidades
    dataframe_continuo = dataframe_continuo.rename(columns={"Hora continuo": "Hora muestreo continuo","O2": "oxigeno optodo(µmol/kg)","pCO2": "pCO2(µat)","Salinidad": "salinidad(PSU)","Temperatura": "temperatura tsg(degC)"})

    # Vuelca los datos de cada estación
    dataframe_continuo.to_excel(writer, sheet_name='MUESTREOS_CONTINUO')    
    
    
    # DATOS DEL pCO2
    
    if dataframe_datos_pco2 is not None:
        
        # Extrae las columnas que se desea exportar a un nuevo dataframe
        dataframe_co2_exporta = dataframe_datos_pco2[['tiempo','latitude','longitude','p_NDIR','p_in','Zero','Flush','Signal_raw','Signal_ref','T_gas','S2beam','S2beam_zero','Sdrift','Sprocesado','xCO2_procesado','pCO2_procesado','flag','temperatura_tsg','salinidad_tsg']]

        # Renombre algunas de las columnas
        dataframe_co2_exporta = dataframe_co2_exporta.rename(columns={'pCO2_procesado':'pCO2(µat)','temperatura_tsg':'Temperatura TSG(degC)','salinidad_tsg':'Salinidad TSG(PSU)'})

        # Vuelca los datos del continuo de pCO2
        dataframe_co2_exporta.to_excel(writer, sheet_name='pCO2') 
    
    
    # DATOS BOTELLERO
    if dataframe_botellero is not None:
        
        # Modifica el formato de la hora de cierre
        for idato in range(dataframe_botellero.shape[0]):
            dataframe_botellero['tiempo_cierre_botella'].iloc[idato] = dataframe_botellero['tiempo_cierre_botella'].iloc[idato].time()
        
        # Reordena y modifica los nombres de los encabezados 
        dataframe_botellero = dataframe_botellero[['Estación','tiempo_cierre_botella','oxigeno_continuo','oxigeno_roseta','pCO2_continuo','salinidad_continuo','salinidad_roseta','temperatura_continuo','temperatura_roseta']]
        dataframe_botellero = dataframe_botellero.rename(columns={"oxigeno_continuo": "oxigeno continuo(µmol/kg)","salinidad_continuo": "salinidad continuo(PSU)","temperatura_continuo": "temperatura continuo(degC)","pCO2_continuo": "pCO2 continuo(µat)",'salinidad_roseta':'salinidad roseta(PSU)','temperatura_roseta':'temperatura roseta(PSU)','oxigeno_roseta':'oxigeno roseta(µmol/kg)','tiempo_cierre_botella':'tiempo cierre botella superficie'})

        # Vuelca los datos de la comparacion continuo y botellero
        dataframe_botellero.to_excel(writer, sheet_name='MUESTREOS_SUPERFICIE') 
    
    
    # DATOS DE LAS DEMÁS VARIABLES
    
    # Elimina las columnas de fecha y tiempo en el dataframe de estaciones
    dataframe_estaciones = dataframe_estaciones.drop(columns=['Hora llegada','Hora salida','Hora continuo','tiempo_muestreo','id_muestreo','id_estacion','tiempo_cierre_botella'])

    # Modifica los nombres de los encabezados para incluir las unidades
    dataframe_estaciones = dataframe_estaciones.rename(columns={"oxigeno_media": "oxigeno optodo media(µmol/kg)","oxigeno_desv": "oxigeno optodo desv(µmol/kg)","salinidad_media": "salinidad media(PSU)","salinidad_desv": "salinidad desv(PSU)","pCO2_procesado_media":"pCO2 procesado media(µatm)","pCO2_procesado_desv":"pCO2 procesado desv(µatm)","temperatura_tsg_media":"temperatura tsg media(degC)","temperatura_tsg_desv":"temperatura tsg desv(degC)"})
    dataframe_estaciones = dataframe_estaciones.rename(columns={"tiempo_llegada": "Hora llegada","tiempo_salida": "Hora salida"})

		

    # Vuelca los datos de cada estación
    dataframe_estaciones.to_excel(writer, sheet_name='RESUMEN_ESTACIONES')
    
    # Añade los gráficos de cada variable
    worksheet = writer.sheets['RESUMEN_ESTACIONES']
    
    grafico_oxigeno = directorio_salida + '/oxigeno_' + fecha_salida.strftime("%Y_%m_%d")+ '.png'
    worksheet.insert_image('A10', grafico_oxigeno)
    
    if dataframe_datos_pco2 is not None:
        grafico_pCO2 = directorio_salida + '/pCO2_procesado_' +   fecha_salida.strftime("%Y_%m_%d")+ '.png'
        worksheet.insert_image('N10', grafico_pCO2)
    
    # Cierra la hoja Excel
    writer.save()
    
    
    
    
# FUNCION PARA INSERTAR LOS DATOS DEL AFT EN LA BASE DE DATOS CENTOLO\TERMOSALINOGRAFOS
def inserta_bd_datos_ph(datos_conexion,dataframe_datos_aft):

    engine = create_engine("postgresql://" + datos_conexion['usuario'][0] + ":" + datos_conexion['contrasena'][0] + "@" + datos_conexion['host'][0] + ":" + datos_conexion['puerto'][0] + "/" + datos_conexion['base_datos'][0])
    
    # Consulta los datos ya incluidos en la base de datos
    sql            = "SELECT * FROM ph_aft_datos"
    gdf_previo     = geopandas.read_postgis(sql, engine,geom_col='geometry')
    gdf_previo     = gdf_previo.set_crs("EPSG:4326")
    gdf_previo.crs = 'EPSG:4326'
    
    # Extrae un dataframe solo con las variables a introducir en la base de datos y ajusta su nombre
    df_exporta = dataframe_datos_aft[['tiempo','latitude','longitude','temperatura_aft','salinidad','pH_procesado']]
    df_exporta = df_exporta.rename(columns={"tiempo": "fecha","salinidad":"salinidad_tsg","pH_procesado":"ph"})
    
    
    # Convierte el dataframe con los datos del AFT en un geodataframe, para poder trabajar con geometrías
    gdf_aft     = geopandas.GeoDataFrame(df_exporta, geometry=geopandas.points_from_xy(df_exporta.longitude, df_exporta.latitude))
    gdf_aft     = gdf_aft.set_crs("EPSG:4326") # Ojo, la misma referencia que se definió en la tabla de CENTOLO\termosalinografos
    gdf_aft.crs = 'EPSG:4326'
    
    # Elimina los registros del dataframe con datos previos, del mismo instante que los nuevos datos
    for idato_nuevo in range(gdf_aft.shape[0]):
        gdf_previo = gdf_previo.drop(gdf_previo[gdf_previo.fecha == gdf_aft['fecha'][idato_nuevo]].index)
    
    # Une los dos dataframes y vuelve a convertir en geodataframe (la union resultante es un dataframe, no geodataframe)
    gdf_combinado = pandas.concat([gdf_previo, gdf_aft])
    gdf_combinado = geopandas.GeoDataFrame(gdf_combinado, crs="EPSG:4326",geometry='geometry')
    
    # Genera de nuevo la tabla, para mantener tipo de datos y esas cosas
    genera_tabla_ph_centolo(datos_conexion)
    
    # # Inserta el dataframe resultante de la unión en la base de datos
    gdf_combinado.to_postgis("ph_aft_datos", engine,if_exists = 'append')
    
 
    
# FUNCION PARA INSERTAR LOS DATOS DE PCO2 EN LA BASE DE DATOS CENTOLO\TERMOSALINOGRAFOS
def inserta_bd_datos_pco2(datos_conexion,dataframe_datos_pco2):

    engine = create_engine("postgresql://" + datos_conexion['usuario'][0] + ":" + datos_conexion['contrasena'][0] + "@" + datos_conexion['host'][0] + ":" + datos_conexion['puerto'][0] + "/" + datos_conexion['base_datos'][0])
        
    # Consulta los datos ya incluidos en la base de datos
    sql            = "SELECT * FROM pco2_datos"
    gdf_previo     = geopandas.read_postgis(sql, engine,geom_col='geometry')
    gdf_previo     = gdf_previo.set_crs("EPSG:4326")
    gdf_previo.crs = 'EPSG:4326'
    
    # Extrae un dataframe solo con las variables a introducir en la base de datos y ajusta su nombre
    df_exporta = dataframe_datos_pco2[['tiempo','latitude','longitude','p_NDIR','p_in','Zero','Flush','Signal_raw','Signal_ref','T_gas','xCO2_procesado','pCO2_procesado']]
    df_exporta = df_exporta.rename(columns={"tiempo": "fecha"})
    
    # Cambia los nombres de las columnas a minusculas para evitar errores 
    listado_columnas   = df_exporta.columns.tolist()
    listado_columnas   = [x.lower() for x in listado_columnas]
    df_exporta.columns = listado_columnas
    
    # Convierte el dataframe con los datos del pCO2 en un geodataframe, para poder trabajar con geometrías
    gdf_pco2     = geopandas.GeoDataFrame(df_exporta, geometry=geopandas.points_from_xy(df_exporta.longitude, df_exporta.latitude))
    gdf_pco2     = gdf_pco2.set_crs("EPSG:4326") # Ojo, la misma referencia que se definió en la tabla de CENTOLO\termosalinografos
    gdf_pco2.crs = 'EPSG:4326'
    
    # Elimina los registros del dataframe con datos previos, del mismo instante que los nuevos datos
    for idato_nuevo in range(gdf_pco2.shape[0]):
        gdf_previo = gdf_previo.drop(gdf_previo[gdf_previo.fecha == gdf_pco2['fecha'][idato_nuevo]].index)
    
    # Une los dos dataframes y vuelve a convertir en geodataframe (la union resultante es un dataframe, no geodataframe)
    gdf_combinado = pandas.concat([gdf_previo, gdf_pco2])
    gdf_combinado = geopandas.GeoDataFrame(gdf_combinado, crs="EPSG:4326",geometry='geometry')
    
    # Genera de nuevo la tabla, para mantener tipo de datos y esas cosas
    genera_tabla_pco2_centolo(datos_conexion)
    
    # Inserta el dataframe resultante de la unión en la base de datos
    gdf_combinado.to_postgis("pco2_datos", engine,if_exists = 'append')





    # nombre_tabla = 'pco2_datos'
    
    # # Borra la table si ya existía
    # instruccion_sql = 'DROP TABLE IF EXISTS ' + nombre_tabla + ' CASCADE;'
    # cursor.execute(instruccion_sql)
    # conn.commit()
    
    # # Crea la tabla de nuevo
    # listado_variables = ('(fecha TIMESTAMP WITHOUT TIME ZONE,'
    # 'latitude NUMERIC (6, 4),'
    # 'longitude NUMERIC (6, 4),'
    # 'geometry GEOMETRY (GEOMETRY, 4326) DEFAULT NULL,'  
    # 'p_NDIR NUMERIC (7, 3),'
    # 'p_in NUMERIC (7, 3),'
    # 'Zero int,'
    # 'Flush int,'
    # 'Signal_raw int,'
    # 'Signal_ref int,'
    # 'T_gas NUMERIC (5, 3),'    
    # 'xCO2_procesado NUMERIC (7, 3),'
    # 'pCO2_procesado NUMERIC (7, 3)'




    

# dt_optodo = (dataframe_datos_optodo['tiempo'][1]-dataframe_datos_optodo['tiempo'][0]).total_seconds()
# dt_tsg    = (dataframe_datos_tsg['tiempo'][1]-dataframe_datos_tsg['tiempo'][0]).total_seconds()

# ratio_tsg = int(dt_tsg/dt_optodo)

# dataframe_datos_optodo['salinidad']   = numpy.zeros(dataframe_datos_optodo.shape[0])
# dataframe_datos_optodo['temperatura'] = numpy.zeros(dataframe_datos_optodo.shape[0])
# dataframe_datos_optodo['po2_calc']    = numpy.zeros(dataframe_datos_optodo.shape[0])
# dataframe_datos_optodo['bo2_calc']    = numpy.zeros(dataframe_datos_optodo.shape[0])

# # Coeficientes
# coef_a = 1
# coef_b = 1
# coef_c = 1
# coef_d = 1

# coef_c0 = 1
# coef_c1 = 1
# coef_c2 = 1
# coef_c3 = 1
# coef_c4 = 1
# coef_c5 = 1
# coef_c6 = 1 

# A0 = 5.80818
# A1 = 3.20684
# A2 = 4.11890
# A3 = 4.93846
# A4 = 1.01567
# A5 = 1.41575
# B0 = -7.01211*(10**-3)
# B1 = -7.25958*(10**-3)
# B2 = -7.93334*(10**-3)
# B3 = -5.54491*(10**-3)
# C0 = -1.32412*(10**-7)

# # Encuentra la posicion (indice) en la que comienzan a solparse los tiempos
# if dataframe_datos_optodo['tiempo'][0] > dataframe_datos_tsg['tiempo'][0]:
#     dif_tiempos             = numpy.asarray(abs(dataframe_datos_optodo['tiempo'][0] - dataframe_datos_tsg['tiempo']))
#     indice_posicion_llegada = numpy.argmin(dif_tiempos)
# else:
#     indice_posicion_llegada = 0

# # Calcula el oxígeno de cada registro
# for idato_optodo in range(dataframe_datos_optodo.shape[0]):
        
#     # Busca en el TSG la salinidad correspondiente al instante de medida
#     dataframe_datos_optodo['salinidad'][idato_optodo] = dataframe_datos_tsg['sal00'][indice_posicion_llegada+round(idato_optodo/ratio_tsg)]
        
#     # Calcula la temperatura según la intensidad de la señal
#     temp_raw = dataframe_datos_optodo['Temperature raw'][idato_optodo]
#     t_opt    = 1/(coef_a + coef_b*(math.log(temp_raw)) + coef_c*((math.log(temp_raw))**2) + coef_d*((math.log(temp_raw))**3))
#     dataframe_datos_optodo['temperatura'][idato_optodo] = t_opt

#     # Calcula la pO2
#     pO2 = (((1+t_opt*coef_c3)/(coef_c4+coef_c5*dataframe_datos_optodo['Dphi'][idato_optodo]+coef_c6*(dataframe_datos_optodo['Dphi'][idato_optodo]**2)))-1) / (coef_c0 + coef_c1*t_opt + coef_c2*(t_opt**2)) 
#     dataframe_datos_optodo['po2_calc'][idato_optodo] = pO2
    
#     # Ts
#     ts = math.log((571.3-t_opt)/(t_opt))
    
#     expo = A0 + A1*ts + A2*(ts**2) + A3*(ts**3) + A4*(ts**4) + A5*(ts**5) + dataframe_datos_optodo['salinidad'][idato_optodo]*(B0 + B1*ts + B2*(ts**2) + B3*(ts**3)) + C0*(dataframe_datos_optodo['salinidad'][idato_optodo]**2)
#     c_0   = math.exp(expo) 
    
#     expo = 24.4543 - 67.4509*(100/t_opt)-4.8489*math.log(t_opt/100) - 0.000544*dataframe_datos_optodo['salinidad'][idato_optodo]
#     ph20 = math.exp(expo)
    
#     dataframe_datos_optodo['bo2_calc'][idato_optodo] = (pO2*c_0)/(0.20946*(1013.25-(ph20*1013.25)))  

# ## FUNCION DE LECTURA DEL ARCHIVO BRUTO DEL AFT
# def lectura_aft(archivo_aft):

#     # Parámetros
#     num_rep_blancos  = 4
#     num_rep_descarta = 6
#     to               = datetime.datetime(1904,1,1)
    
#     num_rep_ph       = int((108-num_rep_blancos*4-num_rep_descarta*4)/4)
    
#     # pre-dimensiona matriz en el que almacenar los resultados
#     almacena_valores = numpy.zeros((1,114))
    
#     # Abre el archivo como lectura
#     lectura_archivo = open(archivo_aft, "r")  
#     datos_archivo = lectura_archivo.readlines()
    
#     # Itera en cada una de las líneas
#     for ilinea in range(len(datos_archivo)):
        
#         texto_linea = datos_archivo[ilinea]
    
#         # Lee parametros del AFT
#         if texto_linea[0:5] == 'Cal1:' :
#             mol_abs_a_434 = float(texto_linea[6:-1])
#         if texto_linea[0:5] == 'Cal2:' :
#             mol_abs_b_434= float(texto_linea[6:-1])
#         if texto_linea[0:5] == 'Cal3:' :
#             mol_abs_a_578= float(texto_linea[6:-1])
#         if texto_linea[0:5] == 'Cal4:' :
#             mol_abs_b_578= float(texto_linea[6:-1])       
#         if texto_linea[0:5] == 'Cal5:' :
#             temp_offset = float(texto_linea[6:-1]     )
    
#         # Lee las medidas, aprovechando el encabezado de "10".        
#         if texto_linea[0:2] == '10' :
#             valores = [eval(i) for i in texto_linea.split()] 
    
#             # Añade los valores medidos a la matriz
#             almacena_valores = numpy.append(almacena_valores, [valores], axis=0)
            
#     # Cierra el archivo
#     lectura_archivo.close()
    
#     # Elimina la primera fila, creada al pre-dimensionar la matriz
#     almacena_valores = numpy.delete(almacena_valores, 0, 0)
 
#     # Determina el instante de tiempo de cada medida
#     tiempos = [None]*almacena_valores.shape[0]
#     for idato in range(almacena_valores.shape[0]):
#         tiempos[idato] = to + datetime.timedelta(seconds=almacena_valores[idato,1])
        
#     # Genera un dataframe con las constantes del AFT
#     parametros_AFT = pandas.DataFrame([[mol_abs_a_434,mol_abs_b_434,mol_abs_a_578,mol_abs_b_578,temp_offset]], columns=['mol_abs_a_434','mol_abs_b_434','mol_abs_a_578','mol_abs_b_578','temp_offset'])
    
#     return almacena_valores,parametros_AFT,tiempos

# ## FUNCION PARA EXTRAER LOS DATOS DE UNA VARIABLE EN LAS ESTACIONES MUESTREADAS
# def extrae_datos_estaciones(dataframe_estaciones,dataframe_datos,dataframe_variables,variable):

#     # Busca las unidades de la variable
#     unidades = dataframe_variables['unidades'][dataframe_variables['variable']==variable].iloc[0]
    
#     # Genera columnas en el dataframe de estaciones para guardar la variable
#     dataframe_estaciones[variable+'_media'] = [None]*dataframe_estaciones.shape[0]
#     dataframe_estaciones[variable+'_desv']  = [None]*dataframe_estaciones.shape[0]
    
#     # Crea imagen con 4 subplots
#     fig, axs = plt.subplots(dataframe_estaciones.shape[0],1)
    
#     titulo  = 'Medidas ' + variable + ' salida ' + fecha_salida.strftime("%m/%d/%Y")
#     axs[0].set_title(titulo)
    
#     # Itera en cada estacion
#     for iestacion  in range(dataframe_estaciones.shape[0]):
    
        
        
#         # Encuentra la posicion (indice) del dataframe correspondiente a la llegada de la estacion
#         dif_tiempos             = numpy.asarray(abs(dataframe_estaciones['tiempo_llegada'][iestacion] - dataframe_datos['tiempo']))
#         indice_posicion_llegada = numpy.argmin(dif_tiempos)
    
#         # Encuentra la posicion (indice) del dataframe correspondiente a la salida de la estacion
#         dif_tiempos             = numpy.asarray(abs(dataframe_estaciones['tiempo_salida'][iestacion] - dataframe_datos['tiempo']))
#         indice_posicion_salida  = numpy.argmin(dif_tiempos)
    
#         # comprobacion por si no hay valores en la estacion buscada    
#         if indice_posicion_llegada == indice_posicion_salida:
#             dataframe_estaciones[variable+'_media'][iestacion] = None
#             dataframe_estaciones[variable+'_desv'][iestacion]  = None
            
#         else:
    
#             # Extrae los valores medidos en la estacion 
#             valores_registrados     = dataframe_datos[variable][indice_posicion_llegada:indice_posicion_salida]
#             tiempos_registro        = dataframe_datos['tiempo'][indice_posicion_llegada:indice_posicion_salida]
        
#             dataframe_estaciones[variable+'_media'][iestacion] = valores_registrados.mean()
#             dataframe_estaciones[variable+'_desv'][iestacion]  = valores_registrados.std()
        
#             # Representa los valores registrados en cada estación
#             axs[iestacion].plot(tiempos_registro,valores_registrados)
            
#             # Representa el valor promedio
#             axs[iestacion].plot([tiempos_registro.iloc[0],tiempos_registro.iloc[-1]],[valores_registrados.mean(),valores_registrados.mean()],':k')    
        
#             ### Ajusta formatos del grafico ###
            
#             # Eje x sólo para los intervalos de tiempo de cada estacion
#             axs[iestacion].set_xlim([min(tiempos_registro), max(tiempos_registro)])
#             formato     = DateFormatter("%H:%M")
#             axs[iestacion].xaxis.set_major_formatter(formato)
            
#             # Eje y entre valores máximoy mínimo
#             num_ticks   = 3
#             dt_y        = (max(valores_registrados)-min(valores_registrados))/(num_ticks-1)
#             axs[iestacion].yaxis.set_major_locator(plt.MaxNLocator(num_ticks))
#             axs[iestacion].set_yticks(numpy.arange(min(valores_registrados), max(valores_registrados)+dt_y, step=dt_y))
#             axs[iestacion].set_ylim([min(valores_registrados), max(valores_registrados)])
            
#             # Recuadro con nombre de estacion y media
#             textstr = '\n'.join((
#                 r'Estacion ' + dataframe_estaciones['Estación'][iestacion],
#                 r'$\mu=%.2f$' % (valores_registrados.mean(), ) + '  '  + '$\sigma=%.2f$' % (valores_registrados.std(), )))
#             props = dict(boxstyle='round', facecolor='white', alpha=0.5)
#             axs[iestacion].text(0.775, 0.95, textstr, transform=axs[iestacion].transAxes,fontsize=10,verticalalignment='top', bbox=props)
    
#     # Adapta el tamaño de la imagen y el nombre de los ejes
#     fig.set_size_inches(10, 15.5)
#     texto_ejey   = variable + '(' + unidades + ')'
#     fig.supylabel(texto_ejey)
#     fig.supxlabel('Hora')
#     fig.tight_layout(pad=1)
    
#     # Guarda la imagen
#     nombre_archivo = directorio_salida + '/' + variable + fecha_salida.strftime("%Y_%m_%d")+ '.png'
#     fig.savefig(nombre_archivo, bbox_inches='tight')

#     plt.close('all')

#     return dataframe_estaciones






















###     1 grafica para cada estacion


# ## FUNCION PARA EXTRAER LOS DATOS DE UNA VARIABLE EN LAS ESTACIONES MUESTREADAS
# def extrae_datos_estaciones(dataframe_estaciones,dataframe_datos,variable,io_plot):

#     # Busca las unidades de la variable
#     if variable == 'pH_procesado':
#         unidades = 'uds'
#     if variable == 'oxigeno':
#         unidades = '\u03BCmol/kg'
#     if variable == 'salinidad':
#         unidades = 'psu'
#     if variable == 'pCO2':
#         unidades = '\u03BCatm'
    
#     # Genera columnas en el dataframe de estaciones para guardar la variable
#     dataframe_estaciones[variable+'_media'] = [None]*dataframe_estaciones.shape[0]
#     dataframe_estaciones[variable+'_desv']  = [None]*dataframe_estaciones.shape[0]
    
#     # Itera en cada estacion
#     for iestacion  in range(dataframe_estaciones.shape[0]):
            
#         # Encuentra la posicion (indice) del dataframe correspondiente a la llegada de la estacion
#         dif_tiempos             = numpy.asarray(abs(dataframe_estaciones['tiempo_llegada'][iestacion] - dataframe_datos['tiempo']))
#         indice_posicion_llegada = numpy.argmin(dif_tiempos)
    
#         # Encuentra la posicion (indice) del dataframe correspondiente a la salida de la estacion
#         dif_tiempos             = numpy.asarray(abs(dataframe_estaciones['tiempo_salida'][iestacion] - dataframe_datos['tiempo']))
#         indice_posicion_salida  = numpy.argmin(dif_tiempos)
    
#         # comprobacion por si no hay valores en la estacion buscada    
#         if indice_posicion_llegada == indice_posicion_salida:
#             dataframe_estaciones[variable+'_media'][iestacion] = None
#             dataframe_estaciones[variable+'_desv'][iestacion]  = None
            
#         else:
    
#             # Extrae los valores medidos en la estacion 
#             valores_registrados     = dataframe_datos[variable][indice_posicion_llegada:indice_posicion_salida]
#             tiempos_registro        = dataframe_datos['tiempo'][indice_posicion_llegada:indice_posicion_salida]
        
#             dataframe_estaciones[variable+'_media'][iestacion] = valores_registrados.mean()
#             dataframe_estaciones[variable+'_desv'][iestacion]  = valores_registrados.std()
        
#             if io_plot==1:
        
#                 fig, ax = plt.subplots()
                
#                 # Representa los valores registrados en cada estación
#                 ax.plot(tiempos_registro,valores_registrados)
                
#                 # Representa el valor promedio
#                 ax.plot([tiempos_registro.iloc[0],tiempos_registro.iloc[-1]],[valores_registrados.mean(),valores_registrados.mean()],':k')    
            
#                 ### Ajusta formatos del grafico ###
                
#                 # Eje x sólo para los intervalos de tiempo de cada estacion
#                 ax.set_xlim([min(tiempos_registro), max(tiempos_registro)])
#                 formato     = DateFormatter("%H:%M")
#                 ax.xaxis.set_major_formatter(formato)
                
#                 # Eje y entre valores máximoy mínimo
#                 num_ticks   = 3
#                 dt_y        = (max(valores_registrados)-min(valores_registrados))/(num_ticks-1)
#                 ax.yaxis.set_major_locator(plt.MaxNLocator(num_ticks))
#                 ax.set_yticks(numpy.arange(min(valores_registrados), max(valores_registrados)+dt_y, step=dt_y))
#                 ax.set_ylim([min(valores_registrados), max(valores_registrados)])
                
#                 # Recuadro con nombre de estacion y media
#                 textstr = '\n'.join((
#                     r'Estacion ' + dataframe_estaciones['Estación'][iestacion],
#                     r'$\mu=%.2f$' % (valores_registrados.mean(), ) + '  '  + '$\sigma=%.2f$' % (valores_registrados.std(), )))
#                 props = dict(boxstyle='round', facecolor='white', alpha=0.5)
#                 ax.text(0.775, 0.95, textstr, transform=ax.transAxes,fontsize=10,verticalalignment='top', bbox=props)
        
#                 # Adapta el tamaño de la imagen y el nombre de los ejes
#                 fig.set_size_inches(10, 5)
#                 texto_ejey   = variable + '(' + unidades + ')'
#                 fig.supylabel(texto_ejey)
#                 fig.supxlabel('Hora')
#                 fig.tight_layout(pad=1)
                
#                 # Guarda la imagen
#                 nombre_archivo = directorio_salida + '/' + variable + '_' + dataframe_estaciones['Estación'][iestacion] + '_' + fecha_salida.strftime("%Y_%m_%d")+ '.png'
#                 fig.savefig(nombre_archivo, bbox_inches='tight')
            
#                 plt.close('all')

#     return dataframe_estaciones