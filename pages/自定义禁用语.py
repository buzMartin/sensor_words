import streamlit as st
import pandas as pd
import hmac
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input(
        "请输入密码", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("密码错误")
    return False


if not check_password():
    st.stop()

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

