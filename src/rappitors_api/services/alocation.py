import firebase_admin
from firebase_admin import db
import geopy.distance
import time
from typing import List

def buscar_entregadores_por_raio(ponto_central, raio_metros):
    ref = db.reference("entregadores")
    entregadores = ref.get()

    if not entregadores:
        return []

    entregadores_filtrados = [
        e for e in entregadores
        if e.get("disponivel") and e.get("saldo", 0) > 0
    ]

    return entregadores_filtrados

def selecionar_entregadores(latitude: float, longitude: float):
    ponto_central = {"latitude": latitude, "longitude": longitude}
    raio_metros = 500  # Raio inicial
    max_tentativas = 6  # Máximo de 6 tentativas (~6 min)

    for _ in range(max_tentativas):
        entregadores = buscar_entregadores_por_raio(ponto_central, raio_metros)

        if entregadores:
            top_3 = sorted(entregadores, key=lambda x: x[1]["saldo"], reverse=True)[:3]
            return [id for id, _ in top_3]

        raio_metros += 500  # Aumenta o raio de busca em 500m
        time.sleep(60)  # Aguarda 1 minuto antes de expandir a busca

    return []
