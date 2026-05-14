# Checkpoint v2.0.0 - Multi-Utilizador, Admin e Histórico Persistente

**Data**: 2026-05-12
**Estado**: Estável e Funcional

## Funcionalidades Implementadas desde o v1.0.0:
1.  **Histórico Persistente**: Integração com SQLite (`chat_history.db`).
2.  **Segmentação por Utilizador**: Cada utilizador tem o seu próprio histórico isolado via User ID.
3.  **Painel Administrativo**: Área restrita com login (`admin123`) para gestão do sistema.
4.  **Dashboards de Analítica**: Gráficos interativos (Plotly) mostram métricas de uso e sucesso do RAG.
5.  **Gestão Multi-Dataset**: Possibilidade de ativar/desativar múltiplos CSVs simultaneamente.
6.  **Saudação Dinâmica**: O bot adapta-se automaticamente aos domínios das FAQs ativas.
7.  **Deduplicação de FAQs**: Lógica de merge que remove perguntas repetidas entre ficheiros.

## Estrutura de Ficheiros:
- `app.py`: Interface principal com navegação Chatbot/Admin.
- `admin_page.py`: Componente dedicado ao Painel Administrativo.
- `utils.py`: Motor RAG, Lógica de DB e Analítica.
- `data/`: Folder com datasets CSV ativos e inativos.
- `README.md`: Guia oficial do projeto.

## Próximo Objetivo:
- **Fase 10**: Migração das FAQs para SQLite (CMS) para permitir edição direta via interface.
