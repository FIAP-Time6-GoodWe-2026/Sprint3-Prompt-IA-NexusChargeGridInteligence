"""
Núcleo do agente ChargeGrid Assistant — Sprint 03.

Ganho do refactory em relação à Sprint 1/2:
- Sprint 1/2: system prompt injetado manualmente a cada chamada + histórico
  de mensagens gerenciado "na mão" em uma lista Python, via chamadas
  remotas à Hugging Face Inference API.
- Sprint 03: create_agent (LangChain/LangGraph) decide quando chamar cada
  tool, a memória por sessão é gerenciada nativamente por um checkpointer
  associado a um thread_id, e o modelo roda LOCALMENTE via Ollama — sem
  custo por requisição e sem dependência de crédito de API externa.
"""

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver

from src.config import OLLAMA_HOST, ModelConfig
from src.prompts import SYSTEM_PROMPT
from src.tools import AGENT_TOOLS


def build_chat_model(model_config: ModelConfig) -> ChatOllama:
    """Cria o cliente de chat para um dado ModelConfig, apontando para o
    servidor Ollama local (precisa estar rodando com "ollama serve" e com
    o modelo já baixado via "ollama pull <tag>" — ver README.md).
    """
    return ChatOllama(
        model=model_config.ollama_tag,
        base_url=OLLAMA_HOST,
        temperature=model_config.temperature,
        top_p=model_config.top_p,
        num_predict=model_config.num_predict,
    )


def build_agent(model_config: ModelConfig):
    """Monta o agente LangChain com as tools do ChargeGrid e um checkpointer
    de memória em RAM (InMemorySaver) — suficiente para demonstrar memória
    por sessão em 3+ turnos (Bloco A da rubrica). Para persistência entre
    execuções do processo, troque por um checkpointer em disco/DB do
    LangGraph (ex.: SqliteSaver), mantendo a mesma interface.
    """
    chat_model = build_chat_model(model_config)
    checkpointer = InMemorySaver()

    return create_agent(
        model=chat_model,
        tools=AGENT_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )


def ask(agent, pergunta: str, session_id: str) -> str:
    """Envia uma pergunta ao agente dentro de uma sessão (thread_id) —
    turnos anteriores da mesma session_id são automaticamente recuperados
    pelo checkpointer, sem precisar reenviar o histórico manualmente.
    """
    resultado = agent.invoke(
        {"messages": [HumanMessage(content=pergunta)]},
        config={"configurable": {"thread_id": session_id}},
    )
    return resultado["messages"][-1].content
