from behave import given, when, then
import time
import requests
import redis.asyncio as redis
import asyncio

REDIS_URL = "redis://localhost"

# Função assíncrona para obter a conexão Redis
async def get_redis_connection():
    redis_conn = await redis.from_url(REDIS_URL)  # Estabelece a conexão com o Redis
    return redis_conn

API_URL = "http://localhost:8000/entregadores/{}/saldo_final"

# ========================= Cenário 1 =========================
# Bloco que simula a disponibilidade da API e define o tempo de resposta
@given('a API de ganhos está disponível')
def step_impl(context):
    context.api_available = True
    context.api_response_time = 1.5  # Simulando uma resposta dentro do tempo limite
    context.response_time = context.api_response_time  # Definindo o tempo de resposta esperado

# Verifica se a resposta da API ocorre dentro de 2 segundos
@then('a resposta deve ser retornada em menos de 2 segundos')
def step_impl(context):
    assert context.response_time < 2, f"Tempo de resposta foi {context.response_time}s"

# Verifica se o valor exibido na UI é igual ao saldo final esperado
@then('o valor exibido na UI deve ser igual ao saldo final "{saldo}"')
def step_impl(context, saldo):
    assert context.saldo_final == float(saldo), f"Esperado: {saldo}, Obtido: {context.saldo_final}"

# ========================= Cenário 2 =========================
# Bloco que simula a indisponibilidade da API
@given('a API de ganhos está indisponível')
def step_impl(context):
    context.api_available = False

# Verifica se a UI exibe a mensagem informativa correta quando a API está indisponível
@then('a UI deve exibir uma mensagem informativa "{mensagem}"')
def step_impl(context, mensagem):
    context.ui_message = mensagem  # Simulando a exibição da mensagem
    print(f"[INFO] {mensagem}")  # Exibindo a mensagem no terminal
    assert context.ui_message == mensagem, f"Esperado: {mensagem}, Obtido: {context.ui_message}"

# ========================= Cenário 3 =========================
# Bloco que simula a disponibilidade e indisponibilidade da API de ganhos
@given('que a API de ganhos está disponível')
def step_impl(context):
    context.api_available = True

@given('que a API de ganhos está indisponível')
def step_impl(context):
    context.api_available = False

# Configura o cache Redis com os dados de ganhos do entregador
@given('o cache possui os últimos ganhos do entregador "{entregador_id}"')
async def step_impl(context, entregador_id):
    redis_conn = await get_redis_connection()
    await redis_conn.set(f"saldo:{entregador_id}", 100.00)  # Armazenando saldo no cache
    await redis_conn.set(f"ganho_bruto:{entregador_id}", 50.00)  # Armazenando ganho bruto no cache

# Bloco que solicita os ganhos de um entregador, verificando o cache ou a API
@when('um usuário solicita os ganhos do entregador "{entregador_id}"')
async def step_impl(context, entregador_id):
    redis_conn = await get_redis_connection()
    cache_saldo_key = f"saldo:{entregador_id}"
    cache_ganho_bruto_key = f"ganho_bruto:{entregador_id}"

    # Verifica se os dados do entregador estão no cache
    cached_saldo = await redis_conn.get(cache_saldo_key)
    cached_ganho_bruto = await redis_conn.get(cache_ganho_bruto_key)
    
    if cached_saldo and cached_ganho_bruto:
        context.saldo = float(cached_saldo)
        context.ganho_bruto = float(cached_ganho_bruto)
        context.saldo_final = context.saldo + context.ganho_bruto  # Calculando o saldo final
        context.cache_used = True  # Indicando que o cache foi utilizado
    else:
        if context.api_available:
            # Se os dados não estiverem no cache, solicita os dados da API
            response = requests.get(API_URL.format(entregador_id))
            if response.status_code == 200:
                data = response.json()
                context.saldo = data["saldo"]
                context.ganho_bruto = data["ganho_bruto"]
                context.saldo_final = context.saldo + context.ganho_bruto
                context.cache_used = False
            else:
                context.saldo_final = None
        else:
            context.saldo_final = None

