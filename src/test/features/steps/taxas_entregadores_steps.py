import requests
from behave import given, when, then

API_URL = "https://api.com"

@given("o banco de dados contém um pedido com uma taxa registrada")
def step(context):
    response = requests.get(f"{API_URL}/pedidos/ultima-taxa")

    if response.status_code != 200:
        raise Exception("Erro ao obter a taxa do banco de dados!")

    data = response.json()
    context.taxa_esperada = data.get("taxa", None)

    assert context.taxa_esperada is not None, "Nenhuma taxa foi encontrada no banco de dados!"

@when("a UI exibe a taxa para o entregador")
def step(context):
    response = requests.get(f"{API_URL}/ui/taxa-exibida")

    if response.status_code != 200:
        raise Exception("Erro ao obter a taxa exibida na UI!")

    data = response.json()
    context.taxa_exibida = data.get("taxa", None)

    assert context.taxa_exibida is not None, "A UI não exibiu nenhum valor de taxa!"

@then("a taxa exibida deve corresponder exatamente ao valor mais recente no banco de dados")
def step(context):
    assert context.taxa_exibida == context.taxa_esperada, (
        f"Divergência detectada! Taxa no banco: {context.taxa_esperada}, "
        f"Taxa exibida na UI: {context.taxa_exibida}"
    )
