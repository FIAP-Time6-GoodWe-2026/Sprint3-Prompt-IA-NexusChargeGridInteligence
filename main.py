"""
Ponto de entrada do ChargeGrid Assistant — Sprint 03.

Uso:
    python main.py

Digite "sair" para encerrar. Todas as mensagens da mesma execução
compartilham a sessão "cli-session" (memória mantida pelo checkpointer).
"""

from src.agent import ask, build_agent
from src.config import MODEL_PRIMARY


def main() -> None:
    print(f"ChargeGrid Assistant (Sprint 03) — modelo: {MODEL_PRIMARY.label}")
    print("Digite 'sair' para encerrar.\n")

    agent = build_agent(MODEL_PRIMARY)
    session_id = "cli-session"

    while True:
        pergunta = input("Você: ").strip()
        if pergunta.lower() in {"sair", "exit", "quit"}:
            print("Até mais!")
            break
        if not pergunta:
            continue

        resposta = ask(agent, pergunta, session_id)
        print(f"\nChargeGrid Assistant: {resposta}\n")


if __name__ == "__main__":
    main()
