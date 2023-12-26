import streamlit as st'
import pandas as pd
data = None
with open('pages/forbidden.txt','r',encoding='utf-8-sig') as fp:
    data = fp.readlines()
df = pd.DataFrame({'屏蔽词列表':data})
st.data_editor(df)
_,col2,col3 = st.columns([0.6,0.2,0.2])
with col2:
    plus_btn = st.button('+')
with col3:
    minus_btn = st.button('-')

