# Chatbot de Atendimento ao Segurado InsurCode (RAG & Human-in-the-Loop)

Este é um assistente virtual inteligente de nova geração para a **InsurCode Seguros**. Além do motor RAG (Retrieval-Augmented Generation) para respostas automáticas, o sistema integra agora uma arquitetura robusta de **Escalação para Revisão Humana**, um **Módulo de Gestão de Segurados** e uma interface premium de alta performance.

## 🌟 Funcionalidades Principais (v2.2)

### 🤖 Interface do Segurado (Experiência Inteligente)
- **Identificação por ID ou Nome**: Fluxo conversacional inteligente. Se o utilizador inserir um ID (ex: 101), o sistema resolve automaticamente o nome do segurado e carrega o histórico correspondente.
- **Recuperação Inteligente de Histórico**: O bot deteta conversas anteriores e permite a continuidade fluida do atendimento.
- **Follow-up de Pendentes**: Identificação proativa de dúvidas não resolvidas na última sessão.
- **Escalação Proativa e Híbrida**:
    - **Flags de Dataset**: Marcadores para intervenção humana em temas sensíveis.
    - **Análise de In-Scope**: IA deteta se a dúvida é sobre seguros e encaminha para técnicos se não houver resposta na base.
- **Serviços Rápidos (Sidebar)**: Atalhos para "Participar Sinistro", "2ª Via de Apólice", etc., visíveis apenas para utilizadores identificados.
- **Layout Adaptativo**: Interface expansível para maior conforto visual.

### 🛡️ Painel Administrativo (Gestão Centralizada)
- **👤 Gestão de Segurados (Novo)**:
    - Interface CRUD completa para gerir a base de clientes (ID, Nome, Email, Contacto).
    - Pesquisa rápida e filtros para administração ágil.
- **📝 CMS de FAQs**: Gestão dinâmica de datasets e ativação/desativação de ficheiros em tempo real.
- **📜 Auditoria e Segurança**:
    - **Login Persistente**: Autenticação mantida durante a navegação entre tabs.
    - **Logout Seguro**: Botão "Sair do Painel" com redirecionamento programático e limpeza de estado.
    - **Audit Log**: Registo detalhado de todas as ações administrativas.
- **🔧 Revisão Humana (Tickets)**: Sistema de tickets com filtros por data, utilizador e categoria para escalação técnica.
- **📊 Analítica Visual**: Dashboards responsivos (Plotly) para monitorização de sentimento, performance da IA e volume de tráfego.

## 🏗️ Arquitetura Técnica Avançada

O sistema opera como uma máquina de estados robusta:
1.  **Camada de Identificação**: Resolução de ID -> Nome e orquestração de histórico persistente.
2.  **Motor RAG Semântico**: Recuperação TF-IDF otimizada integrada com **Gemini 2.0 Flash**.
3.  **Pipeline de Confiança**: Avaliação multicritério (RAG Score + NLP Intent) para decidir entre IA ou Humano.
4.  **UX Responsiva (Wide Mode)**: Interface configurada em modo expandido para maximizar a densidade de informação em ecrãs empresariais.

## 🛠️ Tecnologias Utilizadas

- **Frontend**: [Streamlit](https://streamlit.io/) (Layout Wide & Responsive Parameters)
- **Motor de IA**: [OpenRouter](https://openrouter.ai/) (Google Gemini 2.0 Flash 001)
- **Processamento de Dados**: Scikit-Learn (TF-IDF), Pandas, NumPy
- **Persistência**: SQLite3 (Schema dinâmico com suporte a Segurados e Tickets)
- **Estilo**: CSS Vanilla para micro-animações e badges de estado (ex: Shield de Segurado 🛡️)

## ⚙️ Configuração e Instalação

### Pré-requisitos
- Python 3.9+
- `.env` com `OPENROUTER_API_KEY`

### Instalação
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate no Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar aplicação
streamlit run app.py
```

## 📈 Roadmap (2024-2025)

### ✅ Concluído
- [x] Módulo de **Gestão de Segurados** (CRUD e Identificação por ID).
- [x] **Layout Wide** e interface profissional adaptativa.
- [x] Sistema de **Logout e Autenticação Persistente** no Admin.
- [x] Escalação Iterativa e Painel de Tickets avançado.
- [x] Integração total com OpenRouter/Gemini.

### 🚀 Próximos Desafios
- **Análise Multimodal**: Processamento de imagens de sinistros via IA vision.
- **Geolocalização**: Assistência rodoviária em tempo real baseada no GPS do segurado.
- **Conectividade Core**: Integração via API com sistemas de apólices externos.

---
*Documentação oficial da plataforma InsurCode v2.2. Desenvolvido por Antigravity.*
