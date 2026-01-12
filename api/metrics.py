from fastapi import APIRouter, Depends, HTTPException
from itertools import islice
import json
import os

router = APIRouter()

def get_log(file):
    json_logs = []
    if not os.path.exists(file):
        print(f"Erro: o arquivo '{file}' não foi encontrado.")
        return json_logs
    
    with open(file, 'r', encoding ='utf-8') as log_file:
        for number_line, line in enumerate(log_file, 1):
            try:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                json_logs.append(data)
                print(f"Linha {number_line} processada: {data}")

            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON na linha {number_line}: {e}")
            except Exception as e:
                print(f"Occoreu um erro inesperado na linha {number_line}: {e}")
    
    return json_logs

# Rota de métricas da aplicação
@router.get("/metrics")
def send_metrics():
    logs = get_log('app.log')

    if not logs:
        raise HTTPException (status_code = 404, detail="Empty log")
    
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
    sorted_endpoints = sorted(accessed_endpoints.items(), key = lambda item:item[1], reverse=True)
    
    return {
        "Total number of executions": total_number_requests,
        "Avarage execution time": avg_response_time,
        "Status_code responses" : status_code_response,
        "Top 3 accessed endpoints": islice(dict(sorted_endpoints).items(), 3)
    }
            
    




