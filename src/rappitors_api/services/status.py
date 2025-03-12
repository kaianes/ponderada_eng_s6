from firebase_admin import db
from fastapi import HTTPException

async def atualizar_estado_pedido(pedido_id: int, estado: str):
    pedidos_ref = db.reference("pedidos")

    pedido = pedidos_ref.child(str(pedido_id)).get()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    pedidos_ref.child(str(pedido_id)).update({"estado": estado})
    return {"message": "Estado do pedido atualizado"}

async def atualizacao_manual_entregador(entregador_id: str, estado: str):
    entregadores_ref = db.reference("entregadores")

    entregador = entregadores_ref.child(entregador_id).get()
    if not entregador:
        raise HTTPException(status_code=404, detail="Entregador não encontrado")

    entregadores_ref.child(entregador_id).update({"estado": estado})
    return {"message": "Estado do entregador atualizado"}
