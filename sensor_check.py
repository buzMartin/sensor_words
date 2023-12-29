import requests
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
import json
def check_sensor_cn(content):
    url = st.secrets['url_cn']
    payload = {
    "game": st.secrets['game_cn'],
    "timestamp":"1692154705000",
    "os":3,
    "content": content,
    "sign":  st.secrets['sign_cn']
}
    headers = {
    'content-type': 'application/json;charset=UTF-8'
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    res_json= response.json()
    if res_json['status']==0:
        return res_json['data']['words']

def check_sensor_oversea(content):
    url = st.secrets['url_oversea']
    payload = {
    "game": st.secrets['game_oversea'],
    "sid":"abc",
    "os":3,
    "content": content,
    "ip":"192.168.1.11",
    "isYd": 2,
    "isReturnWord": 1,
    "sign":  st.secrets['sign_oversea']
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

def check(row, cn_cols, oversea_cols):
    with ThreadPoolExecutor(max_workers=3) as worker:
        cn_contents = [row[cn] for cn in cn_cols]
        ovs_contents = [row[ovs] for ovs in oversea_cols]
        custom_contents = cn_contents+ovs_contents

        cn_results = worker.map(check_sensor_cn,cn_contents)
        ovs_results = worker.map(check_sensor_oversea,ovs_contents)
        custom_results = worker.map(check_customs,custom_contents)
    return cn_results+ovs_results+custom_results

    for rn, row in df.loc[:,col].items():
        sensor = check_sensor_cn(row)
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