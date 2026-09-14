"""
Configuração central do ChargeGrid Assistant — Sprint 03.

Carrega variáveis de ambiente (.env) e centraliza os parâmetros de modelo,
para que a comparação entre modelos (Bloco B da rubrica) fique documentada
em um único lugar em vez de espalhada pelo código.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError(
        "HF_TOKEN não encontrado. Copie .env.example para .env e preencha "
        "com seu token da Hugging Face (huggingface.co/settings/tokens)."
    )


@dataclass(frozen=True)
class ModelConfig:
    """Agrupa o id do modelo e os hiperparâmetros usados para chamá-lo.

    Manter isso como dataclass (em vez de dicts soltos) facilita o
    relatorio_modelos.md: cada ModelConfig usado no eval vira uma linha
    da tabela de comparação.
    """

    label: str          # nome amigável usado nos relatórios/logs
    repo_id: str         # id do modelo no Hugging Face Hub
    temperature: float
    top_p: float
    max_new_tokens: int


# Modelo principal (mantido da Sprint 1/2 — DeepSeek V3 via Inference API)
MODEL_PRIMARY = ModelConfig(
    label="DeepSeek-V3-0324",
    repo_id=os.getenv("CHARGEGRID_MODEL", "deepseek-ai/DeepSeek-V3-0324"),
    temperature=0.4,
    top_p=0.85,
    max_new_tokens=400,
)

# Modelo secundário — usado apenas no Bloco B (comparação entre modelos).
# Troque o repo_id / hiperparâmetros aqui conforme o resultado dos testes.
MODEL_SECONDARY = ModelConfig(
    label="Qwen2.5-72B-Instruct",
    repo_id=os.getenv("CHARGEGRID_MODEL_COMPARE", "Qwen/Qwen2.5-72B-Instruct"),
    temperature=0.4,
    top_p=0.85,
    max_new_tokens=400,
)

# Modo "diagnóstico" (saída JSON estruturada, herdado da Sprint 2 —
# usado pela tool de diagnóstico de falha técnica)
DIAGNOSTIC_TEMPERATURE = 0.1
DIAGNOSTIC_TOP_P = 0.80
DIAGNOSTIC_MAX_NEW_TOKENS = 600
