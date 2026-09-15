# ChargeGrid Assistant — Sprint 03

**Repositório:** https://github.com/FIAP-Time6-GoodWe-2026/Sprint3-Prompt-IA-NexusChargeGridInteligence

Refactory conversacional do ChargeGrid Assistant (EV Challenge 2026 — GoodWe
× FIAP), migrando o núcleo do chatbot para um framework de agentes
(**LangChain / LangGraph**), com memória por sessão nativa, guardrails de
segurança e comparação entre modelos.

Os modelos rodam **localmente via Ollama** — sem token de API, sem custo por
requisição e sem depender de crédito de serviço externo (mesma abordagem
usada nas Aulas 5 e 6 da disciplina).

## Integrantes

| Nome | RM |
|---|---|
| Alan Junio Araujo de Souza | 574112 |
| Arthur Vettorazzo de Souza | 569445 |
| Brayan Barbosa Dos Santos | 573682 |
| Giovanne Gomes Petenuci | 574091 |
| Gustavo Zibini Belizario | 561376 |
| Luiz Otávio Brito Freixo | 569977 |

**Turma:** 1CCPZ — Ciências da Computação (Noturno) — FIAP

## Por que LangChain + Ollama local?

**LangChain** foi escolhido pelo ecossistema maduro e por já termos
trabalhado com ele nas aulas de "Frameworks na prática" e de prompt
injection, o que permitiu reaproveitar diretamente os padrões de guardrail
vistos em aula.

**Ollama local** foi escolhido depois de esbarrar no limite de créditos da
Hugging Face Inference API durante os testes: rodar o modelo localmente
elimina esse problema por completo — sem token, sem rate limit, sem custo
por chamada — ao custo de precisar de uma máquina com RAM/GPU suficiente
para os modelos escolhidos (8B parâmetros rodam bem em CPU moderna, mais
rápido ainda com GPU).

## O que mudou desde a Sprint 1/2 (resumo)

| | Sprint 1/2 (legado) | Sprint 03 (atual) |
|---|---|---|
| Orquestração | System prompt reenviado manualmente + histórico em lista Python | `create_agent` (LangChain/LangGraph) |
| Modelo | DeepSeek V3 via Hugging Face Inference API (remoto, pago por uso) | Modelo local via Ollama (gratuito, sem token) |
| Memória | Gerenciada "na mão" a cada chamada | Checkpointer nativo por `thread_id` (3+ turnos) |
| Ferramentas | Nenhuma — tudo colado no system prompt | 2 tools (`consultar_politica_chargegrid`, `diagnosticar_problema_tecnico`) |
| Segurança | Sem tratamento explícito de injeção | Hierarquia de instruções + delimitação de conteúdo recuperado + 7 testes de segurança dedicados |
| Comparação de modelos | Só DeepSeek-V3 | 2 modelos locais (Qwen3-8b + Llama3.1-8b), parametrização documentada |

A versão legado foi recriada em `src/legacy_chatbot.py` **apenas para servir
de baseline do comparativo antes/depois** — não faz parte da entrega
funcional da Sprint 03. Ela também roda contra o Ollama local (para isolar
a variável "framework" na comparação), mesmo que a Sprint 1/2 de verdade
tenha usado a Hugging Face Inference API — isso está documentado no próprio
código, para não gerar confusão no relatório de evolução.

## Estrutura do projeto

```
.
├── main.py                       # chat interativo via terminal
├── requirements.txt               # dependências Python
├── entrega_sprint3.txt            # integrantes, RM, turma e link do repo
├── .env.example                   # modelo de configuração (opcional, ver abaixo)
├── .gitignore                     # baseado no template Python do GitHub + .env
├── src/
│   ├── config.py                   # modelos/hiperparâmetros (Ollama local)
│   ├── prompts.py                  # system prompt com hierarquia de instruções
│   ├── tools.py                     # tools do agente (política + diagnóstico)
│   ├── agent.py                      # create_agent + memória por sessão
│   └── legacy_chatbot.py              # baseline Sprint 1/2 (apenas para comparação)
├── tests/
│   ├── eval_set.py                  # 7 testes funcionais + 7 testes de segurança
│   ├── run_eval.py                   # roda tudo e gera comparativo antes/depois
│   └── output/                        # gerado ao rodar run_eval.py (não versionado)
│       ├── comparativo_antes_depois.md
│       └── resultados_brutos.json
└── docs/
    ├── relatorio_modelos.md           # Bloco B — comparação entre modelos + Bloco C — segurança
    └── relatorio_evolucao.pdf          # Bloco D — relatório de evolução do projeto
```

