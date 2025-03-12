from firebase_admin import db
from services.alocation import selecionar_entregadores
from fastapi import HTTPException

async def atribuir_pedido(pedido_id: str, latitude: float, longitude: float):
    melhores_entregadores = selecionar_entregadores(latitude, longitude)

    if not melhores_entregadores:
        raise HTTPException(status_code=404, detail="Nenhum entregador disponível dentro do raio máximo")

    ref = db.reference(f"pedidos/{pedido_id}/candidatos")
    ref.set(melhores_entregadores)

    return {"message": "Pedido enviado aos entregadores", "candidatos": melhores_entregadores}
