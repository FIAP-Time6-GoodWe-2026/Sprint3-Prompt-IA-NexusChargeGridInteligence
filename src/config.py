"""
Configuração central do ChargeGrid Assistant — Sprint 03.

Nesta versão os modelos rodam LOCALMENTE via Ollama (mesma abordagem das
Aulas 5 e 6) — não há nenhum token de API nem custo por requisição. O único
pré-requisito é ter o Ollama instalado e os modelos baixados com
"ollama pull" antes de rodar o projeto (ver README.md).
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


@dataclass(frozen=True)
class ModelConfig:
    """Agrupa o nome do modelo (tag do Ollama) e os hiperparâmetros usados
    para chamá-lo. Manter isso como dataclass facilita o relatorio_modelos.md:
    cada ModelConfig usado no eval vira uma linha da tabela de comparação.
    """

    label: str          # nome amigável usado nos relatórios/logs
    ollama_tag: str       # tag do modelo no Ollama (ex.: "qwen3:8b")
    temperature: float
    top_p: float
    num_predict: int      # equivalente ao max_tokens no Ollama


# Modelo principal — troque a tag se quiser testar outro modelo local.
# Baixe antes com: ollama pull qwen3:8b
MODEL_PRIMARY = ModelConfig(
    label="Qwen3-8b (Ollama local)",
    ollama_tag=os.getenv("CHARGEGRID_MODEL", "qwen3:8b"),
    temperature=0.4,
    top_p=0.85,
    num_predict=1200,
)

# Modelo secundário — usado apenas no Bloco B (comparação entre modelos).
# Baixe antes com: ollama pull llama3.1:8b
MODEL_SECONDARY = ModelConfig(
    label="Llama3.1-8b (Ollama local)",
    ollama_tag=os.getenv("CHARGEGRID_MODEL_COMPARE", "llama3.1:8b"),
    temperature=0.4,
    top_p=0.85,
    num_predict=800,
)

# Modo "diagnóstico" (saída JSON estruturada, herdado da Sprint 2 —
# usado pela tool de diagnóstico de falha técnica)
DIAGNOSTIC_TEMPERATURE = 0.1
DIAGNOSTIC_TOP_P = 0.80
DIAGNOSTIC_NUM_PREDICT = 600
