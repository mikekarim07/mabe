import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO
import io
from io import StringIO
import base64
import xlsxwriter
from xlsxwriter import Workbook
import time






st.set_page_config(
    page_title="Amarre del IVA",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:miguel.karim@karimortega.com'
    }
)

st.image("https://mabeglobal.com/medias/?context=bWFzdGVyfGltYWdlc3wxNDE4fGltYWdlL3BuZ3xhR0ptTDJnMFpDODVNalU0TnpJNU5ETTVNall5fDA1NTc2N2UzYWEzOGJiZWI3ZjdjZWUyNWZhNzNhMjQ0YjdkOTBjOWFhNzRhNDZlYmJjMjg4Y2Q1ZGJhNDU2N2I", width=200)
st.header('Amarre del IVA')
st.subheader('Plataforma Web para la determinación del IVA Acreditable')
st.caption("Update 25/Jul//2024")

# Definir funciones para cargar archivos
@st.cache_data
def get_sheet_names(file):
    # Leer todas las hojas del archivo y devolver sus nombres
    excel_file = pd.ExcelFile(file, engine='openpyxl')
    return excel_file.sheet_names

@st.cache_data
def load_sheet(file, sheet_name, dtype):
    # Leer una hoja específica del archivo de Excel
    return pd.read_excel(file, engine='openpyxl', sheet_name=sheet_name, dtype=dtype)

dtype_RepPagos = {
    'Nombre': str,
    'PAIS': str,
    'NACIONALIDAD': str,
    'Tipo': str,
    'Referencia': str,
    'Doc. Compensacion': str,
}

dtype_RepEgresos = {
    'Clase Docto Comp': str,
    'Docto de Compensación': str,
    'UUID Complemento': str,
    'Moneda Comp': str,
    'RFC de Proveedor': str,
}

dtype_RepFact = {
    'INSTITUCION': str,
    'SEGMENTO': str,
    'Texto': str,
    # 'Clasificacion': str,
    # 'RFC de Proveedor': str,
}

dtype_AuxIVA = {
    'Cuenta': str,
    'Ejercicio': str,
    'Período Contable': str,
    'Nº documento': str,
    'Clase de documento': str,
    'Asignación': str,
    'Referencia': str,
    # '': str,
    # '': str,
    # '': str,
    # '': str,
    # '': str,
}

dtype_FactPub = {
    'Nº doc.': str,
    'II': str,
    # 'Período Contable': str,
    # 'Nº documento': str,
    # 'Clase de documento': str,
    # 'Asignación': str,
    # 'Referencia': str,
    # '': str,
    # '': str,
    # '': str,
    # '': str,
    # '': str,
}

dtype_fbl1n = {
    'TEXT CAB cartera': str,
    'Documento': str,
}


uploaded_RepEgresos = st.sidebar.file_uploader("Carga el Reporte de Egresos", type=["xlsx"])
st.sidebar.divider()

uploaded_RepPagos = st.sidebar.file_uploader("Carga el Reporte de Pagos", type=["xlsx"])
if uploaded_RepPagos is not None:
    # Obtener nombres de las hojas del archivo
    sheet_names_pagos = get_sheet_names(uploaded_RepPagos)
    
    # Seleccionar la hoja de Excel
    sheet_Rep_pagos = st.sidebar.selectbox("Seleccionar hoja del reporte de pagos que contiene los datos para procesar", sheet_names_pagos)
st.sidebar.divider()

uploaded_RepFactoraje = st.sidebar.file_uploader("Carga el Reporte de Factoraje", type=["xlsx"])
if uploaded_RepFactoraje is not None:
    # Obtener nombres de las hojas del archivo
    sheet_names_fact = get_sheet_names(uploaded_RepFactoraje)
    
    # Seleccionar la hoja de Excel
    sheet_Rep_fact = st.sidebar.selectbox("Seleccionar hoja del reporte de pagos que contiene los datos para procesar", sheet_names_fact)

