from fastapi import FastAPI, HTTPException
from services.accept_order import responder_pedido
from services.alocation import selecionar_entregadores
from services.assignment import atribuir_pedido
from services.location import atualizar_localizacao
from services.status import atualizar_estado_pedido, atualizacao_manual_entregador
import firebase_admin
from firebase_admin import credentials, db
import os
import logging

cred_path = os.getenv("FIREBASE_CREDENTIALS", "../config/alocacao-entregadores-firebase-credenciais.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://alocacao-entregadores-default-rtdb.firebaseio.com/"
    })

db_ref = db.reference("entregadores")
app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/entregadores/{entregador_id}")
async def get_entregador(entregador_id: int):
    entregadores = db_ref.get()
    if not entregadores:
        raise HTTPException(status_code=404, detail="Nenhum entregador encontrado")
    entregador = next((e for e in entregadores if e["id"] == entregador_id), None)
    if not entregador:
        raise HTTPException(status_code=404, detail="Entregador não encontrado")
    return entregador

@app.get("/pedidos/{pedido_id}/taxa")
async def get_taxa_pedido(pedido_id: int):
    try:
        pedido = db.reference(f"pedidos/{pedido_id}").get()
        
        if not pedido:
            raise HTTPException(status_code=404, detail=f"Pedido {pedido_id} não encontrado no banco de dados.")

        taxa = pedido.get("taxa_do_entregador")
        
        if taxa is None:
            raise HTTPException(status_code=404, detail=f"O pedido {pedido_id} não contém taxa definida.")

        return {"pedido_id": pedido_id, "taxa_do_entregador": taxa}
    except Exception as e:
        logging.error(f"Erro ao buscar taxa do pedido {pedido_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a requisição.")

@app.post("/responder_pedido")
async def responder_pedido(pedido_id: int, entregador_id: int):
    ref_pedido = db.reference(f"pedidos/{pedido_id}")
    pedido = ref_pedido.get()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    candidatos = pedido.get("candidatos", [])
    if entregador_id not in candidatos:
        raise HTTPException(status_code=400, detail="Entregador não está na lista de candidatos")
    ref_pedido.update({"entregador_atribuido": entregador_id})
    return {"message": "Pedido aceito pelo entregador", "pedido_id": pedido_id, "entregador_id": entregador_id}

@app.post("/atribuir_pedido")
async def atribuir_pedido(pedido_id: int, latitude: float, longitude: float):
    ref_pedido = db.reference(f"pedidos/{pedido_id}")
    pedido = ref_pedido.get()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    entregadores = db.reference("entregadores").get()
    if not entregadores:
        raise HTTPException(status_code=404, detail="Nenhum entregador encontrado")
    melhores_entregadores = [e for e in entregadores if e.get("disponivel") and e.get("saldo", 0) > 0]
    if not melhores_entregadores:
        raise HTTPException(status_code=404, detail="Nenhum entregador disponível dentro do raio")
    candidatos = [e["id"] for e in melhores_entregadores]
    ref_pedido.update({"candidatos": candidatos})
    return {"message": "Entregadores atribuídos ao pedido", "pedido_id": pedido_id, "candidatos": candidatos}

@app.post("/localizacao")
async def api_atualizar_localizacao(entregador_id: int, latitude: float, longitude: float):
    return await atualizar_localizacao(entregador_id, latitude, longitude)

@app.put("/pedidos/{pedido_id}/atualizar_estado")
async def api_atualizar_estado_pedido(pedido_id: int, estado: str):
    return await atualizar_estado_pedido(pedido_id, estado)

@app.put("/entregadores/{entregador_id}/atualizar_estado")
async def api_atualizacao_manual_entregador(entregador_id: int, estado: str):
    ref_entregadores = db.reference("entregadores")
    entregadores = ref_entregadores.get()

    if not entregadores or not isinstance(entregadores, list):
        raise HTTPException(status_code=404, detail="Nenhum entregador encontrado")

    # Buscar o índice do entregador na lista
    entregador_index = next((i for i, e in enumerate(entregadores) if e["id"] == entregador_id), None)

    if entregador_index is None:
        raise HTTPException(status_code=404, detail="Entregador não encontrado")

    # Atualizar o estado do entregador
    entregadores[entregador_index]["estado"] = estado

    # Atualizar a lista completa no Firebase
    ref_entregadores.set(entregadores)

    return {
        "message": "Estado do entregador atualizado",
        "entregador_id": entregador_id,
        "novo_estado": estado
    }


