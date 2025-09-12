# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 14:47:40 2022

@author: ifraga
"""
import pandas
import numpy
import os
import matplotlib.pyplot as plt
import imageio.v3 as iio
import datetime



        
###################################################################
#### FUNCION PARA GENERAR IMÁGENES CON LOS PERFILES REALIZADOS ####
###################################################################

def graficos_perfiles(directorio_trabajo,listado_variables,listado_unidades,tipo_dato_representa):
    
    ### CARGA LA INFORMACION DEL FLUORIMETRO
    archivo_datos_combinado = directorio_trabajo + '/Datos_combinados_fluorimetro' 
    datos_fluorimetro       = pandas.read_pickle(archivo_datos_combinado)
    
    ### MANTÉN SÓLO LOS DATOS CORRESPONDIENTE A PERFILES (ETAPA = 3)
    datos_fluorimetro       = datos_fluorimetro[datos_fluorimetro['etapa_perfilador']==3] 
    
    ### COMPRUEBA SI YA EXISTEN LOS DIRECTORIOS EN LOS QUE GUARDAR LAS IMAGENES GENERADAS
    directorio_resultados = directorio_trabajo + '/IMAGENES'
    os.makedirs(directorio_resultados, exist_ok=True)         
    
    ### EXTRAE LISTADO DE PERFILES Y RANGO DE PROFUNDIDADES
    listado_perfiles = datos_fluorimetro['id_perfil'].unique()
    min_prof = int(0.9*min(datos_fluorimetro['presion']))
    max_prof = int(1.1*max(datos_fluorimetro['presion']))
    
    ### CAMBIA LAS VARIABLES DE TRABAJO A LAS FILTRADAS 
    listado_variables_representa = [None]*len(listado_variables)
    for ivariable in range(len(listado_variables)): 
        listado_variables_representa[ivariable] =  listado_variables[ivariable] + '_' + tipo_dato_representa 
    
    ### EXTRAE LOS RANGOS DE CADA VARIABLE Y COMPRUEBA SI EXISTEN DIRECTORIOS PARA GUARDAR LAS IMAGENES
    min_valor = [None]*3
    max_valor = [None]*3
    
    for ivariable in range(len(listado_variables)): 
        
        # Comprueba que hay un directorio con el nombre de la variable
        directorio_variable = directorio_resultados + '/' + listado_variables[ivariable]
        os.makedirs(directorio_variable, exist_ok=True)
    
        if listado_variables[ivariable] == 'TRYP':
            # Extrae los rangos de variacion
            min_valor[ivariable] = int(1*min(datos_fluorimetro[listado_variables_representa[ivariable]]))
            max_valor[ivariable] = int(1*max(datos_fluorimetro[listado_variables_representa[ivariable]]))
        
        else:
            # Extrae los rangos de variacion
            min_valor[ivariable] = int(0.9*min(datos_fluorimetro[listado_variables_representa[ivariable]]))
            max_valor[ivariable] = int(1.1*max(datos_fluorimetro[listado_variables_representa[ivariable]]))
    
        #for iperfil in range(len(listado_perfiles)):
        
    # GENERA LOS GRAFICOS DE CADA PERFIL        
    for iperfil in range(len(listado_perfiles)):        
            
        subset_perfil = datos_fluorimetro[datos_fluorimetro['id_perfil']==listado_perfiles[iperfil]]
        
        for ivariable in range(len(listado_variables)):

            nombre_archivo = directorio_resultados + '/' + listado_variables[ivariable]  + '/perfil_' + str(iperfil).zfill(2) + '.png'
            
            
            fig, ax = plt.subplots(figsize=(20/2.54, 20/2.54))
        
            # Textos
            #ax.set_title('Perfil ' + variable + ' ' + df_perfil['tiempo'].iloc[0].strftime('%Y-%m-%d') , fontsize=16)
            ax.text(0.75, 0.9, 'Fecha:'+ subset_perfil['tiempo_corregido'].iloc[0].strftime('%d/%m/%y'), transform=ax.transAxes, fontsize=14)
            ax.text(0.75, 0.82, 'Hora:'+ subset_perfil['tiempo_corregido'].iloc[0].strftime('%H:%M:%S'), transform=ax.transAxes, fontsize=14)
            #Representacion
            ax.grid(True)
            ax.plot(subset_perfil[listado_variables_representa[ivariable]],subset_perfil['presion'],'ro',markersize = 3,label='Observado')
            ax.set_xlim(min_valor[ivariable],max_valor[ivariable])
            ax.set_ylim(min_prof,max_prof)
            ax.set_yticks(list(numpy.arange(min_prof,max_prof,1)))
            ax.set_xlabel(listado_variables[ivariable]+' (' + listado_unidades[ivariable] + ')', fontsize=16)
            ax.set_ylabel('Presion (m)', fontsize=16)
            ax.tick_params(axis='both', which='major', labelsize=14)
            ax.invert_yaxis()
            # Guardado de la imagen
            fig.savefig(nombre_archivo)   # save the figure to file
            plt.close(fig)
            
            
            
###################################################################
#### FUNCION PARA GENERAR GIF CON LA EVOLUCION DE LOS PERFILES ####
###################################################################

def gif_evolucion_perfiles(directorio_trabajo,listado_variables,tipo_dato_representa):            
            
    ### COMPRUEBA SI YA EXISTEN LOS DIRECTORIOS EN LOS QUE GUARDAR LAS IMAGENES GENERADAS
    directorio_resultados = directorio_trabajo + '/IMAGENES'
    os.makedirs(directorio_resultados, exist_ok=True) 
    
    # GENERA UNA ANIMACION CON LA EVOLUCION DE LOS PERFILES
    for ivariable in range(len(listado_variables)):
        
        directorio_resultados = directorio_trabajo + '/IMAGENES/' + listado_variables[ivariable] 
        
        listado_perfiles = [f for f in os.listdir(directorio_resultados) if f.endswith('.png')]
        
        if len(listado_perfiles) > 0:
        
            archivo_gif = directorio_resultados + '/Evolucion_' + tipo_dato_representa +'.gif'
        
            imagenes = []

            for iperfil in range(len(listado_perfiles)):

                nombre_archivo = directorio_resultados + '/' + listado_perfiles[iperfil]
        
                imagenes.append(iio.imread(nombre_archivo))
                iio.imwrite(archivo_gif, imagenes, duration = 3*len(listado_perfiles))
    
        else:
            
            print('No hay perfiles de la variable ',listado_variables[ivariable])
            



#################################################################
#### FUNCION PARA REPRESENTAR LA EVOLUCION TEMPORAL COMPLETA ####
#################################################################

def serie_temporal(directorio_trabajo,listado_variables,listado_unidades,tipo_dato_representa):            
            
    ### CARGA LA INFORMACION DEL FLUORIMETRO
    archivo_datos     = directorio_trabajo + '/Datos_filtrados_fluorimetro' 
    datos_fluorimetro = pandas.read_pickle(archivo_datos)
       
    ### COMPRUEBA SI YA EXISTEN LOS DIRECTORIOS EN LOS QUE GUARDAR LAS IMAGENES GENERADAS
    directorio_resultados = directorio_trabajo + '/IMAGENES'
    os.makedirs(directorio_resultados, exist_ok=True)         
            
    for ivariable in range(len(listado_variables)):
    
        ### CAMBIA LAS VARIABLES DE TRABAJO A LAS FILTRADAS 
        variable_representa =  listado_variables[ivariable] + '_' + tipo_dato_representa     
    
        ### GENERA GRAFICO
        nombre_archivo = directorio_resultados + '/' + listado_variables[ivariable]  + '/Serie_temporal.tiff'
        
        fig, ax = plt.subplots(figsize=(40/2.54, 20/2.54))
    
        # Textos
        #ax.set_title('Serie temporal ' + variable_representa , fontsize=16)
        #Representacion
        ax.grid(True)
        ax.plot(datos_fluorimetro['tiempo_corregido'],datos_fluorimetro[variable_representa],'ro',markersize = 3)
        ax.set_xlabel('Tiempo', fontsize=16)
        ax.set_ylabel(listado_variables[ivariable]+' (' + listado_unidades[ivariable] + ')', fontsize=16)
        ax.tick_params(axis='both', which='major', labelsize=14)
        ax.invert_yaxis()
        # Guardado de la imagen
        fig.savefig(nombre_archivo)   # save the figure to file
        plt.close(fig)


########################################################################
#### FUNCION PARA REPRESENTAR LA EVOLUCION TEMPORAL DE LOS PERFILES ####
########################################################################

def serie_temporal_perfiles(directorio_trabajo,listado_variables,tipo_dato_representa,fecha_despliegue): 

    ### CARGA LA INFORMACION DEL FLUORIMETRO
    archivo_datos     = directorio_trabajo + '/Datos_combinados_fluorimetro' 
    datos_fluorimetro = pandas.read_pickle(archivo_datos)
       
    #datos_fluorimetro = datos_fluorimetro.iloc[::200]
    
    ### COMPRUEBA SI YA EXISTEN LOS DIRECTORIOS EN LOS QUE GUARDAR LAS IMAGENES GENERADAS
    directorio_resultados = directorio_trabajo + '/IMAGENES'
    os.makedirs(directorio_resultados, exist_ok=True)         
            
    for ivariable in range(len(listado_variables)):
        
        ### CAMBIA LAS VARIABLES DE TRABAJO A LAS FILTRADAS 
        variable_representa =  listado_variables[ivariable] + '_' + tipo_dato_representa     
    
        ### GENERA GRAFICO
        nombre_archivo = directorio_resultados + '/' + listado_variables[ivariable]  + '/Serie_temporal_perfiles_' + listado_variables[ivariable] + '_' + str(fecha_despliegue) +  '.tiff'
        fig, ax = plt.subplots(figsize=(40/2.54, 20/2.54))
        #Representacion
        ax.grid(True)
        scatter = ax.scatter(datos_fluorimetro['tiempo_corregido'], datos_fluorimetro['presion'], c=datos_fluorimetro[variable_representa], cmap="Spectral_r",s=4)
        ax.legend(*scatter.legend_elements(),loc="center left",title=listado_variables[ivariable],bbox_to_anchor=(1, 0.5))
        ax.set_xlabel('Tiempo', fontsize=16)
        ax.set_ylabel('Presion(m)', fontsize=16)
        ax.tick_params(axis='both', which='major', labelsize=14)
        ax.invert_yaxis()
        ax.set_title('Evolucion ' + listado_variables[ivariable] , fontsize=16)
        # Guardado de la imagen
        fig.savefig(nombre_archivo)   # save the figure to file
        plt.close(fig)
        
############################################################################################
#### FUNCION PARA REPRESENTAR LA EVOLUCION TEMPORAL DE LOS PERFILES CON DATOS DE LLUVIA ####
############################################################################################

def serie_temporal_perfiles_lluvia(directorio_general,directorio_trabajo,listado_variables,tipo_dato_representa,fecha_despliegue):         
    

    ### CARGA LA INFORMACION DEL FLUORIMETRO
    archivo_datos     = directorio_trabajo + '/Datos_combinados_fluorimetro' 
    datos_fluorimetro = pandas.read_pickle(archivo_datos)
       
    ### CARGA LA INFORMACION DE LLUVIA EN EL PUNTO RELACIONADO    
    archivo_lluvia = directorio_general + '/LLUVIA.csv'
    datos_lluvia = pandas.read_csv(archivo_lluvia,skiprows=2,sep=';')
    # Convierte fechas
    datos_lluvia['tiempo'] = pandas.to_datetime(datos_lluvia['Fecha'], format='%d/%m/%Y %H:%M')
    datos_lluvia = datos_lluvia[['tiempo','Valor']]
    # Conserva los datos del periodo de tiempo del fondeo del fluorimetro
    datos_lluvia = datos_lluvia[(datos_lluvia['tiempo']>min(datos_fluorimetro['tiempo_corregido'])) & (datos_lluvia['tiempo']<max(datos_fluorimetro['tiempo_corregido']))]
    
    
    ### CARGA LA INFORMACION DEL INDICE DE AFLORAMIENTO  
    archivo_upwelling = directorio_general + '/UI_HORARIO.csv'
    datos_upwelling = pandas.read_csv(archivo_upwelling,sep=',')
    # Convierte fechas
    datos_upwelling['tiempo'] = None
    for idato in range(datos_upwelling.shape[0]):
        datos_upwelling['tiempo'].iloc[idato] = datetime.datetime(datos_upwelling['ano'].iloc[idato],datos_upwelling['mes'].iloc[idato],datos_upwelling['dia'].iloc[idato],datos_upwelling['hora'].iloc[idato])
    
    
    ### COMPRUEBA SI YA EXISTEN LOS DIRECTORIOS EN LOS QUE GUARDAR LAS IMAGENES GENERADAS
    directorio_resultados = directorio_trabajo + '/IMAGENES'
    os.makedirs(directorio_resultados, exist_ok=True)         
            
    for ivariable in range(len(listado_variables)): 
        
        ### CAMBIA LAS VARIABLES DE TRABAJO A LAS FILTRADAS 
        variable_representa =  listado_variables[ivariable] + '_' + tipo_dato_representa     
    
        ### GENERA GRAFICO
        
        fecha_inicio_despliegue = min(datos_fluorimetro['tiempo_corregido']).date()
        fecha_final_despliegue  = max(datos_fluorimetro['tiempo_corregido']).date()
    
        #Representacion
        fig, (ax1, ax2, ax3) = plt.subplots(3,figsize=(40/2.54, 20/2.54),sharex=True, gridspec_kw={'height_ratios': [1, 1, 3]})
    
        # Gráfico superior, lluvia
        ax1.bar(datos_lluvia['tiempo'],datos_lluvia['Valor'] ,width=0.01)
        ax1.set_xlim(fecha_inicio_despliegue, fecha_final_despliegue)
        ax1.set_ylabel('Lluvia (mm)', fontsize=16)
        ax1.tick_params(axis='both', which='major', labelsize=14)
        
        # Gráfico intermedio, UI
        ax2.plot(datos_upwelling['tiempo'],datos_upwelling['ui'],'.-b')
        ax2.set_xlim(fecha_inicio_despliegue, fecha_final_despliegue)
        ax2.set_ylabel('UI', fontsize=16)
        ax2.tick_params(axis='both', which='major', labelsize=14)
        ax2.axhline(0)
        
        # Gráfico inferior, variable
        ax3.grid(True)
        scatter = ax3.scatter(datos_fluorimetro['tiempo_corregido'], datos_fluorimetro['presion'], c=datos_fluorimetro[variable_representa], cmap="Spectral_r",s=4)
        ax3.legend(*scatter.legend_elements(),loc="center left",title=listado_variables[ivariable],bbox_to_anchor=(1, 0.5))
        ax3.set_xlabel('Tiempo', fontsize=16)
        ax3.set_ylabel('Presion(m)', fontsize=16)
        ax3.tick_params(axis='both', which='major', labelsize=14)
        ax3.invert_yaxis()
        
        # Guardado de la imagen
        nombre_archivo = directorio_resultados + '/' + listado_variables[ivariable]  + '/Serie_temporal_perfiles_factores_' + listado_variables[ivariable] + '_' + str(fecha_despliegue) +  '.tiff'

        fig.savefig(nombre_archivo)   # save the figure to file
        plt.close(fig)