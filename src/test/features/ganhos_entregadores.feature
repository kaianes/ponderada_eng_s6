Feature: Validação da exibição de ganhos dos entregadores

  Scenario: A UI deve exibir os ganhos corretamente em menos de 2 segundos
    Given a API de ganhos está disponível
    When um usuário solicita os ganhos do entregador "E1"
    Then a resposta deve ser retornada em menos de 2 segundos
    And o valor exibido na UI deve ser igual ao saldo final "171.26"

  Scenario: Exibir mensagem informativa quando a API não responder em 2 segundos
    Given a API de ganhos está indisponível
    When um usuário solicita os ganhos do entregador "E2"
    Then a UI deve exibir uma mensagem informativa "Dados temporariamente indisponíveis"

  Scenario: Garantir que a soma dos ganhos seja correta
    Given um entregador "E3" com saldo "220" e ganho bruto "34.91"
    When a API de ganhos responde com esses valores
    Then o saldo final exibido deve ser "254.91"

  Scenario: Cache deve fornecer último saldo final conhecido se a API estiver indisponível
    Given a API de ganhos estava disponível anteriormente
    And o cache possui os ganhos do entregador "E5"
    When a API fica indisponível
    Then a UI deve exibir o último saldo conhecido "350.51"

  Scenario: Requisições devem ter retentativa automática com backoff exponencial
    Given a API de ganhos está instável
    When uma requisição falha
    Then o sistema deve tentar novamente com um backoff exponencial
    And deve exibir os ganhos se a tentativa for bem-sucedida
  

