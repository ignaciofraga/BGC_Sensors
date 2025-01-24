# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 08:05:55 2022

@author: ifraga
"""
import streamlit as st
import datetime
import pandas 
from io import BytesIO





st.title("Procesado de datos del perfilador y fluorimetro")

           
# Formulario con los archivos de entrada y diferencia de tiempos perfilador-fluorimetro            
with st.form("Formulario", clear_on_submit=False):

    archivo_datos_perfilador  = st.file_uploader("Archivo con los datos del PERFILADOR", accept_multiple_files=False)

    archivo_datos_fluorimetro  = st.file_uploader("Archivo con los datos del FLUORIMETRO", accept_multiple_files=False)

    col1, col2 = st.columns(2,gap="small")
    with col1:
        offset_fluorimetro = st.number_input('Incremento de tiempo fluorimetro (segundos):',value=0.5)
    with col2:
        max_dt_tiempo = st.number_input('Máxima diferencia de tiempo (segundos):',value=10)        
        
    io_envio                    = st.form_submit_button("Procesar los archivos subidos")

if io_envio is True:
    
    # Lectura del archivo con los resultados del AA
    datos_perfilador       = pandas.read_excel(archivo_datos_perfilador)            
                  

    ## PROCESADO DE LA INFORMACION
    texto_estado = 'Procesando los archivos subidos '
    with st.spinner(texto_estado):
        
        datos_exporta = datos_perfilador



        # Mensaje de aviso 
        texto_exito = 'Archivos procesados correctamente'
        st.success(texto_exito)
        
        #else:
            #texto_error = 'El participante introducido ya se encuentra en la base de datos '
            #st.warning(texto_error, icon="⚠️") 



        ## EXPORTA LOS RESULTADOS

        # Botón para descargar la información como Excel
        nombre_archivo =  'PROCESADO_FLUORIMETRO.xlsx'
               
        output = BytesIO()
        writer = pandas.ExcelWriter(output, engine='xlsxwriter')
        datos_excel = datos_exporta.to_excel(writer, index=False, sheet_name='DATOS')
        writer.close()
        datos_excel = output.getvalue()

        st.download_button(
            label="DESCARGA EXCEL CON LOS DATOS PROCESADOS",
            data=datos_excel,
            file_name=nombre_archivo,
            help= 'Descarga un archivo .xlsx con los datos procesados',
            mime="application/vnd.ms-excel"
            )              
   


        
     
        
     
