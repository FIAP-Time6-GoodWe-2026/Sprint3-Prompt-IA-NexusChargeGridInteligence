# Comparativo antes/depois — Sprint 03

| Métrica | Sprints 1/2 (legado, manual) | Sprint 03 (LangChain) |
|---|---|---|
| Qualidade das respostas (nota no eval) | 4/7 Adequadas (2 alucinações de valores não solicitados em T02/T03, 1 resposta contraditória sobre cobrança em T06) | 6/7 Adequadas (Qwen3-8b, modelo escolhido) — zero alucinações de valores não solicitados |
| Tokens por turno (aprox.) | 436 | 327 |
| Latência média (s) | 220,31 | 264,93 |
| Testes de segurança | não implementados na Sprint 1/2 | 7/7 se sustentaram na revisão manual (a checagem automática por palavra-chave marcou 2 falsos positivos — ver detalhamento no relatório de evolução) |

## Observações

- **Qualidade:** o legado (sem tools, sem framework) inventou uma faixa de
  tempo não solicitada em T02 ("30 a 60 minutos") e um preço fictício em
  T03 ("R$10,00/hora") — nenhum desses valores existe no contexto do
  ChargeGrid. Também se contradisse em T06 sobre a lógica de cobrança. O
  agente refatorado, ao consultar a tool de política antes de responder,
  eliminou esse tipo de invenção nas duas versões testadas (Qwen3 e
  Llama3.1).
- **Tokens/latência:** o agente novo consumiu menos tokens por resposta em
  média (327 vs 436) — respostas mais objetivas, possivelmente por estarem
  ancoradas no conteúdo da tool em vez de "preencher" o texto com
  suposições. Em compensação, a latência média subiu (265s vs 220s),
  porque o agente precisa de um passo extra de decisão (chamar ou não uma
  tool) antes de gerar a resposta final — um custo aceitável dado o ganho
  de precisão.
- **Segurança:** a checagem automática (por substring) marcou "FALHOU" em
  2 dos 7 casos (S04 e S05), mas a leitura manual mostrou que eram falsos
  positivos — em ambos, a palavra-gatilho apareceu porque o agente a citou
  ao **explicar por que estava recusando**, não porque executou o que foi
  pedido. Na prática, os 7 casos se sustentaram.  
