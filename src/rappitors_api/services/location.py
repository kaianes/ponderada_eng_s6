from firebase_admin import db

async def atualizar_localizacao(entregador_id: str, latitude: float, longitude: float):
    ref = db.reference(f"entregadores/{entregador_id}/localizacao")
    ref.set({"latitude": latitude, "longitude": longitude})
    return {"message": "Localização atualizada"}
