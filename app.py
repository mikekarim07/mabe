import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Amarre del IVA",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:miguel.karim@karimortega.com'
    }
)

st.image("https://mabeglobal.com/medias/?context=bWFzdGVyfGltYWdlc3wxNDE4fGltYWdlL3BuZ3xhR0ptTDJnMFpDODVNalU0TnpJNU5ETTVNall5fDA1NTc2N2UzYWEzOGJiZWI3ZjdjZWUyNWZhNzNhMjQ0YjdkOTBjOWFhNzRhNDZlYmJjMjg4Y2Q1ZGJhNDU2N2I", width=120)
st.header('Amarre del IVA')
st.subheader('Plataforma Web dedicada a la determinación del IVA Acreditable')


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




if uploaded_RepEgresos and uploaded_RepPagos and uploaded_RepFactoraje and uploaded_AuxIVA:
    RepEgresos = load_sheet(uploaded_RepEgresos, 'Sheet1', dtype_RepEgresos)
    RepPagos = load_sheet(uploaded_RepPagos, sheet_Rep_pagos, dtype_RepPagos)
    RepFactoraje = load_sheet(uploaded_RepFactoraje, sheet_Rep_fact, dtype_RepFact)
    AuxIVA =  load_sheet(uploaded_AuxIVA, sheet_AuxIVA, dtype_AuxIVA)

    # Reemplazar errores en el reporte de pagos en las columnas Tipo 1 y Doc Comepnsacion
    ColsNA_RepPagos = ['TIPO 1', 'Doc. Compensacion']
    RepPagos[ColsNA_RepPagos] = RepPagos[ColsNA_RepPagos].fillna('')
    
    # Reemplazar errores en el reporte de factoraje en la columna Institucion
    ColsNA_RepFact = ['INSTITUCION']
    RepFactoraje[ColsNA_RepFact] = RepFactoraje[ColsNA_RepFact].fillna('')

    #Comparativa de Reporte de Egresos vs Reporte de Pagos
    RepEgresos_compPag = RepEgresos.copy()
    RepEgresos_compPag['Importe MDE'] = RepEgresos_compPag['Total al TC de Pago']/RepEgresos_compPag['Tipo Cambio Comp']
    RepEgresos_compPag = RepEgresos_compPag[RepEgresos_compPag['Factoraje'] != 'X']
    RepEgresos_compPag = RepEgresos_compPag.groupby(['Clase Docto Comp', 'Docto de Compensación', 'NACIONALIDAD'], as_index=False).agg({
        'Importe MDE': 'sum',
        'Total al TC de Pago': 'sum'
    })
    RepPagos_comp = RepPagos.copy()
    RepPagos_comp = RepPagos_comp.groupby(["Doc. Compensacion", "Nombre", "CLASIFICACION 1", "Clasificacion 2", "NACIONALIDAD"], as_index=False).agg({
        ('Importe MDE': 'sum').round(2),
        ('Importe ML': 'sum').round(2),
    })
    Comparativo_RPvsRE = RepPagos_comp.merge(RepEgresos_compPag, left_on="Doc. Compensacion", right_on='Docto de Compensación', how='left', suffixes=('', '_RE'))
    Comparativo_RPvsRE = Comparativo_RPvsRE[['Doc. Compensacion','Nombre','CLASIFICACION 1','Clasificacion 2','NACIONALIDAD','Importe MDE','Importe ML','Clase Docto Comp','Importe MDE_RE']]
    Comparativo_RPvsRE['Diferencia'] = (Comparativo_RPvsRE['Importe MDE']-Comparativo_RPvsRE['Importe MDE_RE']).round(2)
    
    # Comparativa de Reporte de Facturacion vs Reporte de Egresos
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
        'Importe MDE': 'sum',
        'Total al TC de Pago': 'sum'})
    Comparativo_RFvsREg = RepFactoraje_compRE.merge(RepEgresos_compFact, left_on="DCTO COMPENSACION", right_on='Docto de Compensación', how='left', suffixes=('', '_RE'))
    Comparativo_RFvsREg['Dif MDE'] = Comparativo_RFvsREg['Importe MDE'] + Comparativo_RFvsREg['Importe MDE_RE']
    Comparativo_RFvsREg['Dif ML'] = Comparativo_RFvsREg['Importe ML'] + Comparativo_RFvsREg['Total al TC de Pago']

    # Auxiliar del IVA
    AuxIVA['Asignación Factoraje Publicado/ND (Cliente Proveedor)'] = AuxIVA['Asignación'].str[:10]
    AuxIVA['Documento Llave'] = AuxIVA['Referencia'].str[:-3]
    AuxIVA['Mes'] = AuxIVA['Fe.contabilización'].dt.month_name()
    AuxIVA_PGE = AuxIVA.groupby(['Mes'], as_index=False).agg({
        'Cuenta': 'count',
        })
    min_cuenta_index = AuxIVA_PGE['Cuenta'].idxmin()

    # Obtener el valor del mes correspondiente
    mes_menor_cuenta = AuxIVA_PGE.loc[min_cuenta_index, 'Mes']
    
    # Mostrar el resultado
    st.write(mes_menor_cuenta)

    def PE_GE(row):
    # Verificar las condiciones
        if mes_menor_cuenta == row['Mes']:
            return "PE_GE"
        else:
            return ''

    AuxIVA['Periodo_GE'] = AuxIVA.apply(PE_GE, axis=1)


    
    st.dataframe(AuxIVA_PGE)
    
    RepEgresosF38 = RepEgresos.copy()
    RepEgresosF38['Año Documento'] = RepEgresosF38['Fecha de Documento'].dt.year.astype(str)
    RepEgresosF38['Año Documento'] = RepEgresosF38['Año Documento'].str[-2:]
    RepEgresosF38['Documento Origen Llave'] = RepEgresosF38['Documento Origen'].astype(str) + RepEgresosF38['Año Documento']

    #Opcion 1 - Merge
    RepEgresosF38 = RepEgresosF38[['Documento Origen Llave','IVA al TC de Pago']]
    AuxIVA = AuxIVA.merge(RepEgresosF38, left_on="Documento Llave", right_on='Documento Origen Llave', how='left', suffixes=('', '_RE'))

    #Opcion 2 - Funcion
    # AuxIVA['MDE'] = AuxIVA['Documento Llave'].map(lambda x: RepEgresosF38[RepEgresosF38['Documento Origen Llave'] == x]['IVA al TC de Pago'].values[0] if x in RepEgresosF38['Documento Origen Llave'].values else 0)
    st.dataframe(AuxIVA)
    st.dataframe(RepEgresosF38)





    tab1, tab2, tab3 = st.tabs(["R_Pagos vs R_Egresos", "R_Factoraje vs R_Egresos", "Otro"])

    with tab1:
        st.subheader('Comparativo Reporte de Pagos vs Reporte de Egresos')
        st.dataframe(Comparativo_RPvsRE)

    with tab2:
        st.subheader('Comparativo Reporte de Factoraje vs Reporte de Egresos')
        st.dataframe(Comparativo_RFvsREg)

    with tab3:
        st.subheader('Comparativo Reporte de Factoraje vs Reporte de Egresos')
        st.dataframe(Comparativo_RFvsREg)




