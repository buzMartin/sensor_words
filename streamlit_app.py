import streamlit as st
import pandas as pd
import requests
import json
import time
import st_aggrid
from st_aggrid.shared import ExcelExportMode
import hmac

def check_lt_sensor(content):
    url = st.secrets['url_ep']
    payload = {
    "game": st.secrets['game'],
    "timestamp":"1692154705000",
    "os":3,
    "content": content,
    "sign":  st.secrets['sign']
}
    headers = {
    'content-type': 'application/json;charset=UTF-8'
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    res_json= response.json()
    if res_json['status']==0:
        return res_json['data']['words']

def check_customs(content):
    words_list = st.session_state['sensors']
    result_list = []
    if len(words_list)>0:
        for word in words_list:
            if word in content:
                result_list.append(word)
    
    if len(result_list)>0:
        return result_list
             
def make_df(v_list:list, cols_num:int):
    st.session_state['data_storage'] = {}
    raw_data = st.session_state['data_storage']
    for i in range(1, cols_num+1):
        raw_data[i] = []
    for i,v in enumerate(v_list):
        raw_data[i % cols_num+1].append(v)
    max_len = max([len(l) for l in raw_data.values()])
    for k,v in raw_data.items():
        if len(v)<max_len:
            raw_data[k]=raw_data[k]+['']*(max_len-len(v))
    df = pd.DataFrame(raw_data).dropna()
    return df
    
def handle_upload_files(file_list):
    st.session_state['data_storage'] = {}
    data_storage = st.session_state['data_storage']
    for file in file_list:
        if file.name.endswith('srt'):
            lines=[l for l in file.getvalue().decode('utf-8-sig').splitlines() if l!='']
            data_storage[file.name]=lines

def apply_check(num,to_checks):
    try:
        num = int(num)
        to_checks = [int(c) for c in to_checks.split(',')]
    except:
        st.warning('请检查输入的格式')
    sensor_dict= {
        '文件':[],
        '段':[],
        '内容':[],
        '敏感词':[]
    }
    total_progress = 0
    total_progress_add = round(100/(len(st.session_state['data_storage'])*len(to_checks))/100,2)
    total_progress_bar = st.progress(total_progress,'总进度')
    cur_progress = 0
    cur_progress_bar = st.progress(cur_progress,'当前进度')
    
    for k, v in st.session_state['data_storage'].items():
        total_progress_bar.progress(total_progress:=min(total_progress+total_progress_add,1),f'总进度：正在检查{k}')
        df = make_df(v,num)
        for col in to_checks:
            cur_progress_add = round(100/df.shape[0]/100,2)
            for rn, row in df.loc[:,col].items():
                sensor = check_lt_sensor(row)
                time.sleep(1)
                if sensor:
                    sensor_dict['文件'].append(k)
                    sensor_dict['段'].append(rn+1)
                    sensor_dict['内容'].append(row)
                    sensor_dict['敏感词'].append(f'{sensor}')
                custom_sensor = check_customs(row)
                if custom_sensor:
                    sensor_dict['文件'].append(k)
                    sensor_dict['段'].append(rn+1)
                    sensor_dict['内容'].append(row)
                    sensor_dict['敏感词'].append(f'自定义敏感词: {sensor}')
                    # sensor_list.append(f'文件{k}，第{rn+1}段检测到自定义敏感词：{sensor}')
                cur_progress_bar.progress(cur_progress:=min(cur_progress+cur_progress_add,1),f'当前：第{rn+1}段第{col}行')
            cur_progress = 0
            cur_progress_bar.empty()     
    total_progress_bar.progress(1,'检查完成')
    time.sleep(1)
    total_progress_bar.empty()
    st.text('检查完成! 右键点击下面表格可导出为xlsx')
    st.session_state['result_df']=pd.DataFrame(sensor_dict)
    st_aggrid.AgGrid(st.session_state['result_df'],excel_export_mode=ExcelExportMode.MANUAL)

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

with open('pages/forbidden.txt','r',encoding='utf-8-sig') as fp:
    st.session_state['sensors'] =  fp.readlines()

st.title('字幕敏感词检测工具')

upload_files = st.file_uploader('请上传待检测的文件，可上传文件夹或单个文件',type=['srt','txt'],accept_multiple_files=True)

if upload_files:
    handle_upload_files(upload_files)
    chunk_num = st.text_input('多少行作为一段，请输入数字',4)
    check_cols = st.text_input('需要检测一段中的哪些行，数字用逗号隔开，如3,4','3,4')
    apply_btn = st.button('开始检查',on_click=apply_check,args=[chunk_num,check_cols])
    example = """## 填写示例
    例如格式如下，可以看出每4行作为一个段落，中文和英文的行分别是段内的第3，第4行。
    所以上面的参数可以填4和3,4
    1
    00:00:05,800 --> 00:00:07,250
    舒颜
    Shu Yan

    2
    00:00:07,251 --> 00:00:08,050
    赵有为接到一个
    After Zhao Youwei received a
    """
    st.markdown(example)
    