## Pré-requisitos: instalar o Ollama e baixar os modelos

**1. Instalar o Ollama** (uma vez por máquina):

- **Linux/macOS:**
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
- **Windows:** baixe o instalador em [ollama.com/download](https://ollama.com/download)

**2. Confirmar que o servidor do Ollama está rodando.** O instalador
geralmente já deixa o Ollama rodando em segundo plano (ícone na bandeja do
sistema, no Windows/macOS). Para confirmar, rode:

```bash
curl http://localhost:11434
```

Se aparecer `Ollama is running`, está tudo certo. **Não é necessário** rodar
`ollama serve` manualmente — se você rodar e aparecer um erro de porta já em
uso (`bind: ... address already in use`), isso só confirma que o servidor já
está ativo; pode ignorar o erro.

**3. Baixar os modelos usados no projeto** (uma vez, pode demorar alguns
minutos dependendo da internet — os modelos ficam salvos localmente):

```bash
ollama pull qwen3:8b
ollama pull llama3.1:8b
```

> Se sua máquina tiver pouca RAM/VRAM, troque por versões menores (ex.:
> `qwen3:4b`, `llama3.2:3b`) — ver seção **Configuração via `.env`** abaixo.
> Só lembre de documentar a troca no `docs/relatorio_modelos.md`.

## Como rodar o projeto

```bash
git clone https://github.com/FIAP-Time6-GoodWe-2026/Sprint3-Prompt-IA-NexusChargeGridInteligence.git
cd Sprint3-Prompt-IA-NexusChargeGridInteligence

python -m venv .venv
source .venv/bin/activate      # Windows (PowerShell): .venv\Scripts\Activate.ps1

pip install -r requirements.txt

python main.py
```

Repare que **não existe um passo obrigatório de criar o `.env`** — o projeto
já roda direto com os valores padrão. A seção abaixo explica quando e por
que você pode querer criar um mesmo assim.

## Configuração via `.env` (opcional)

Esta versão **não usa nenhuma API paga nem token** — por isso o `.env` não é
obrigatório, diferente da versão antiga (Sprint 1/2), que dependia de um
token da Hugging Face para funcionar. Sem o `.env`, o projeto usa estes
valores padrão, definidos em `src/config.py`:

| Variável | Valor padrão | Serve para |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Endereço do servidor Ollama local |
| `CHARGEGRID_MODEL` | `qwen3:8b` | Modelo principal do agente |
| `CHARGEGRID_MODEL_COMPARE` | `llama3.1:8b` | Modelo usado só na comparação (Bloco B) |

Crie um `.env` **apenas se quiser sobrescrever algum desses valores** — por
exemplo, se sua máquina não aguentar os modelos de 8B e você quiser usar
versões menores, ou se o Ollama estiver rodando em outra porta/máquina:

```bash
cp .env.example .env
# depois edite o .env com os valores desejados
```

## Como rodar a avaliação (gera o comparativo antes/depois)

Com o Ollama rodando e os dois modelos já baixados:

```bash
python -m tests.run_eval
```

Gera `tests/output/comparativo_antes_depois.md` e
`tests/output/resultados_brutos.json` — os números finais já foram
transcritos manualmente, com a devida análise, para `docs/relatorio_modelos.md`
e `docs/relatorio_evolucao.pdf`.

## Segurança e guardrails (Bloco C)

- **Hierarquia de instruções** no system prompt (`src/prompts.py`):
  instruções do desenvolvedor têm prioridade absoluta sobre qualquer
  conteúdo vindo do usuário ou de uma tool.
- **Delimitação de conteúdo recuperado**: a tool `consultar_politica_chargegrid`
  sempre envolve o resultado em `<documento_recuperado>` e reforça, logo
  depois, que aquilo é dado — não comando.
- **Privilégio mínimo**: nenhuma tool executa ações reais (não aprova
  reembolso/desconto, não altera dados) — apenas leem e retornam texto.
- **7 casos de teste de segurança** em `tests/eval_set.py`, cobrindo:
  injeção indireta (via documento) e direta (via chat), tentativa de
  vazamento do system prompt, saída de escopo, e recusa de aconselhamento
  jurídico/financeiro/elétrico fora de competência. Resultado e justificativa
  caso a caso em `docs/relatorio_modelos.md` (seção 6).

## Sem API key no histórico

Esta versão não usa nenhuma API externa — os modelos rodam localmente via
Ollama, então não há token/credencial de serviço pago para vazar.

