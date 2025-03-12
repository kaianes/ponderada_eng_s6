from locust import HttpUser, task, between
import time
import firebase_admin
from firebase_admin import credentials, db
from random import randint
import os
from locust import HttpUser, task, between
from prometheus_client import start_http_server, Counter

cred_path = os.getenv("FIREBASE_CREDENTIALS", "/app/config/alocacao-entregadores-firebase-credenciais.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://alocacao-entregadores-default-rtdb.firebaseio.com/"
    })


# Referência para a coleção onde os logs serão salvos
logs_ref = db.reference("locust_logs")

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def get_entregador(self):
        # Gera um ID aleatório entre 1 e 10 para testar endpoints diferentes
        entregador_id = randint(1, 10)
        response = self.client.get(f"/entregadores/{entregador_id}")

        try:
            response_time = response.elapsed.total_seconds()
        except Exception:
            response_time = None

        # Cria o log com os dados desejados
        log_data = {
            "endpoint": f"/entregadores/{entregador_id}",
            "status_code": response.status_code,
            "response_time": response_time,
            "timestamp": time.time()
        }
        # Envia o log para o Firebase
        logs_ref.push(log_data)


#Prometheus
# Inicia o servidor de métricas do Prometheus na porta 9646
start_http_server(9646)

# Define uma métrica personalizada para contar requisições
requests_count = Counter('locust_requests_total', 'Total de requisições feitas pelo Locust')

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def get_entregador(self):
        requests_count.inc()  # Incrementa o contador a cada requisição
        self.client.get("/entregadores/1")
