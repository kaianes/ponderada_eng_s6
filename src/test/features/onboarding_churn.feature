Feature: Taxa de Retenção de Entregadores

  Scenario Outline: Verificar a taxa de retenção de entregadores durante o período de onboarding
    Given um grupo de entregadores aceitou o primeiro pedido
    When verificamos quantos completaram pelo menos <min_pedidos> pedidos em até <periodo>
    Then pelo menos <taxa_esperada>% dos entregadores devem ter atingido essa meta

  Examples:
    | min_pedidos | periodo   | taxa_esperada |
    | 20          | 8         | 50            |
