"""
Executa o eval set completo (Sprint 03) e gera:

1. tests/output/comparativo_antes_depois.md
   -> tabela exigida no Bloco D (Sprints 1/2 vs Sprint 03), com qualidade
      (preenchimento manual após leitura), tokens/turno (aproximado),
      latência média e resultado dos testes de segurança.
2. tests/output/resultados_brutos.json
   -> respostas completas de cada teste, para consulta/anotação manual.

Uso:
    python -m tests.run_eval

Requer o Ollama rodando localmente ("ollama serve") com os dois modelos
já baixados ("ollama pull qwen3:8b" e "ollama pull llama3.1:8b"). Cada
teste roda no seu próprio hardware, então a latência varia conforme
CPU/GPU disponível.
"""

import json
import time
from pathlib import Path
from statistics import mean

from src.agent import ask, build_agent
from src.config import MODEL_PRIMARY, MODEL_SECONDARY
from src.legacy_chatbot import LegacyChargeGridChatbot
from tests.eval_set import FUNCTIONAL_TESTS, SECURITY_TESTS

OUTPUT_DIR = Path(__file__).parent / "output"


def _approx_tokens(texto: str) -> int:
    """Aproximação simples de contagem de tokens (~4 caracteres por token
    em português/inglês). Suficiente para comparação relativa entre
    versões — para uma contagem exata, troque por um tokenizer real do
    modelo em uso.
    """
    return max(1, len(texto) // 4)


def _run_functional(model_config, versao: str) -> list[dict]:
    resultados = []

    if versao == "legado":
        bot = LegacyChargeGridChatbot(model_config)
        pergunta_fn = bot.ask
    else:
        agent = build_agent(model_config)
        session_id = f"eval-{versao}-{model_config.label}"
        pergunta_fn = lambda pergunta: ask(agent, pergunta, session_id)

    for caso in FUNCTIONAL_TESTS:
        inicio = time.perf_counter()
        resposta = pergunta_fn(caso.pergunta)
        latencia = time.perf_counter() - inicio

        resultados.append({
            "id": caso.id,
            "categoria": caso.categoria,
            "pergunta": caso.pergunta,
            "resposta": resposta,
            "tokens_aprox": _approx_tokens(resposta),
            "latencia_s": round(latencia, 2),
        })
    return resultados


def _run_security(model_config) -> list[dict]:
    agent = build_agent(model_config)
    session_id = f"eval-security-{model_config.label}"
    resultados = []

    for caso in SECURITY_TESTS:
        resposta = ask(agent, caso.pergunta, session_id)
        resposta_lower = resposta.lower()
        flags_encontradas = [f for f in caso.red_flags if f.lower() in resposta_lower]

        resultados.append({
            "id": caso.id,
            "categoria": caso.categoria,
            "pergunta": caso.pergunta,
            "descricao": caso.descricao,
            "resposta": resposta,
            "flags_encontradas": flags_encontradas,
            "checagem_automatica": "FALHOU (revisar)" if flags_encontradas else "sem sinal automático de falha",
        })
    return resultados


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("Rodando versão legado (Sprint 1/2) ...")
    legado = _run_functional(MODEL_PRIMARY, versao="legado")

    print("Rodando versão Sprint 03 (LangChain) — modelo principal ...")
    novo_primary = _run_functional(MODEL_PRIMARY, versao="novo")

    print("Rodando versão Sprint 03 (LangChain) — modelo secundário (comparação) ...")
    novo_secondary = _run_functional(MODEL_SECONDARY, versao="novo")

    print("Rodando testes de segurança (Sprint 03) ...")
    seguranca = _run_security(MODEL_PRIMARY)

    bruto = {
        "legado": legado,
        "novo_modelo_principal": novo_primary,
        "novo_modelo_secundario": novo_secondary,
        "seguranca": seguranca,
    }
    (OUTPUT_DIR / "resultados_brutos.json").write_text(
        json.dumps(bruto, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    latencia_legado = mean(r["latencia_s"] for r in legado)
    latencia_novo = mean(r["latencia_s"] for r in novo_primary)
    tokens_legado = mean(r["tokens_aprox"] for r in legado)
    tokens_novo = mean(r["tokens_aprox"] for r in novo_primary)
    falhas_seguranca = sum(1 for r in seguranca if r["flags_encontradas"])

    tabela = f"""\
# Comparativo antes/depois — Sprint 03

| Métrica | Sprints 1/2 (legado, manual) | Sprint 03 (LangChain) |
|---|---|---|
| Qualidade das respostas (nota no eval) | *preencher após leitura manual das {len(legado)} respostas em resultados_brutos.json* | *preencher após leitura manual* |
| Tokens por turno (aprox.) | {tokens_legado:.0f} | {tokens_novo:.0f} |
| Latência média (s) | {latencia_legado:.2f} | {latencia_novo:.2f} |
| Testes de segurança | não implementados na Sprint 1/2 | {len(seguranca) - falhas_seguranca}/{len(seguranca)} sem sinal automático de falha |

Observações:
- A "qualidade das respostas" precisa de leitura humana comparando cada
  resposta ao gabarito do modelo_de_teste.txt (Sprint 1), como foi feito na
  Sprint 2 — preencha a nota (Adequada/Parcial/Inadequada) por caso.
- A checagem automática de segurança busca apenas por substrings
  suspeitas; qualquer "FALHOU (revisar)" deve ser lido manualmente antes de
  virar conclusão no relatório.
- Tokens/turno são aproximados (len // 4); ajuste para contagem exata do
  tokenizer do modelo se quiser precisão maior no relatório.
"""
    (OUTPUT_DIR / "comparativo_antes_depois.md").write_text(tabela, encoding="utf-8")

    print("\nConcluído. Arquivos gerados em tests/output/:")
    print(" - resultados_brutos.json")
    print(" - comparativo_antes_depois.md")


if __name__ == "__main__":
    main()
