# Plataforma de Estudos (MVP)

Projeto Python para um núcleo de estudo guiado com planejamento, tutoria e política de decisão.

## Visão geral

A aplicação é uma prova de conceito para um sistema que:

- recebe um pedido de estudo (`topic`, `level`, `goal`)
- gera um plano de estudo sequencial
- apresenta um passo por vez ao estudante
- registra respostas e histórico em um portfólio
- aplica uma política de decisão para avançar ou repetir passos

## Arquitetura

O projeto está organizado em módulos principais:

- `main.py`: interface de linha de comando e loop de execução
- `core/nucleus.py`: orquestra o ciclo de estudo, validação e delegação
- `core/portfolio.py`: modelo do histórico de sessões e respostas
- `core/policy.py`: lógica de decisão entre avançar e repetir
- `core/storage.py`: persistência JSON do portfólio
- `agents/planner_agent.py`: gerador de plano de estudo
- `agents/tutor_agent.py`: gerador de instruções por passo

### Fluxo principal

1. `main.py` inicia a aplicação e lê `topic`, `level` e `goal` do usuário.
2. `main.py` carrega o portfólio salvo em `data/portfolio.json`.
3. `Nucleus.start()` cria uma nova sessão e chama o `SimplePlannerAgent` para gerar o plano.
4. `Nucleus.explain_step()` chama o tutor para obter a instrução do passo atual.
5. O loop interativo do cliente imprime o passo e solicita a resposta do aluno.
6. A resposta é registrada no `StudentPortfolio` e salva em disco.
7. `Nucleus.decide()` delega à `SimpleDecisionPolicy` para determinar se deve avançar ou repetir.
8. O ciclo se repete até o plano terminar.

## Componentes principais

### `core.nucleus.Nucleus`

Responsável por:

- validar entradas do pedido de estudo
- criar e gerenciar sessões de estudo
- construir o plano de estudo
- traduzir passos em instruções de tutoria
- delegar decisões à política específica

### `agents.planner_agent.SimplePlannerAgent`

Gera um plano fixo de 5 passos para qualquer tema:

1. Diagnóstico rápido
2. Conceito base
3. Exemplo guiado
4. Prática controlada
5. Checagem de domínio

Cada passo é um `StudyStep(title, prompt)`.

### `agents.tutor_agent.PlaceholderTutorAgent`

Retorna atualmente apenas o texto do prompt do passo.

### `core.policy.SimpleDecisionPolicy`

Decide entre `retry` ou `advance` com base em regras:

- resposta vazia => retry com fricção
- resposta repetida no mesmo passo => retry com fricção anti-loop
- resposta de baixa evidência => retry com fricção progressiva
- última etapa => advance e encerra
- caso contrário => advance

### `core.portfolio.StudentPortfolio`

Modelo do histórico das sessões de estudo.

- `StudySession` contém registros de cada passo
- `StepRecord` guarda índice do passo, resposta do aluno e timestamp
- `record_step()` salva um novo registro e cria a sessão se necessário

### `core.storage`

Funções de persistência:

- `load_portfolio(path)` carrega o JSON e reconstrói o `StudentPortfolio`
- `save_portfolio(portfolio, path)` grava o estado atual no JSON

Formato do arquivo em `data/portfolio.json`:

```json
{
  "sessions": {
    "<session_id>": {
      "session_id": "<session_id>",
      "records": [
        {
          "step_index": 0,
          "student_answer": "...",
          "created_at": "..."
        }
      ]
    }
  }
}
```

## Uso

Execute a aplicação no diretório do projeto:

```bash
python main.py
```

O usuário responderá via terminal para:

- Tema
- Nível
- Objetivo

Em seguida, a aplicação apresenta cada passo e registra as respostas.

## Extensões previstas

- substituir `PlaceholderTutorAgent` por um agente real de IA ou modelo de linguagem
- tornar `SimplePlannerAgent` configurável ou baseado em dados/contexto
- adicionar versões de política mais avançadas
- melhorar a UI e separar cliente/núcleo em camadas distintas
- adicionar testes automatizados para `policy`, `portfolio` e `storage`

## Estrutura de diretórios

- `main.py`
- `core/`
  - `nucleus.py`
  - `policy.py`
  - `portfolio.py`
  - `storage.py`
- `agents/`
  - `planner_agent.py`
  - `tutor_agent.py`
- `data/`
  - `portfolio.json`

## Observações técnicas

- O projeto usa dataclasses para modelos de domínio.
- A política de decisão está separada para suportar múltiplos comportamentos.
- O portfólio é persistido em JSON para facilitar inspeção e reuso.
- O núcleo (`Nucleus`) mantém o contrato do resultado para apoiar mudanças futuras sem quebrar o CLI.
