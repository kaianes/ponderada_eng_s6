Feature: Precisão na Exibição da Taxa dos Pedidos

  Scenario Outline: Garantir que a UI exibe corretamente a taxa mais recente do banco de dados
    Given o banco de dados contém um pedido com uma taxa registrada
    When a UI exibe a taxa para o entregador
    Then a taxa exibida deve corresponder exatamente ao valor mais recente no banco de dados

  Examples:
    | pedido_id | taxa_esperada | taxa_exibida
    | 101       | 5.99          | 5.99
    | 102       | 7.50          | 7.50
    | 103       | 3.25          | 3.25
