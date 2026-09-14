"""
Núcleo do agente ChargeGrid Assistant — Sprint 03.

Ganho do refactory em relação à Sprint 1/2:
- Sprint 1/2: system prompt injetado manualmente a cada chamada + histórico
  de mensagens gerenciado "na mão" em uma lista Python.
- Sprint 03: create_agent (LangChain/LangGraph) decide quando chamar cada
  tool, e a memória por sessão é gerenciada nativamente por um checkpointer,
  associada a um thread_id — sem código condicional extra para manter o
  histórico.
"""

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.checkpoint.memory import InMemorySaver

from src.config import HF_TOKEN, ModelConfig
from src.prompts import SYSTEM_PROMPT
from src.tools import AGENT_TOOLS


def build_chat_model(model_config: ModelConfig) -> ChatHuggingFace:
    """Cria o cliente de chat para um dado ModelConfig, via Hugging Face
    Inference API (sem download local de pesos — mesma decisão arquitetural
    da Sprint 1/2, agora parametrizada para permitir a troca de modelo).
    """
    endpoint = HuggingFaceEndpoint(
        repo_id=model_config.repo_id,
        huggingfacehub_api_token=HF_TOKEN,
        temperature=model_config.temperature,
        top_p=model_config.top_p,
        max_new_tokens=model_config.max_new_tokens,
    )
    return ChatHuggingFace(llm=endpoint)


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
