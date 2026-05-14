# Checkpoint Inicial - v1.0.0

Este documento marca o estado inicial estável do Chatbot de Seguros Auto.

## Estado do Projeto
- **Chatbot**: Funcional (app.py)
- **RAG**: Implementado com TF-IDF (utils.py)
- **Interface**: Streamlit com design premium
- **Dataset**: FAQs seguradora (200 linhas)
- **Dependências**: requirements.txt criado

## Arquitetura
O sistema utiliza um fluxo de Recuperação-Aumentação-Geração (RAG) onde:
1. O texto do utilizador é vetorizado via TF-IDF.
2. A FAQ mais similar é recuperada do dataset.
3. O Gemini 2.0 Flash (OpenRouter) gera a resposta final baseada no contexto.

## Data e Hora
2026-05-12T21:32:00
