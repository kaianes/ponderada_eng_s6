import requests
from behave import given, when, then

# Definição da URL base da API
API_URL = "https://api.com"

# Verifica se pelo menos um entregador aceitou o primeiro pedido
@given("um grupo de entregadores aceitou o primeiro pedido")
def step(context):
    response = requests.get(f"{API_URL}/entregadores/primeiro-pedido")
    
    if response.status_code != 200:
        raise Exception("Erro ao obter dados da API!")

    data = response.json()
    context.entregadores_iniciais = data.get("total", 0)
    
    assert context.entregadores_iniciais > 0, "Nenhum entregador aceitou o primeiro pedido!"

# Passo do cenário de teste: Verifica quantos entregadores completaram os pedidos do onboarding dentro do período definido
@when("verificamos quantos completaram os {pedidos_onboarding} pedidos em {periodo} dias")
def step(context, pedidos_onboarding, periodo):
    context.pedidos_onboarding = int(pedidos_onboarding)
    context.periodo = int(periodo)

    response = requests.get(f"{API_URL}/entregadores/desempenho")

    if response.status_code != 200:
        raise Exception("Erro ao obter dados da API!")
    
    entregadores = response.json().get("entregadores", [])

    context.onboardings_concluidos = sum(
        1 for entregador in entregadores 
        if entregador["pedidos_completos"] >= context.pedidos_onboarding and entregador["tempo_conclusao"] <= context.periodo
    )
    
# Passo do cenário de teste: Verifica se a taxa de retenção esperada foi atingida
@then("pelo menos {taxa_esperada}% dos entregadores devem ter atingido essa meta e completado o período de onboarding")
def step(context, taxa_esperada):
    taxa_esperada = float(taxa_esperada)

    if context.entregadores_iniciais != 0:
        taxa_retencao = (context.onboardings_concluidos / context.entregadores_iniciais) * 100
    else:
        raise Exception("Nenhum entregador inicial para calcular retenção!")


    assert taxa_retencao >= taxa_esperada, f"A taxa de retenção foi de {taxa_retencao}%, menor que o esperado ({taxa_esperada}%)!"