"""
Versão "legado" (Sprints 1/2) do núcleo conversacional — reconstruída aqui
APENAS para servir de baseline do comparativo antes/depois exigido no
Bloco D. Não faz parte da solução da Sprint 03; representa como o chatbot
funcionava antes do refactory:

- System prompt (sem hierarquia de instruções / sem guardrails explícitos)
  reenviado a cada chamada.
- Histórico de conversa mantido manualmente em uma lista Python.
- Sem tools/framework: O contexto do ChargeGrid é colado direto no
  system prompt, e a chamada ao modelo é feita direto pelo client do
  Ollama (sem LangChain), para deixar bem claro o "antes" do refactory.
"""

import ollama

from src.config import OLLAMA_HOST, ModelConfig

LEGACY_SYSTEM_PROMPT = """\
Você é o ChargeGrid Assistant, o assistente oficial do sistema de eletropostos
ChargeGrid Intelligence da GoodWe. Você apoia motoristas de veículos elétricos
que estão utilizando ou planejam utilizar eletropostos comerciais gerenciados
pelo ChargeGrid.

O ChargeGrid Intelligence controla a potência entre carregadores, exibe a
tarifa via LED (verde/amarelo/vermelho), integra energia solar, usa OCPP e
MODBUS, e suporta pagamento avulso, assinatura e plano premium.

Responda sempre em português claro, sem jargão técnico. Não invente valores
de tarifa ou tempo — oriente a consultar o app/totem. Se houver risco
elétrico (cheiro de queimado, faísca), oriente a desconectar e acionar o
suporte. Mantenha o foco em eletromobilidade e no ecossistema ChargeGrid.
"""


class LegacyChargeGridChatbot:
    """Réplica fiel do padrão Sprint 1/2: um único system prompt fixo +
    histórico de mensagens mantido "na mão" (lista de dicts), sem framework
    de agentes e sem tools. Roda contra o Ollama local (mesmo servidor
    usado pela versão nova) só para isolar a variável "framework" na
    comparação antes/depois — não é assim que a Sprint 1/2 rodava de fato
    (que usava a Hugging Face Inference API), mas garante que a diferença
    medida hoje seja "com framework" vs. "sem framework", não "modelo
    diferente".
    """

    def __init__(self, model_config: ModelConfig):
        self.model_config = model_config
        self.client = ollama.Client(host=OLLAMA_HOST)
        self.history: list[dict] = [{"role": "system", "content": LEGACY_SYSTEM_PROMPT}]

    def ask(self, pergunta: str) -> str:
        self.history.append({"role": "user", "content": pergunta})

        resposta = self.client.chat(
            model=self.model_config.ollama_tag,
            messages=self.history,
            options={
                "temperature": self.model_config.temperature,
                "top_p": self.model_config.top_p,
                "num_predict": self.model_config.num_predict,
            },
        )
        conteudo = resposta["message"]["content"]
        self.history.append({"role": "assistant", "content": conteudo})
        return conteudo
