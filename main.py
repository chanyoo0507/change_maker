import streamlit as st
import pandas as pd

st.title("강원생활도우미앱 3.0")

def load_data():
    uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요",type=["xlsx"])
    if uploaded_file is not None:
        table = pd.read_excel(uploaded_file)
        return table

df = load_data()
st.dataframe(df)
