import streamlit as st
import pandas as pd
import sensor_check
import time
import st_aggrid
from st_aggrid.shared import ExcelExportMode
import hmac
with open('pages/forbidden.txt','r',encoding='utf-8-sig') as fp:
    st.session_state['sensors'] =  fp.readlines()
    
def make_df(v_list:list, cols_num:int):
    """
    这里的df结构是，按每段x行，规划有多少个字段。然后装入df,填充长度
    这样的结果是字幕中每一段被作为一行保存
    比如:
    {
    0:['a','b'],
    1:[2,3],
    2:[5,'']
    }
    """
    st.session_state['data_storage'] = {}
    raw_data = st.session_state['data_storage']

    # 确认字段数量
    for i in range(cols_num):
        raw_data[i] = []

    # 在每个列里面填充内容
    for i,v in enumerate(v_list):
        raw_data[i % cols_num].append(v)
    
    # 补齐短的列
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

def apply_check(num,cn_to_checks, oversea_to_checks):
    try:
        num = int(num)
        cn_to_checks = [int(c) for c in cn_to_checks.split(',')]
        oversea_to_checks = [int(c) for c in oversea_to_checks.split(',')]
    except:
        st.warning('请检查输入参数的格式')
        return
    
    sensor_dict= {
        '文件':[],
        '段':[],
        '内容':[],
        '敏感词':[]
    }

    dfs = []
    for k, v in st.session_state['data_storage'].items():
        df = make_df(v,num)
        if max(cn_to_checks+oversea_to_checks) > df.shape[1]:
            st.warning('检查的行参数有误，请核对参数')
            return
        dfs.append(df)

    total_progress = 0
    total_progress_add = round(100/len(dfs)/100, 2)
    total_progress_bar = st.progress(total_progress,'总进度')

    cur_progress = 0
    cur_progress_bar = st.progress(cur_progress,'当前进度')
    for i, df in enumerate(dfs):
        file_name = list(st.session_state['data_storage'].keys())[i]
        total_progress_bar.progress(total_progress:=min(total_progress+total_progress_add,1),f'总进度：正在检查{file_name}')
        cur_progress_add = round(100/df.shape[0]/100,2)
        for n, row in df.iterrows():
            sensor_list = sensor_check.check(row, cn_to_checks, oversea_to_checks)
            time.sleep(0.5)
            if len(sensor_list)>0:
                sensor_dict['文件'].append(file_name)
                sensor_dict['段'].append(n+1)
                sensor_dict['内容'].append(row)
                sensor_dict['敏感词'].append(f'{sensor_list}')
            cur_progress_bar.progress(cur_progress:=min(cur_progress+cur_progress_add,1),f'当前：第{n+1}段')
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

st.title('字幕敏感词检测工具')

upload_files = st.file_uploader('请上传待检测的文件，可上传文件夹或单个文件',type=['srt','txt'],accept_multiple_files=True)

if upload_files:
    handle_upload_files(upload_files)
    chunk_num = st.text_input('多少行作为一段，请输入数字',4)
    check_cn_cols = st.text_input('中文敏感词检测的行，用数字填写，多行用逗号隔开，如3,4','3')
    check_oversea_cols = st.text_input('海外敏感词检测的行，用数字填写，多行用逗号隔开，如3,4','4')
    apply_btn = st.button('开始检查',on_click=apply_check,args=[chunk_num,check_cn_cols,check_oversea_cols])
    example = """## 填写示例
    例如格式如下，可以看出每4行作为一个段落，中文和英文的行分别是段内的第3，第4行。
    所以上面的参数可以填4，第二个填3，第三个填4
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
    