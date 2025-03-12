Feature: Busca por entregador disponível

  Scenario: Encontrar um entregador dentro do tempo máximo
    Given o sistema inicia a busca por um entregador disponível
    When o sistema encontra um entregador antes de 15 minutos
    Then o sistema deve alocar o entregador para a entrega

  Scenario: Tempo de busca ultrapassa 15 minutos sem encontrar um entregador
    Given o sistema inicia a busca por um entregador disponível
    When o tempo de busca ultrapassa 15 minutos
    Then o sistema deve alertar entregadores próximos com pedidos quase finalizados

  Scenario: Nenhum entregador próximo para receber alerta
    Given o sistema inicia a busca por um entregador disponível
    When o tempo de busca ultrapassa 15 minutos
    And não há entregadores próximos com pedidos quase finalizados
    Then o sistema não deve enviar alertas

  Scenario: Alertar múltiplos entregadores próximos
    Given o sistema inicia a busca por um entregador disponível
    When o tempo de busca ultrapassa 15 minutos
    And há entregadores próximos com pedidos quase finalizados
    Then o sistema deve alertar todos os entregadores próximos disponíveis
