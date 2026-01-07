import streamlit as st
from api.metrics import get_log


logs = get_log('app.log')

total_number_requests = len(logs)
total_response_time_sum = 0.0
status_code_response = {}
accessed_endpoints = {}
for log in logs:
    total_response_time_sum += log['Execution time']

    if log['status_code'] not in status_code_response:
        status_code_response[log['status_code']] = 0      
    status_code_response[log['status_code']] +=1

    if log['path'] not in accessed_endpoints:
        accessed_endpoints[log['path']] = 0      
    accessed_endpoints[log['path']] +=1

avg_response_time = total_response_time_sum / total_number_requests
   
    

st.title("API Dashboard")
st.write("Dashboard para monitoramento de parâmetros da API REST criada para o Tech Challenge fase 1 da postech e Machine Learning")
st.metric("Requisições", total_number_requests)
st.metric("Tempo médio de resposta", f"{avg_response_time} sec")

st.bar_chart( data = status_code_response, x_label='status_code', y_label='count')
st.bar_chart( data = accessed_endpoints, x_label='endpoint', y_label='count', sort = True)