st.sidebar.divider()

uploaded_AuxIVA = st.sidebar.file_uploader("Carga el Auxiliar del IVA de la cuenta 1330011002", type=["xlsx"])
if uploaded_AuxIVA is not None:
    # Obtener nombres de las hojas del archivo
    sheet_names_AuxIVA = get_sheet_names(uploaded_AuxIVA)
    
    # Seleccionar la hoja de Excel
    sheet_AuxIVA = st.sidebar.selectbox("Seleccionar hoja del reporte de pagos que contiene los datos para procesar", sheet_names_AuxIVA)

st.sidebar.divider()

uploaded_FactPub = st.sidebar.file_uploader("Carga el Reporte de Factoraje Publicado", type=["xlsx"])
if uploaded_FactPub is not None:
    # Obtener nombres de las hojas del archivo
    sheet_names_factpub = get_sheet_names(uploaded_FactPub)
    
    # Seleccionar la hoja de Excel
    sheet_Rep_factpub = st.sidebar.selectbox("Seleccionar hoja que contiene el factoraje publicado", sheet_names_factpub)
    sheet_Rep_factpub_TC = st.sidebar.selectbox('''Seleccionar hoja que contiene la FBL1N con el "TEXT CAB" ''', sheet_names_factpub)
st.sidebar.divider()


