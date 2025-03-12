from firebase_admin import db
from fastapi import HTTPException

async def responder_pedido(pedido_id: str, entregador_id: str):
    ref = db.reference(f"pedidos/{pedido_id}/candidatos")
    candidatos = ref.get()

    if not candidatos or entregador_id not in candidatos:
        raise HTTPException(status_code=400, detail="Entregador não está na lista de candidatos")

    ref_final = db.reference(f"pedidos/{pedido_id}/entregador_atribuido")
    ref_final.set(entregador_id)

    return {"message": "Pedido aceito pelo entregador", "entregador": entregador_id}
