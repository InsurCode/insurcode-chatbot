import streamlit as st


import random


from utils import load_faq_data, build_retriever, find_best_faq_rag, get_ai_response, init_db, save_message, get_chat_history, delete_chat_history, log_analytics, load_active_datasets, analyze_sentiment, verify_admin, check_unresolved_issues, register_ticket, is_insurance_related, get_tickets, update_ticket_status, find_segurado_by_id


from admin_page import admin_panel


import os


import time





# Configuração da Página


st.set_page_config(
    page_title="InsurCode Seguros - Assistente Virtual",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GLOBAL: Logout Handler ---
if st.session_state.get('logout_triggered'):
    st.session_state.navigation = "Chatbot"
    st.session_state.admin_authenticated = False
    st.session_state.logout_triggered = False
    st.rerun()






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


    


    
    app_mode = st.radio("Navegação", ["Chatbot", "Painel Admin"], key="navigation")

    # Inicializar estado de autenticação admin
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if app_mode == "Chatbot":
        st.info("Utilize o chat para se identificar.")
    else:
        if not st.session_state.admin_authenticated:
            st.header("Acesso WebAdmin")
            admin_user = st.text_input("Username", value="admin")
            admin_pass = st.text_input("Senha Admin", type="password")
            
            if st.button("Entrar", width='stretch'):
                admin_role = verify_admin(admin_user, admin_pass)
                if admin_role:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_user = admin_user
                    st.session_state.admin_role = admin_role
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
                    st.stop()
        else:
            st.success(f"Logado como: {st.session_state.admin_user} ({st.session_state.get('admin_role', '')})")

    st.divider()





if app_mode == "Painel Admin":
    if st.session_state.get('admin_authenticated'):
        admin_panel(st.session_state.admin_user)
    st.stop()





# --- ABAIXO: Lógica do Chatbot ---


st.title("🤖 Assistente Virtual InsurCode")





# Inicialização do estado de autenticação


if "auth_step" not in st.session_state:


    st.session_state.auth_step = "waiting_for_name"


    st.session_state.messages = []


    st.session_state.current_user = None





# Sidebar dinà¢mica


with st.sidebar:


    if st.session_state.auth_step == "authenticated":


        st.success(f"Sessão ativa: **{st.session_state.current_user}**")


        if st.button("Sair / Mudar Usuário"):


            st.session_state.auth_step = "waiting_for_name"


            st.session_state.current_user = None


            st.session_state.messages = []


            st.rerun()


        


        if st.button("Limpar o meu Histórico"):


            delete_chat_history(st.session_state.current_user)


            st.session_state.messages = []


            st.rerun()





# Fluxo de Identificação no Chat


if st.session_state.auth_step == "waiting_for_name":


    # Mensagem inicial do bot


    if not st.session_state.messages:


        initial_msg = "Olá! Bem-vindo à  InsurCode. Para começarmos, por favor, diga-me o seu **nome** ou **ID de segurado**."


        st.session_state.messages.append({"role": "assistant", "content": initial_msg})


    


    for message in st.session_state.messages:


        with st.chat_message(message["role"]):


            st.markdown(message["content"])


            


    if prompt := st.chat_input("Insira o seu nome aqui..."):


        st.session_state.messages.append({"role": "user", "content": prompt})


        # Procura por ID ou Nome de Segurado
        segurado = find_segurado_by_id(prompt)
        
        if segurado:
            st.session_state.current_user = segurado['nome']
            st.session_state.is_insured = True
            welcome_name = segurado['nome']
        else:
            st.session_state.current_user = prompt
            st.session_state.is_insured = False
            welcome_name = prompt

        # Verificar se existe histórico (usando o nome identificado)
        history = get_chat_history(st.session_state.current_user)

        if history:
            st.session_state.auth_step = "history_decision"
            msg = f"Olá **{welcome_name}**! Notei que já temos um histórico de conversas anterior. Deseja recuperar a conversa anterior ou começar um novo chat?"
            st.session_state.messages.append({"role": "assistant", "content": msg})
        else:
            st.session_state.auth_step = "authenticated"
            msg = f"Muito prazer, **{welcome_name}**! Como posso ajudar com os seus seguros hoje?"
            st.session_state.messages.append({"role": "assistant", "content": msg})
            save_message(st.session_state.current_user, "assistant", msg)
        st.rerun()





elif st.session_state.auth_step == "history_decision":


    for message in st.session_state.messages:


        with st.chat_message(message["role"]):


            st.markdown(message["content"])


            


    col1, col2 = st.columns(2)


    with col1:


        if st.button("Recuperar Histórico", width='stretch'):


            history = get_chat_history(st.session_state.current_user)


            st.session_state.messages = history


            


            # Verificar se há algo pendente


            unresolved_query = check_unresolved_issues(st.session_state.current_user)


            if unresolved_query:


                st.session_state.pending_query = unresolved_query


                st.session_state.auth_step = "follow_up"


                st.session_state.messages.append({"role": "assistant", "content": f"Histórico recuperado. Antes de continuarmos, notei que na última vez tivemos uma dúvida sobre: '*{unresolved_query}*'. Isso ficou devidamente resolvido?"})


            else:


                st.session_state.messages.append({"role": "assistant", "content": f"Histórico recuperado com sucesso. Como posso continuar a ajudar, **{st.session_state.current_user}**?"})


                st.session_state.auth_step = "authenticated"


            st.rerun()


    with col2:


        if st.button("Começar Novo Chat", width='stretch'):


            st.session_state.messages = [{"role": "assistant", "content": f"Certo, **{st.session_state.current_user}**! Vamos começar do zero. O que precisa hoje?"}]


            st.session_state.auth_step = "authenticated"


            st.rerun()





elif st.session_state.auth_step == "follow_up":


    for message in st.session_state.messages:


        with st.chat_message(message["role"]):


            st.markdown(message["content"])


            


    col1, col2 = st.columns(2)


    with col1:


        if st.button("Sim, resolvido", width='stretch'):


            st.session_state.messages.append({"role": "assistant", "content": "Fico contente por saber! Como posso ajudar-lhe hoje?"})


            st.session_state.auth_step = "authenticated"


            st.rerun()


    with col2:


        if st.button("Não, ainda preciso de ajuda", width='stretch'):


            st.session_state.messages.append({"role": "assistant", "content": "Lamento que ainda não esteja resolvido. Pode dar-me mais alguns detalhes sobre o problema? Vou registar para que um técnico de seguros o contacte diretamente."})


            st.session_state.auth_step = "collect_details"


            st.rerun()





elif st.session_state.auth_step == "collect_details":


    # Mostrar um aviso amarelo persistente no topo da recolha de detalhes


    st.warning(f"📝 **A registar revisão para:** \"{st.session_state.get('pending_query', 'consulta')}\"")


    


    for message in st.session_state.messages:


        with st.chat_message(message["role"]):


            st.markdown(message["content"])


            


    # Mostrar resumo do que já foi recolhido se houver


    if st.session_state.get('temp_details'):


        with st.chat_message("assistant"):


            st.info("**Detalhes acumulados:**\n\n" + "\n".join([f"- {d}" for d in st.session_state.temp_details]))


            col1, col2 = st.columns(2)


            with col1:


                if st.button("Submeter para Revisão", width='stretch'):


                    final_details = " | ".join(st.session_state.temp_details)


                    ticket_id = register_ticket(


                        st.session_state.current_user, 


                        st.session_state.get('pending_query', 'N/A'), 


                        final_details,


                        categoria=st.session_state.get('pending_category', 'Geral')


                    )


                    # Simular um ID de ticket para o utilizador


                    disp_id = f"TIC-{random.randint(1000, 9999)}"


                    


                    msg = f"✅ **Submetido com sucesso!** O seu número de pedido é **{disp_id}**. Um técnico entrará em contacto brevemente."


                    st.session_state.messages.append({"role": "assistant", "content": msg})


                    save_message(st.session_state.current_user, "assistant", msg)


                    st.session_state.auth_step = "authenticated"


                    del st.session_state.temp_details


                    st.rerun()


            with col2:


                st.write("Ou continue a escrever abaixo para acrescentar mais...")





    if user_input := st.chat_input("Adicione mais detalhes..."):


        st.session_state.messages.append({"role": "user", "content": user_input})


        if 'temp_details' not in st.session_state:


            st.session_state.temp_details = []


        st.session_state.temp_details.append(user_input)


        st.rerun()





elif st.session_state.auth_step == "authenticated":


    user_id = st.session_state.current_user


    


    # Exibir histórico de mensagens


    for message in st.session_state.messages:


        with st.chat_message(message["role"]):


            st.markdown(message["content"])





    # Input do utilizador (via trigger ou input direto)
    prompt = None
    if st.session_state.get('sidebar_trigger'):
        prompt = st.session_state.sidebar_trigger
        st.session_state.sidebar_trigger = None # Limpa trigger
    else:
        prompt = st.chat_input("Ex: 'O que fazer em caso de acidente?'")

    if prompt:


        # Adicionar mensagem do utilizador


        save_message(user_id, "user", prompt)


        st.session_state.messages.append({"role": "user", "content": prompt})


        with st.chat_message("user"):


            st.markdown(prompt)





        # Processamento


        with st.chat_message("assistant"):


            with st.spinner("A consultar base de conhecimento..."):


                # Carregar FAQS se não estiverem em cache


                if "faq_df" not in st.session_state:


                    df = load_active_datasets()


                    st.session_state.faq_df = df


                    st.session_state.vectorizer, st.session_state.tfidf_matrix = build_retriever(df)


                


                # 1. Recuperação (RAG Retrieval)


                faq_match = find_best_faq_rag(


                    prompt, 


                    st.session_state.faq_df, 


                    st.session_state.vectorizer, 


                    st.session_state.tfidf_matrix


                )


                


                # 2. Obter resposta da IA (Contextualizada com FAQ se encontrada)


                start_time = time.time()


                response = get_ai_response(prompt, faq_match, user_name=user_id)


                end_time = time.time()


                resp_duration = end_time - start_time


                


                # 3. Analisar Sentimento


                user_sentiment = analyze_sentiment(prompt)


                


                # 4. Log Analytics


                log_analytics(user_id, prompt, faq_match, response_time=resp_duration, sentiment=user_sentiment)


                


                st.markdown(response)


                


                # 5. Lógica de Escalabilidade Automática


                escalated = False


                revision_flag = str(faq_match.get('requer_revisao_humana', 'Não')).strip().lower() if faq_match else 'não'


                


                if (faq_match and revision_flag == 'sim') or (not faq_match and is_insurance_related(prompt)):


                    escalated = True


                    st.session_state.pending_query = prompt


                    st.session_state.pending_category = faq_match.get('categoria', 'Geral') if faq_match else "Geral"


                    


                    # Espaço reservado para o aviso amarelo


                    placeholder = st.empty()


                    with placeholder.container():


                        if faq_match:


                            st.warning(f"⚠️ **Nota:** Este assunto requer validação humana ({faq_match.get('motivo_revisao')}).")


                        else:


                            st.info("💡 Notei que a sua dúvida é sobre seguros, mas requer uma análise mais detalhada de um técnico.")


                        


                        if st.button("Fornecer mais detalhes para o técnico", width='stretch'):


                            st.session_state.auth_step = "collect_details"


                            st.session_state.temp_details = [] # Inicializa lista de detalhes


                            st.session_state.messages.append({"role": "assistant", "content": "Certo! Estou a aguardar os detalhes do seu problema. Pode escrever abaixo."})


                            placeholder.empty() # Limpa o aviso


                            st.rerun()





                # Adicionar feedback visual se foi baseado numa FAQ


                if faq_match:


                    with st.expander("Ver fonte oficial (FAQ)"):


                        st.info(f"**Categoria:** {faq_match['categoria']}\n\n**Resposta oficial:** {faq_match['resposta']}")





        # Adicionar mensagem do assistente ao histórico


        save_message(user_id, "assistant", response)


        st.session_state.messages.append({"role": "assistant", "content": response})


        if escalated:


            # Se escalou mas o utilizador ainda não clicou, o estado mantém-se autenticado


            # mas o aviso visual está lá. Se o utilizador escrever outra coisa, o aviso some


            pass





# Sidebar com serviços adicionais
with st.sidebar:
    if st.session_state.get('auth_step') == "authenticated":
        if st.session_state.get('is_insured'):
            st.success(f"🛡️ Segurado: {st.session_state.current_user}")
        st.header("Serviços Rápidos")
        if st.button("Participar Sinistro", width='stretch'):
            st.session_state.sidebar_trigger = "Gostaria de participar um Sinistro"
            st.rerun()
        if st.button("Segunda via de Apólice", width='stretch'):
            st.session_state.sidebar_trigger = "Gostaria de pedir a segunda via da minha Apólice"
            st.rerun()
        if st.button("Assistência 24h", width='stretch'):
            st.session_state.sidebar_trigger = "Preciso de assistência 24h"
            st.rerun()
        st.divider()

    st.caption("Desenvolvido por Antigravity para InsurCode Seguros.")


