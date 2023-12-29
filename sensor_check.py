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

def check_customs(content, custom_list):
    words_list = custom_list
    result_list = []
    if len(words_list)>0:
        for word in words_list:
            if word in content:
                result_list.append(word)
    
    if len(result_list)>0:
        return result_list

def check(row, cn_cols, oversea_cols, sensor_custom_list):
    with ThreadPoolExecutor(max_workers=3) as worker:
        cn_contents = [row.iat[cn-1] for cn in cn_cols]
        ovs_contents = [row.iat[ovs-1] for ovs in oversea_cols]
        custom_contents = cn_contents+ovs_contents
        sensors = [sensor_custom_list] * len(custom_contents)
        cn_results = worker.map(check_sensor_cn,cn_contents)
        ovs_results = worker.map(check_sensor_oversea,ovs_contents)
        custom_results = worker.map(check_customs,custom_contents,sensors)
    return list(cn_results)+list(ovs_results)+list(custom_results)