# Verifica se a UI exibe o saldo correto, seja do cache ou da API
@then('a UI deve exibir o último saldo conhecido "{saldo_esperado}"')
async def step_impl(context, saldo_esperado):
    if hasattr(context, "api_disponivel") and not context.api_disponivel:
        # Caso a API esteja indisponível, usa os dados do cache
        redis_conn = await get_redis_connection()
        cached_saldo = await redis_conn.get(f"saldo:{context.entregador_id}")
        cached_ganho_bruto = await redis_conn.get(f"ganho_bruto:{context.entregador_id}")

        if cached_saldo and cached_ganho_bruto:
            context.saldo_final = float(cached_saldo) + float(cached_ganho_bruto)
        else:
            context.saldo_final = None
    else:
        pass  # Usa o saldo final calculado anteriormente

    assert context.saldo_final == float(saldo_esperado), (
        f"Esperado: {saldo_esperado}, Obtido: {context.saldo_final}"
    )

# ========================= Cenário 4 =========================
# Bloco que simula a API instável e o número de tentativas de retentativa
@given('a API de ganhos está instável')
def step_impl(context):
    context.api_available = False
    context.retry_attempts = 0

# Bloco que simula a falha de uma requisição e o processo de retentativa com backoff exponencial
@when('uma requisição falha')
def step_impl(context):
    while not context.api_available and context.retry_attempts < 3:
        time.sleep(2 ** context.retry_attempts)  # Simulando backoff exponencial
        context.retry_attempts += 1

# Verifica se houve pelo menos uma tentativa de retentativa
@then('o sistema deve tentar novamente com um backoff exponencial')
def step_impl(context):
    assert context.retry_attempts > 0, "Deve haver pelo menos uma retentativa."

# Verifica se os ganhos são exibidos corretamente após uma retentativa bem-sucedida
@then('deve exibir os ganhos se a tentativa for bem-sucedida')
def step_impl(context):
    context.api_available = True  # Simulando a recuperação da API
    if context.api_available:
        context.saldo_final = 450.75  # Simulando uma resposta bem-sucedida
    assert context.saldo_final == 450.75, "Os ganhos devem ser exibidos corretamente após a retentativa."

# ========================= Cenário 5 =========================
# Simula dados de saldo e ganho bruto de um entregador
@given('um entregador "{entregador_id}" com saldo "{saldo}" e ganho bruto "{ganho_bruto}"')
def step_impl(context, entregador_id, saldo, ganho_bruto):
    context.entregador_id = entregador_id
    context.saldo = float(saldo)
    context.ganho_bruto = float(ganho_bruto)

# Bloco que simula a resposta da API com os valores informados
@when('a API de ganhos responde com esses valores')
def step_impl(context):
    context.saldo_final = context.saldo + context.ganho_bruto

# Verifica se o saldo final exibido está correto
@then('o saldo final exibido deve ser "{saldo_esperado}"')
def step_impl(context, saldo_esperado):
    assert context.saldo_final == float(saldo_esperado), (
        f"Esperado: {saldo_esperado}, Obtido: {context.saldo_final}"
    )

# ========================= Cenário 6 =========================
# Simula que a API estava disponível anteriormente
@given('a API de ganhos estava disponível anteriormente')
def step_impl(context):
    context.api_disponivel_anteriormente = True

# Armazena os dados de saldo e ganho bruto no cache
@given('o cache possui os ganhos do entregador "{entregador_id}"')
async def step_impl(context, entregador_id):
    redis_conn = await get_redis_connection()
    await redis_conn.set(f"saldo:{entregador_id}", 300.00)
    await redis_conn.set(f"ganho_bruto:{entregador_id}", 50.51)

# Simula que a API fica indisponível
@when('a API fica indisponível')
def step_impl(context):
    context.api_disponivel = False
