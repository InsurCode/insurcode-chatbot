import streamlit as st
from utils import load_faq_data, build_retriever, find_best_faq_rag, get_ai_response, init_db, save_message, get_chat_history, delete_chat_history, log_analytics, load_active_datasets, analyze_sentiment, verify_admin
from admin_page import admin_panel
import os
import time

# Configuração da Página
st.set_page_config(
    page_title="InsurCode Seguros - Assistente Virtual",
    page_icon="🚗",
    layout="centered"
)

# Estilo Customizado (Premium)
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #007bff;
        color: white;
    }
    .bot-message {
        background-color: white;
        border: 1px solid #dee2e6;
    }
    h1 {
        color: #1e3a8a;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização da base de dados
init_db()

# Navegação na Barra Lateral
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3064/3064155.png", width=100)
    
    app_mode = st.radio("Navegação", ["Chatbot", "Painel Admin"])
    
    if app_mode == "Chatbot":
        st.header("Identificação")
        user_id = st.text_input("ID ou Nome do Segurado", value="segurado_01", placeholder="Ex: joao_silva")
        
        if st.button("Limpar o meu Histórico"):
            delete_chat_history(user_id)
            st.session_state.messages = []
            st.rerun()
    else:
        st.header("Acesso WebAdmin")
        admin_user = st.text_input("Username", value="admin")
        admin_pass = st.text_input("Senha Admin", type="password")
        
        admin_role = verify_admin(admin_user, admin_pass)
        
        if not admin_role:
            st.warning("Credenciais inválidas.")
            st.stop()
        else:
            st.success(f"Logado como: {admin_user} ({admin_role})")
    
    st.divider()

if app_mode == "Painel Admin":
    admin_panel(admin_user)
    st.stop()

# --- ABAIXO: Lógica do Chatbot ---
st.title("🤖 Assistente Virtual InsurCode")

# Determina saudação dinâmica
active_categories = st.session_state.faq_df['categoria'].unique() if "faq_df" in st.session_state else []
dominios_str = " e ".join([c.lower() for c in active_categories]) if len(active_categories) > 0 else "seguros"

st.markdown(f"Olá! Sou o seu assistente especializado em **{dominios_str}**. Como posso ajudar hoje?")

# No multi-user, o default dataset já é gerido pelo admin globalmente ou na sessão

# Resetar estado se o utilizador mudar
if "current_user" not in st.session_state or st.session_state.current_user != user_id:
    st.session_state.current_user = user_id
    st.session_state.messages = get_chat_history(user_id)

if "faq_df" not in st.session_state:
    try:
        df = load_active_datasets()
        st.session_state.faq_df = df
        st.session_state.vectorizer, st.session_state.tfidf_matrix = build_retriever(df)
    except Exception as e:
        st.error(f"Erro ao carregar base de dados ativa: {e}")
        st.stop()

# Exibir histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do utilizador
if prompt := st.chat_input("Ex: 'O que fazer em caso de acidente?'"):
    # Adicionar mensagem do utilizador
    save_message(user_id, "user", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Processamento
    with st.chat_message("assistant"):
        with st.spinner("A consultar base de conhecimento..."):
            # 1. Recuperação (RAG Retrieval)
            faq_match = find_best_faq_rag(
                prompt, 
                st.session_state.faq_df, 
                st.session_state.vectorizer, 
                st.session_state.tfidf_matrix
            )
            
            # 2. Obter resposta da IA (Contextualizada com FAQ se encontrada)
            start_time = time.time()
            response = get_ai_response(prompt, faq_match)
            end_time = time.time()
            resp_duration = end_time - start_time
            
            # 3. Analisar Sentimento
            user_sentiment = analyze_sentiment(prompt)
            
            # 4. Log Analytics
            log_analytics(user_id, prompt, faq_match, response_time=resp_duration, sentiment=user_sentiment)
            
            st.markdown(response)
            
            # Adicionar feedback visual se foi baseado numa FAQ
            if faq_match:
                with st.expander("Ver fonte oficial (FAQ)"):
                    st.info(f"**Categoria:** {faq_match['categoria']}\n\n**Resposta oficial:** {faq_match['resposta']}")

    # Adicionar mensagem do assistente ao histórico
    save_message(user_id, "assistant", response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar com serviços adicionais
with st.sidebar:
    st.header("Serviços Rápidos")
    st.button("Participar Sinistro")
    st.button("Segunda via de Apólice")
    st.button("Assistência 24h")
    
    st.divider()
    st.caption("Desenvolvido por Antigravity para InsurCode Seguros.")
