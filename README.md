# Chatbot de Atendimento ao Segurado InsurCode (RAG)

Este é um assistente virtual inteligente baseado em IA para automatizar o atendimento de segurados da **InsurCode Seguros**. Utiliza uma arquitetura RAG (Retrieval-Augmented Generation) para garantir respostas precisas baseadas em bases de conhecimento oficiais, combinando curadoria humana com a potência de modelos de linguagem de larga escala.

## 🌟 Funcionalidades Principais

### Interface do Segurado
- **Motor RAG Híbrido**: Combina busca semântica eficiente (TF-IDF) com o raciocínio avançado do modelo **Gemini 2.0 Flash**.
- **Contextualização Dinâmica**: O bot ajusta a sua personalidade e saudação com base nos datasets ativos (Auto, Saúde, Casa, etc.).
- **Histórico Persistente**: Conversas guardadas em SQLite, permitindo que o utilizador retome o diálogo onde parou.
- **Análise de Sentimento**: Monitorização em tempo real do estado emocional do utilizador para respostas mais empáticas.

### Painel Administrativo (WebAdmin)
- **Dashboards de Analítica**: Visualização de métricas de utilização, taxa de sucesso RAG, tempo médio de resposta e distribuição de sentimentos através de gráficos interativos (Plotly).
- **Gestão de Conhecimento (CMS)**: 
    - Interface para adicionar, editar ou remover FAQs manualmente.
    - Upload de novos datasets em CSV.
    - Ativação/desativação dinâmica de fontes de dados sem necessidade de reiniciar o sistema.
- **Curadoria de IA**: Identificação automática de perguntas que o bot não soube responder, permitindo a criação imediata de novas soluções oficiais.
- **Auditoria & Segurança**: Registo completo de todas as ações administrativas e proteção de acesso via SHA256.

## 🏗️ Arquitetura Técnica

O sistema funciona num fluxo de 4 passos principais:
1.  **Recuperação (Retrieval)**: Quando o utilizador faz uma pergunta, o motor TF-IDF procura a FAQ mais relevante nos datasets ativos.
2.  **Aumentação (Augmentation)**: Se uma FAQ é encontrada, ela é injetada como contexto no prompt da IA.
3.  **Geração (Generation)**: O modelo **Gemini 2.0 Flash** (via OpenRouter) gera uma resposta conversacional e empática baseada na informação oficial.
4.  **Monitorização**: O sistema regista a performance, o sentimento e o tempo de execução para melhoria contínua.

## 🛠️ Tecnologias Utilizadas

- **Interface**: [Streamlit](https://streamlit.io/)
- **IA/LLM**: [OpenRouter](https://openrouter.ai/) (Google Gemini 2.0 Flash 001)
- **Processamento de Dados**: Pandas, Scikit-Learn
- **Base de Dados**: SQLite3 (Persistência, Analítica e Auditoria)
- **Visualização**: Plotly Express
- **Segurança**: Hashlib (SHA256) e Dotenv para gestão de segredos.

## ⚙️ Configuração e Instalação

### Pré-requisitos
- Python 3.8 ou superior.
- Chave de API da [OpenRouter](https://openrouter.ai/).

### Passos
1. **Clonar e Instalar**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configurar Variáveis**:
   Crie um ficheiro `.env` na raiz com:
   ```env
   OPENROUTER_API_KEY=sua_chave_aqui
   OPENROUTER_MODEL=google/gemini-2.0-flash-001
   ```
3. **Iniciar**:
   ```bash
   streamlit run app.py
   ```

## 🛡️ Acesso Administrativo
O acesso ao painel admin é feito através da barra lateral.
- **Utilizador**: `admin`
- **Senha Padrão**: `admin123` *(Pode ser alterada via código ou DB)*.

## 📈 Estado do Projeto e Roadmap

### ✅ Fases Concluídas
- [x] **Fase 1-3**: Setup, Motor RAG Base e Interface de Chat.
- [x] **Fase 4-5**: Persistência de Histórico e Gestão Multi-utilizador.
- [x] **Fase 6-7**: Painel Admin, Dashboards e CMS de FAQs.
- [x] **Fase 8**: Curadoria de Falhas de IA e Auditoria de Segurança.

### 🚀 Próximos Passos (Roadmap 2024-2025)
- **Inteligência**: Migração para Vector DB (ChromaDB) para busca semântica profunda.
- **UX**: Integração de Voz (STT/TTS) e Leitura de PDFs de apólices individuais.
- **Automação**: Conectores com APIs de sistemas core para consulta de sinistros em tempo real.
- **Segurança**: Mascaramento automático de dados de PII (RGPD Compliance).

---
*Desenvolvido por Antigravity para a Equipa de Inovação InsurCode.*
