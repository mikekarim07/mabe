import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import pickle
import os
import datetime
from io import BytesIO
import io
from io import StringIO
import base64
import xlsxwriter
from xlsxwriter import Workbook
import time
# import pygwalker as pyg
# import streamlit.components.v1 as components
# from pygwalker.api.streamlit import init_streamlit_comm, get_streamlit_html



st.set_page_config(
    page_title="Conciliación de Reportes para la determinación del IVA acreeditable",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:miguel.karim@karimortega.com'
    }
)

st.image("https://mabeglobal.com/medias/?context=bWFzdGVyfGltYWdlc3wxNDE4fGltYWdlL3BuZ3xhR0ptTDJnMFpDODVNalU0TnpJNU5ETTVNall5fDA1NTc2N2UzYWEzOGJiZWI3ZjdjZWUyNWZhNzNhMjQ0YjdkOTBjOWFhNzRhNDZlYmJjMjg4Y2Q1ZGJhNDU2N2I", width=120)
# st.header('Machine Learnig Model')
st.subheader('Plataforma Web dedicada a la conciliación de los distintos reportes para la determinación del los cálculos de impuestos')
st.write('Contenido en construcción')

