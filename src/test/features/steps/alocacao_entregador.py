from behave import given, when, then
import time
import random
from features.steps.data_alocacao import MAX_TEMPO_BUSCA, RAIO_INICIAL, INCREMENTO_RAIO

# Cenário inicial: O sistema inicia a busca por um entregador disponível.
# A busca é realizada por um tempo máximo, com o raio de pesquisa aumentando progressivamente.
# Durante a busca, há uma chance de encontrar um entregador ou identificar entregadores que estão finalizando pedidos.
@given("o sistema inicia a busca por um entregador disponível")
def step_given_sistema_em_busca(context):
    context.tempo_busca = 0  # Tempo decorrido na busca
    context.raio_busca = RAIO_INICIAL  # Define o raio inicial de pesquisa
    context.entregador_encontrado = False  # Flag para indicar se um entregador foi encontrado
    context.entregadores_proximos = []  # Lista de entregadores próximos para possível alerta

    print(f"[INFO] Iniciando busca por entregador. Raio inicial: {context.raio_busca}m")

    while context.tempo_busca < MAX_TEMPO_BUSCA:
        time.sleep(60)  # Simula a passagem do tempo real (1 minuto)
        context.tempo_busca += 1
        context.raio_busca += INCREMENTO_RAIO  # Expande o raio de busca

        print(f"[INFO] Minuto {context.tempo_busca}: Expansão da busca para {context.raio_busca}m.")

        # Simulação de um evento aleatório onde um entregador é encontrado
        if random.random() < 0.4:  
            context.entregador_encontrado = True
            print(f"[SUCESSO] Entregador encontrado no minuto {context.tempo_busca} dentro de {context.raio_busca}m.")
            break  # Finaliza a busca imediatamente

        # Simulação de identificação de entregadores que podem ficar disponíveis em breve
        if random.random() < 0.3:  
            entregador_id = f"E{random.randint(100, 999)}"
            print(f"[ALERTA] Entregador {entregador_id} pode ser alertado para um novo pedido.")
            context.entregadores_proximos.append(entregador_id)

    # Caso nenhum entregador seja encontrado dentro do tempo máximo, um erro é registrado
    context.erro = None  # Inicializa a variável de erro
    if not context.entregador_encontrado:
        context.erro = "Nenhum entregador disponível dentro do tempo máximo"
        print(f"[ERRO] {context.erro}. Total de {len(context.entregadores_proximos)} entregadores próximos identificados.")
    else:
        print(f"[SUCESSO] Entregador alocado com sucesso em {context.tempo_busca} minutos.")

# Verificação do sucesso da busca dentro do tempo estipulado
@when("o sistema encontra um entregador antes de 15 minutos")
def step_when_encontra_entregador(context):
    context.tempo_busca = random.randint(1, 14)  # Garante que o tempo de busca será menor que 15 minutos
    context.entregador_encontrado = True
    print(f"[SUCESSO] Entregador encontrado dentro de {context.tempo_busca} minutos.")

# Caso o tempo máximo seja excedido, o sistema marca a busca como falha
@when("o tempo de busca ultrapassa 15 minutos")
def step_when_tempo_excedido(context):
    try:
        if context.tempo_busca <= 15:
            raise ValueError("Erro: Tempo de busca não ultrapassou 15 minutos.")
        
        context.busca_falhou = True  # Indica que a busca não teve sucesso
        print(f"[LOG] Tempo final de busca: {context.tempo_busca} minutos. Nenhum entregador encontrado.")
    
    except Exception as e:
        context.erro = str(e)
        print(f"[ERRO] {context.erro}")

# Simulação da ausência de entregadores próximos que poderiam ser alertados
@when("não há entregadores próximos com pedidos quase finalizados")
def step_when_nao_ha_entregadores_proximos(context):
    context.entregadores_proximos = []  # Limpa a lista de entregadores próximos
    print("[LOG] Nenhum entregador próximo identificado.")

# Simulação da existência de entregadores próximos que podem ser alertados
@when("há entregadores próximos com pedidos quase finalizados")
def step_when_ha_entregadores_proximos(context):
    context.entregadores_proximos = [f"E{random.randint(100, 999)}" for _ in range(3)]
    print(f"[INFO] {len(context.entregadores_proximos)} entregadores próximos identificados.")

# Confirmação de que o entregador encontrado será alocado para a entrega
@then("o sistema deve alocar o entregador para a entrega")
def step_then_alocar_entregador(context):
    if context.entregador_encontrado:
        print(f"[SUCESSO] Entregador alocado para a entrega após {context.tempo_busca} minutos.")
    else:
        print("[ERRO] Nenhum entregador encontrado.")

# Caso haja entregadores próximos, eles devem ser alertados
@then("o sistema deve alertar entregadores próximos com pedidos quase finalizados")
def step_then_alertar_entregadores(context):
    try:
        if not context.entregadores_proximos:
            print("[LOG] Nenhum entregador próximo disponível para alerta.")
            return

        # Notificação de cada entregador próximo identificado
        context.entregadores_alertados = []
        for entregador in context.entregadores_proximos:
            print(f"[ALERTA] Notificando entregador {entregador} sobre a nova entrega.")
            context.entregadores_alertados.append(entregador)
        
        print(f"[SUCESSO] {len(context.entregadores_alertados)} entregadores foram notificados.")
    
    except Exception as e:
        context.erro = str(e)
        print(f"[ERRO] Falha ao enviar alertas: {context.erro}")

# Caso não haja entregadores disponíveis, nenhum alerta deve ser enviado
@then("o sistema não deve enviar alertas")
def step_then_nao_enviar_alertas(context):
    if context.erro == "Nenhum entregador disponível dentro do tempo máximo":
        print("[LOG] Não há entregadores para alertar, portanto nenhum alerta será enviado.")
    else:
        print("[ERRO] O sistema tentou enviar alertas quando não deveria.")

# Confirmação de que todos os entregadores próximos foram alertados corretamente
@then("o sistema deve alertar todos os entregadores próximos disponíveis")
def step_then_alertar_todos_os_entregadores(context):
    if context.entregadores_proximos:
        context.entregadores_alertados = []
        for entregador in context.entregadores_proximos:
            print(f"[ALERTA] Notificando entregador {entregador} sobre a nova entrega.")
            context.entregadores_alertados.append(entregador)
        
        if len(context.entregadores_alertados) == len(context.entregadores_proximos):
            print(f"[SUCESSO] {len(context.entregadores_alertados)} entregadores foram alertados com sucesso.")
        else:
            print("[ERRO] Nem todos os entregadores foram alertados.")
    else:
        print("[ERRO] Não há entregadores próximos para alertar.")