# if uploaded_RepEgresos and uploaded_RepPagos and uploaded_RepFactoraje and uploaded_AuxIVA:
if uploaded_RepEgresos and uploaded_RepPagos and uploaded_RepFactoraje and uploaded_AuxIVA and uploaded_FactPub:
    RepEgresos = load_sheet(uploaded_RepEgresos, 'Sheet1', dtype_RepEgresos)
    RepPagos = load_sheet(uploaded_RepPagos, sheet_Rep_pagos, dtype_RepPagos)
    RepFactoraje = load_sheet(uploaded_RepFactoraje, sheet_Rep_fact, dtype_RepFact)
    AuxIVA =  load_sheet(uploaded_AuxIVA, sheet_AuxIVA, dtype_AuxIVA)
    Fact_publicado = load_sheet(uploaded_FactPub, sheet_Rep_factpub, dtype_FactPub)
    Fact_pub_textcab = load_sheet(uploaded_FactPub, sheet_Rep_factpub_TC, dtype_fbl1n)

    # Limpiar reporte de egresos general
    RepEgresos['Tipo Cambio Comp'] = RepEgresos['Tipo Cambio Comp'].fillna(value=1)
    RepEgresos['Factoraje'] = RepEgresos['Factoraje'].fillna('')
    RepEgresos['Importe MDE'] = RepEgresos['Total al TC de Pago']/RepEgresos['Tipo Cambio Comp']
    
    # Reemplazar errores en el reporte de pagos en las columnas Tipo 1 y Doc Comepnsacion
    ColsNA_RepPagos = ['TIPO 1', 'Doc. Compensacion']
    RepPagos[ColsNA_RepPagos] = RepPagos[ColsNA_RepPagos].fillna('')
    
    # Reemplazar errores en el reporte de factoraje en la columna Institucion
    ColsNA_RepFact = ['INSTITUCION']
    RepFactoraje[ColsNA_RepFact] = RepFactoraje[ColsNA_RepFact].fillna('')

    #----- Comparativa de Reporte de Egresos vs Reporte de Pagos -----#
    RepEgresos_compPag = RepEgresos.copy()
    RepEgresos_compPag = RepEgresos_compPag[RepEgresos_compPag['Factoraje'] != 'X']
    RepEgresos_compPag = RepEgresos_compPag.groupby(['Clase Docto Comp', 'Docto de Compensación', 'NACIONALIDAD'], as_index=False).agg({
        'Importe MDE': 'sum',
        'Total al TC de Pago': 'sum'
    })
    
        
    RepPagos_comp = RepPagos.copy()
    RepPagos_comp = RepPagos_comp.groupby(["Doc. Compensacion", "Nombre", "CLASIFICACION 1", "Clasificacion 2", "NACIONALIDAD"], as_index=False).agg({
        'Importe MDE': 'sum',
        'Importe ML': 'sum',
    }).round(2)
    Comparativo_RPvsRE = RepPagos_comp.merge(RepEgresos_compPag, left_on="Doc. Compensacion", right_on='Docto de Compensación', how='left', suffixes=('', '_RE'))
    Comparativo_RPvsRE = Comparativo_RPvsRE[['Doc. Compensacion','Nombre','CLASIFICACION 1','Clasificacion 2','NACIONALIDAD','Importe MDE','Importe ML','Clase Docto Comp','Importe MDE_RE']]
    Comparativo_RPvsRE['Importe MDE_RE'] = Comparativo_RPvsRE['Importe MDE_RE'].fillna(value=0)
    Comparativo_RPvsRE['Diferencia'] = (Comparativo_RPvsRE['Importe MDE']+Comparativo_RPvsRE['Importe MDE_RE']).round(2)

    def Comentarios_RE(row):
    # Verificar las condiciones
        if  ((row['Diferencia']>2) or (row['Diferencia']<-2)) and ((row['CLASIFICACION 1'] == "(Transferencias)") or (row['CLASIFICACION 1'] == "(Cheque)")) and (row['Doc. Compensacion'] != "") :
            return "Documento Faltante"
        elif (row['CLASIFICACION 1'] == "(Factoraje)"):
            return "Factoraje"
        elif ((row['Diferencia']>2) or (row['Diferencia']<-2)) and (row['CLASIFICACION 1'] == "(Compensacion)"):
            return "No es Flujo"
        else:
            return 'Ok'

    Comparativo_RPvsRE['Comentarios'] = Comparativo_RPvsRE.apply(Comentarios_RE, axis=1)


    
        
    #----- Comparativa de Reporte de Facturacion vs Reporte de Egresos -----#
    RepFactoraje_compRE = RepFactoraje.copy()
    RepFactoraje_compRE['FECHA PAGO'] = RepFactoraje_compRE['FECHA PAGO'].astype(str)
    RepFactoraje_compRE['DCTO COMPENSACION'] = RepFactoraje_compRE['DCTO COMPENSACION'].astype(str)

    RepFactoraje_compRE = RepFactoraje_compRE.groupby(["SEMANA", "FECHA PAGO", "DCTO COMPENSACION"], as_index=False).agg({
        'Importe MDE': 'sum',
        'Importe ML': 'sum'
    })
    RepEgresos_compFact = RepEgresos.copy()
    RepEgresos_compFact['Importe MDE'] = RepEgresos_compFact['Total al TC de Pago']/RepEgresos_compFact['Tipo Cambio Comp']
    RepEgresos_compFact = RepEgresos_compFact[RepEgresos_compFact['Factoraje'] == 'X']
    RepEgresos_compFact = RepEgresos_compFact.groupby(['Clase Docto Comp', 'Docto de Compensación'], as_index=False).agg({
        'Importe MDE': 'sum'})
    RepEgresos_compFact['Importe MDE'] = RepEgresos_compFact['Importe MDE'].round(2)
    Comparativo_RFvsREg = RepFactoraje_compRE.merge(RepEgresos_compFact, left_on="DCTO COMPENSACION", right_on='Docto de Compensación', how='left', suffixes=('', '_RE'))
    Comparativo_RFvsREg['Diferencia'] = Comparativo_RFvsREg['Importe MDE'] + Comparativo_RFvsREg['Importe MDE_RE']
    Comparativo_RFvsREg['Diferencia'] = pd.to_numeric(Comparativo_RFvsREg['Diferencia'], errors='coerce')
    Comparativo_RFvsREg['Diferencia'] = Comparativo_RFvsREg['Diferencia'].round(2)

    #----- Factoraje Publicado -----#
    Fact_publicado.columns = Fact_publicado.columns.str.strip()
        
    def fact_pag_baseiva(row):
        if  (row['II'] == 'V2'):
            return row['Importe en ML']/1.16
        elif (row['II'] == 'V0') or (row['II'] == 'V5'):
            return row['Importe en ML']
        elif (row['II'] == 'V8'):
            return row['Importe en ML']/1.08
        else:
            return 0
    Fact_publicado['Base'] = Fact_publicado.apply(fact_pag_baseiva, axis=1).round(2)
    
    def fact_pag_iva(row):
        if  (row['II'] == 'V2'):
            return (row['Importe en ML']/1.16)*.16
        elif (row['II'] == 'V0') or (row['II'] == 'V5'):
            return 0
        elif (row['II'] == 'V8'):
            return (row['Importe en ML']/1.08)*.08
        else:
            return 0
    Fact_publicado['IVA ML'] = Fact_publicado.apply(fact_pag_iva, axis=1).round(2)
    
    def fact_pag_iva_mo(row):
        if  (row['II'] == 'V2'):
            return (row['Importe en MD']/1.16)*.16
        elif (row['II'] == 'V0') or (row['II'] == 'V5'):
            return 0
        elif (row['II'] == 'V8'):
            return (row['Importe en MD']/1.08)*.08
        else:
            return 0
    Fact_publicado['IVA MO'] = Fact_publicado.apply(fact_pag_iva_mo, axis=1).round(2)
    Fact_publicado = Fact_publicado[['Nº doc.', 'Mon.', 'Base', 'IVA ML', 'IVA MO']]
    st.write("factoraje publicado")
    st.dataframe(Fact_publicado)
    
    Fact_publicado = Fact_publicado.merge(Fact_pub_textcab, left_on="Nº doc.", right_on='Documento', how='left')
    RE_AB = RepEgresos.copy()
    # st.write('Reporte de egresos puro')
    # st.dataframe(RE_AB)
    RE_AB = RE_AB[RE_AB['Clase Docto Comp']== 'AB']
    RE_AB = RE_AB[['Clase Docto Comp', 'Docto de Compensación', 'Base al TC de Pago', 'Documento Origen']]
    st.write('Reporte de egresos solo abs')
    st.dataframe(RE_AB)
    Fact_publicado = Fact_publicado.merge(RE_AB, left_on='TEXT CAB cartera', right_on='Documento Origen', how='left')


    
    st.write("factoraje publicado con text cab")
    st.dataframe(Fact_publicado)







    AuxIVAvsFact = AuxIVA.copy()
    AuxIVAvsFact.columns = AuxIVAvsFact.columns.str.strip()
    AuxIVAvsFact.columns = AuxIVAvsFact.columns.str.strip()
    AuxIVAvsFact['Asig Fact Pub'] = AuxIVAvsFact['Asignación'].str[:10]
    AuxIVAvsFact = AuxIVAvsFact.groupby(['Cuenta', 'Asig Fact Pub'], as_index=False).agg({
        'Importe en moneda local': 'sum',
        'Importe en moneda doc.': 'sum',
        })
    # st.write("auxiliar iva para cruce con fact pub")
    # st.dataframe(AuxIVAvsFact)
    
    Fact_publicado_vsAuxIVA = Fact_publicado.merge(AuxIVAvsFact, left_on="Nº doc.", right_on='Asig Fact Pub', how='left')
    Fact_publicado_vsAuxIVA['Dif vs Aux ML'] = Fact_publicado_vsAuxIVA['IVA ML'] + Fact_publicado_vsAuxIVA['Importe en moneda local']
    Fact_publicado_vsAuxIVA['Dif vs Aux MO'] = Fact_publicado_vsAuxIVA['IVA MO'] + Fact_publicado_vsAuxIVA['Importe en moneda doc.']
    st.write("fact pub con iva f38")
    st.dataframe(Fact_publicado_vsAuxIVA)


    #----- Auxiliar del IVA
    AuxIVA.columns = AuxIVA.columns.str.strip()
    AuxIVA['Asig Fact Pub'] = AuxIVA['Asignación'].str[:10]
    AuxIVA['Doc Llave'] = AuxIVA['Referencia'].str[:-3]
    AuxIVA['Doc Llave'] = AuxIVA['Doc Llave'].astype(str)
    AuxIVA['Consecutivo'] = AuxIVA.groupby('Doc Llave').cumcount()
    auxiva_info = AuxIVA.shape
    auxiva_pivot = AuxIVA.groupby(['Clase de documento'], as_index=False).agg({
        'Importe en moneda local': 'sum',
        })
    
    st.write(auxiva_info)
    st.write(auxiva_pivot)
    def documento_llave(row):
    # Verificar las condiciones
        if  (row['Consecutivo'] == 0):
            return row['Doc Llave']
        elif (row['Consecutivo'] != 0):
            return row['Doc Llave'] + "X"
    AuxIVA['Documento Llave'] = AuxIVA.apply(documento_llave, axis=1)
    
    AuxIVA['Mes'] = AuxIVA['Fe.contabilización'].dt.month_name()
    AuxIVA_PGE = AuxIVA.groupby(['Mes'], as_index=False).agg({
        'Cuenta': 'count',
        })
    min_cuenta_index = AuxIVA_PGE['Cuenta'].idxmin()

    # Obtener el valor del mes correspondiente
    mes_menor_cuenta = AuxIVA_PGE.loc[min_cuenta_index, 'Mes']
    
    # Mostrar el resultado
    st.write(f' Periodo GE: {mes_menor_cuenta}')

    def PE_GE(row):
    # Verificar las condiciones
        if mes_menor_cuenta == row['Mes']:
            return "PE_GE"
        else:
            return None

    AuxIVA['Periodo_GE'] = AuxIVA.apply(PE_GE, axis=1)

    st.dataframe(AuxIVA_PGE)
    st.dataframe(AuxIVA)
    
    RepEgresosF38 = RepEgresos.copy()
    RepEgresosF38['Año Documento'] = RepEgresosF38['Fecha de Documento'].dt.year.astype(str)
    RepEgresosF38['Año Documento'] = RepEgresosF38['Año Documento'].str[-2:]
    RepEgresosF38['Documento Origen Llave'] = RepEgresosF38['Documento Origen'].astype(str) + RepEgresosF38['Año Documento']
    RepEgresosF38 = RepEgresosF38[['Factoraje', 'Clase Docto Comp', 'Docto de Compensación', 'Total al TC de Pago', 'Base al TC de Pago', 'IVA al TC de Pago', 'Indicador de IVA', 'Ret. IVA', 'Documento Origen Llave']]
    RepEgresosF38 = RepEgresosF38.groupby(['Factoraje', 'Clase Docto Comp', 'Docto de Compensación', 'Documento Origen Llave'], as_index=False).agg({
        'Total al TC de Pago': 'sum',
        'Base al TC de Pago': 'sum',
        'IVA al TC de Pago': 'sum',
        'Ret. IVA': 'sum'
        })
    st.header('reporte de egresos')
    st.dataframe(RepEgresosF38)
    AuxIVA = AuxIVA.merge(RepEgresosF38, left_on="Documento Llave", right_on='Documento Origen Llave', how='left')
    

    AuxIVA['CDC'] = AuxIVA.groupby('Doc Llave')['Clase Docto Comp'].transform('first')
    AuxIVA = AuxIVA.merge(Fact_publicado, left_on="Asig Fact Pub", right_on='Nº doc.', how='left')
    st.subheader("aux iva con merge fact")
    st.dataframe(AuxIVA)
    st.divider()

    AuxIVA = AuxIVA[AuxIVA['Clase de documento'] == 'TI']
    
    def clasificacion(row):
    # Verificar las condiciones
        if row['Documento Llave'].startswith("16") and row['Periodo_GE']==None:
            return "Mercado Pago"
        elif row['Periodo_GE']=='PE_GE':
            return 'PE_GE'
        elif row['CDC']=='KZ':
            return 'Reporte Egresos'
        elif row['CDC']=='AB':
            return 'AB'
        elif pd.notna(row['Nº doc.']):
            return 'Factoraje Publicado'
        else:
            return ''

    AuxIVA['clasificacion'] = AuxIVA.apply(clasificacion, axis=1)

    AuxIVA_summary = AuxIVA[AuxIVA['Clase de documento'] == 'TI']
    AuxIVA_summary = AuxIVA_summary.groupby(['clasificacion'], as_index=False).agg({
        'Importe en moneda local': 'sum',
        'Cuenta': 'count'
        })


    st.dataframe(AuxIVA)
    st.dataframe(AuxIVA_summary)


    auxiva_pivot = AuxIVA.groupby(['Clase de documento'], as_index=False).agg({
        'Importe en moneda local': 'sum',
        })
    
    #st.write(auxiva_info)
    #st.write(auxiva_pivot)


    tab1, tab2, tab3 = st.tabs(["R_Pagos vs R_Egresos", "R_Factoraje vs R_Egresos", "Conciliacion"])

    with tab1:
        st.subheader('Comparativo de Reporte de Pagos vs Reporte de Egresos')
        st.write('''Detalle del total de documentos en el **:red-background[Reporte de Pagos]** que no se encontraron en el **:blue-background[Reporte de Egresos]**''')
        st.dataframe(Comparativo_RPvsRE)

        Nacionales = Comparativo_RPvsRE[(Comparativo_RPvsRE['NACIONALIDAD'] == 'NACIONAL') & (Comparativo_RPvsRE['Comentarios'] == 'Documento Faltante')].shape[0]
        Extranjeros = Comparativo_RPvsRE[(Comparativo_RPvsRE['NACIONALIDAD'] == 'EXTRANJERO') & (Comparativo_RPvsRE['Comentarios'] == 'Documento Faltante')].shape[0]
        st.write(f'Total de documento **NACIONALES** no encontrados: {Nacionales}')
        st.write(f'Total de documento **EXTRANJEROS** no encontrados: {Extranjeros}')
        st.write('''Dar click en el boton :point_down:"Resumen Comparativo" para descargar el archivo de excel que contiene el total de documentos del reporte de pagos no encontrados en el reporte de Egresos.''')

        
        

    with tab2:
        st.subheader('Comparativo Reporte de Factoraje vs Reporte de Egresos')
        st.dataframe(Comparativo_RFvsREg)

    with tab3:
        st.subheader('Conciliacion')
        st.dataframe(RepEgresos)


    doc_faltantes = Comparativo_RPvsRE[Comparativo_RPvsRE['Comentarios'] == "Documento Faltante"]
    
    
    
    current_datetime = datetime.now().strftime('%y%m%d_%H%M')
    file_name_resumen = f'Resumen_{current_datetime}.xlsx'

    xls_buffer_docsfaltantes = BytesIO()
    with pd.ExcelWriter(xls_buffer_docsfaltantes, engine='xlsxwriter') as writer:
        Comparativo_RPvsRE.to_excel(writer, index=False, sheet_name='Comp_RPvsRE')
        Comparativo_RFvsREg.to_excel(writer, index=False, sheet_name='Comp_RFactvsRE')
        doc_faltantes.to_excel(writer, index=False, sheet_name='Doc_Faltantes')
        AuxIVA_summary.to_excel(writer, index=False, sheet_name='AuxIVA_summary')
        AuxIVA.to_excel(writer, index=False, sheet_name='AuxIVA')




    # Descargar el archivo Excel en Streamlit
    st.download_button(
        label="Resumen Comparativo",
        data=xls_buffer_docsfaltantes.getvalue(),
        file_name=file_name_resumen,
        key='Download_Resumen'
    )
    
    
    
