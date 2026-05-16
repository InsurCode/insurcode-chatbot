import streamlit as st


import pandas as pd


import plotly.express as px


from utils import (get_analytics_data, load_faq_data, get_datasets_config, 
                   update_dataset_status, load_active_datasets, build_retriever,
                   get_all_faqs, update_faq, delete_faq, add_custom_faq, get_missed_questions,
                   log_audit, get_audit_logs, get_tickets, update_ticket_status,
                   get_segurados, add_segurado, update_segurado, delete_segurado, find_segurado_by_id)


import os





def admin_panel(current_admin):
    # Sidebar de Navegação do Admin
    with st.sidebar:
        st.header(f"🔐 Admin: {current_admin}")
        if st.button("🚪 Sair do Painel", width='stretch'):
            st.session_state.logout_triggered = True
            st.rerun()
        st.divider()

    st.title("🛡️ Painel de Administração")


    


    # Tab de Dashboards, Gestão, CMS e Auditoria


    tabs = st.tabs(["📊 Analítica", "📂 Gestão de Dados", "👤 Segurados", "📝 CMS (Editor)", "🧠 Curadoria de IA", "📜 Auditoria", "🔧 Revisão Humana"])


    tab_dash, tab_data, tab_insured, tab_cms, tab_ia, tab_audit, tab_tickets = tabs


    


    df_analytics, df_messages = get_analytics_data()


    


    with tab_dash:


        st.header("Métricas de Utilização")


        


        if df_analytics.empty:


            st.info("Ainda não existem dados de analítica para exibir.")


        else:


            col1, col2, col3, col4 = st.columns(4)


            col1.metric("Total de Perguntas", len(df_analytics))


            col2.metric("Utilizadores Únicos", df_analytics['user_id'].nunique())


            col3.metric("Taxa de Sucesso RAG", f"{(df_analytics['faq_score'] > 0).mean()*100:.1f}%")


            


            avg_time = df_analytics['response_time'].mean()


            col4.metric("Tempo Médio Resp.", f"{avg_time:.2f}s" if pd.notnull(avg_time) else "N/A")


            


            st.divider()


            


            col_sent, col_perf = st.columns(2)


            


            with col_sent:


                st.subheader("Análise de Sentimento")


                if 'sentiment' in df_analytics.columns:


                    sent_counts = df_analytics['sentiment'].value_counts().reset_index()


                    sent_counts.columns = ['sentimento', 'count']


                    fig_sent = px.pie(sent_counts, values='count', names='sentimento', 


                                    color='sentimento',


                                    color_discrete_map={'Positivo':'#2ecc71', 'Neutro':'#95a5a6', 'Negativo':'#e67e22', 'Irritado':'#e74c3c'},


                                    title="Distribuição de Satisfação")


                    st.plotly_chart(fig_sent, width='stretch')


            


            with col_perf:


                st.subheader("Performance da IA")


                if 'response_time' in df_analytics.columns:


                    fig_perf = px.line(df_analytics, x='timestamp', y='response_time', title="Tempo de Resposta ao Longo do Tempo")


                    st.plotly_chart(fig_perf, width='stretch')





            st.divider()


            


            st.subheader("Atividade por Utilizador")


            user_counts = df_analytics['user_id'].value_counts().reset_index()


            user_counts.columns = ['user_id', 'count']


            fig_users = px.bar(user_counts, x='user_id', y='count', title="Atividade por Utilizador")


            st.plotly_chart(fig_users)


            


            st.subheader("FAQs Mais Consultadas")


            faq_counts = df_analytics[df_analytics['faq_pergunta'] != "Nenhuma correspondência"]['faq_pergunta'].value_counts().head(10).reset_index()


            faq_counts.columns = ['pergunta', 'count']


            fig_faqs = px.pie(faq_counts, values='count', names='pergunta', title="Top 10 FAQs Mais Consultadas")


            st.plotly_chart(fig_faqs)


            


            st.subheader("Volume de Conhecimento por Categoria")


            active_df = load_active_datasets()


            if not active_df.empty:


                cat_counts = active_df['categoria'].value_counts().reset_index()


                cat_counts.columns = ['categoria', 'count']


                fig_cats = px.bar(cat_counts, x='categoria', y='count', color='categoria', title="Total de FAQs Ativas por Domínio")


                st.plotly_chart(fig_cats)





            st.divider()


            st.subheader("Exportação de Dados")


            csv = df_analytics.to_csv(index=False).encode('utf-8')


            st.download_button(


                label="Descarregar Relatório de Analítica (CSV)",


                data=csv,


                file_name='relatorio_analitica_i2a2.csv',


                mime='text/csv',


            )





    with tab_data:


        st.header("Gestão de Datasets")


        


        # Upload de novo ficheiro


        uploaded_file = st.file_uploader("Carregar novo dataset FAQ (CSV)", type="csv")


        if uploaded_file is not None:


            save_path = os.path.join("data", uploaded_file.name)


            with open(save_path, "wb") as f:


                f.write(uploaded_file.getbuffer())


            st.success(f"Ficheiro {uploaded_file.name} guardado na pasta /data!")


        


        st.divider()


        


        # Seleção de datasets ativos


        st.subheader("Configuração de Conhecimento Ativo")


        datasets_df = get_datasets_config()


        


        changes_detected = False


        new_statuses = {}


        


        for _, row in datasets_df.iterrows():


            filename = row['filename']


            is_active = bool(row['is_active'])


            new_val = st.toggle(f"Ativar: {filename}", value=is_active, key=f"toggle_{filename}")


            if new_val != is_active:


                new_statuses[filename] = new_val


                changes_detected = True


        


        if st.button("Gravar Alterações e Reconstruir RAG"):


            for fname, status in new_statuses.items():


                update_dataset_status(fname, status)


                log_audit(current_admin, f"Alterou estado do dataset: {fname} para {status}")


            


            # Recarregar e Reconstruir


            combined_df = load_active_datasets()


            if not combined_df.empty:


                st.session_state.faq_df = combined_df


                st.session_state.vectorizer, st.session_state.tfidf_matrix = build_retriever(combined_df)


                st.success("Configuração guardada! O chatbot agora usa o conhecimento combinado dos datasets ativos.")


            else:


                st.error("Pelo menos um dataset deve estar ativo.")


        


        st.divider()


        st.subheader("Pré-visualização da Base Consolidada")


        active_df = load_active_datasets()


        st.write(f"Total de registos ativos: {len(active_df)}")


        st.dataframe(active_df.head(10))






    with tab_insured:
        st.header("👤 Gestão de Segurados")
        st.markdown("Gerencie os dados dos segurados que podem aceder ao chat com identificação prioritária.")
        
        # 1. Formulário para Adicionar
        with st.expander("➕ Registar Novo Segurado"):
            with st.form("add_segurado_form"):
                col_id, col_nome = st.columns(2)
                s_id = col_id.text_input("ID do Segurado (Único)")
                s_nome = col_nome.text_input("Nome Completo")
                
                col_email, col_tel = st.columns(2)
                s_email = col_email.text_input("Email")
                s_tel = col_tel.text_input("Contacto Telefónico")
                
                if st.form_submit_button("Guardar Segurado"):
                    if s_id and s_nome:
                        if add_segurado(s_id, s_nome, s_email, s_tel):
                            log_audit(current_admin, f"Adicionou segurado: {s_nome} (ID: {s_id})")
                            st.success(f"Segurado {s_nome} registado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Erro: O ID indicado já existe.")
                    else:
                        st.warning("Preencha pelo menos o ID e o Nome.")

        st.divider()
        
        # 2. Lista e Edição
        st.subheader("Lista de Segurados")
        df_seg = get_segurados()
        
        if df_seg.empty:
            st.info("Ainda não existem segurados registados.")
        else:
            # Barra de Pesquisa rápida
            search = st.text_input("🔍 Procurar segurado (Nome ou ID):", key="search_seg")
            if search:
                df_seg = df_seg[df_seg['nome'].str.contains(search, case=False) | df_seg['id'].str.contains(search, case=False)]
            
            st.dataframe(df_seg, width='stretch')
            
            # Edição/Remoção
            st.divider()
            st.subheader("Alterar / Remover")
            target_id = st.selectbox("Seleccione ID para gerir:", ["-- Seleccionar --"] + df_seg['id'].tolist(), key="select_target_seg")
            
            if target_id != "-- Seleccionar --":
                seg_da = df_seg[df_seg['id'] == target_id].iloc[0]
                
                with st.form("edit_segurado_form"):
                    e_nome = st.text_input("Nome", value=seg_da['nome'])
                    e_email = st.text_input("Email", value=seg_da['email'])
                    e_tel = st.text_input("Contacto", value=seg_da['contacto'])
                    
                    col_e1, col_e2 = st.columns(2)
                    if col_e1.form_submit_button("Atualizar Dados"):
                        update_segurado(target_id, e_nome, e_email, e_tel)
                        log_audit(current_admin, f"Editou segurado ID {target_id}")
                        st.success("Dados atualizados!")
                        st.rerun()
                        
                    if col_e2.form_submit_button("❌ Remover Segurado"):
                        delete_segurado(target_id)
                        log_audit(current_admin, f"Removeu segurado ID {target_id}")
                        st.warning("Segurado removido!")
                        st.rerun()

    with tab_cms:


        st.header("Gestão de Conteúdo (FAQs)")


        


        # Formulário para nova FAQ


        with st.expander("➕ Adicionar Nova FAQ"):


            with st.form("new_faq_form"):


                new_cat = st.text_input("Categoria")


                new_preg = st.text_input("Pergunta")


                new_resp = st.text_area("Resposta")


                new_tags = st.text_input("Tags (separadas por vírgula)")


                if st.form_submit_button("Guardar FAQ"):


                    add_custom_faq(new_cat, new_preg, new_resp, new_tags)


                    log_audit(current_admin, f"Adicionou nova FAQ: {new_preg[:30]}...")


                    st.success("FAQ adicionada com sucesso!")


                    st.rerun()





        st.divider()


        


        # Lista de FAQs com edição


        st.subheader("Base de Dados de FAQs")


        all_faqs = get_all_faqs()


        


        for idx, row in all_faqs.iterrows():


            with st.expander(f"📌 {row['categoria']}: {row['pergunta'][:50]}..."):


                edit_cat = st.text_input("Categoria", value=row['categoria'], key=f"cat_{row['id']}")


                edit_preg = st.text_input("Pergunta", value=row['pergunta'], key=f"preg_{row['id']}")


                edit_resp = st.text_area("Resposta", value=row['resposta'], key=f"resp_{row['id']}")


                edit_tags = st.text_input("Tags", value=row['tags'], key=f"tags_{row['id']}")


                


                col_save, col_del = st.columns(2)


                if col_save.button("Atualizar", key=f"save_{row['id']}"):


                    update_faq(row['id'], edit_cat, edit_preg, edit_resp, edit_tags)


                    log_audit(current_admin, f"Editou FAQ ID {row['id']}")


                    st.success("Atualizado!")


                    st.rerun()


                if col_del.button("Apagar", key=f"del_{row['id']}"):


                    delete_faq(row['id'])


                    log_audit(current_admin, f"Apagou FAQ ID {row['id']}")


                    st.warning("Apagado!")


                    st.rerun()





    with tab_ia:


        st.header("🧠 Curadoria Inteligente")


        st.markdown("Aqui aparecem as perguntas que o chatbot **não soube responder** (score baixo).")


        


        missed = get_missed_questions()


        


        if missed.empty:


            st.success("Excelente! Não há falhas recentes registadas.")


        else:


            for idx, row in missed.iterrows():


                with st.expander(f"❓ Pergunta: {row['query']}"):


                    st.write(f"**Data:** {row['timestamp']}")


                    st.write(f"**Melhor Score RAG:** {row['faq_score']:.2f}")


                    


                    st.divider()


                    st.subheader("Transformar em FAQ")


                    with st.form(f"form_missed_{row['id']}"):


                        new_cat = st.text_input("Categoria", value="Geral")


                        new_preg = st.text_input("Pergunta Corrigida", value=row['query'])


                        new_resp = st.text_area("Resposta Oficial")


                        new_tags = st.text_input("Tags")


                        


                        if st.form_submit_button("Aprovar e Adicionar à Base"):


                            add_custom_faq(new_cat, new_preg, new_resp, new_tags)


                            log_audit(current_admin, f"Curadoria: Adicionou FAQ de falha '{new_preg[:30]}'")


                            st.success("Nova FAQ adicionada! O bot já aprendeu esta resposta.")


                            st.rerun()





    with tab_audit:


        st.header("📜 Logs de Auditoria")


        st.markdown("Registo de todas as ações administrativas realizadas no sistema.")


        


        logs = get_audit_logs()


        if logs.empty:


            st.info("Ainda não existem registos de auditoria.")


        else:


            st.dataframe(logs, width='stretch')


            


    with tab_tickets:


        st.header("🔧 Pedidos de Revisão Humana")


        


        # Filtros


        colf1, colf2, colf3 = st.columns(3)


        


        tickets_df = get_tickets()


        


        if tickets_df.empty:


            st.info("Ainda não existem pedidos de revisão humana.")


        else:


            # Converter timestamp para datetime se ainda não for


            tickets_df['timestamp'] = pd.to_datetime(tickets_df['timestamp'])


            


            with colf1:


                date_range = st.date_input("Filtrar por Data", value=[tickets_df['timestamp'].min().date(), tickets_df['timestamp'].max().date()])


            


            with colf2:


                users = ["Todos"] + sorted(tickets_df['user_id'].unique().tolist())


                selected_user = st.selectbox("Filtrar por Utilizador", users)


                


            with colf3:


                cats = ["Todas"] + sorted(tickets_df['categoria'].unique().tolist())


                selected_cat = st.selectbox("Filtrar por Categoria", cats)


                


            # Aplicar Filtros


            filtered_df = tickets_df.copy()


            


            if len(date_range) == 2:


                start_date, end_date = date_range


                filtered_df = filtered_df[(filtered_df['timestamp'].dt.date >= start_date) & (filtered_df['timestamp'].dt.date <= end_date)]


            


            if selected_user != "Todos":


                filtered_df = filtered_df[filtered_df['user_id'] == selected_user]


                


            if selected_cat != "Todas":


                filtered_df = filtered_df[filtered_df['categoria'] == selected_cat]


                


            st.divider()


            


            # Formatação para exibição


            display_df = filtered_df.copy()


            display_df['Data'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')


            display_df = display_df[['id', 'Data', 'user_id', 'original_query', 'details', 'categoria', 'status']]


            display_df.columns = ['ID', 'Data/Hora', 'Utilizador', 'Pergunta Original', 'Detalhes/Motivo', 'Categoria', 'Estado']


            


            st.dataframe(display_df, width='stretch')


            


            # Gestão de Tickets Individuais


            st.subheader("Gerir Estado dos Pedidos")


            ticket_to_update = st.selectbox("Seleccione o ID do Pedido para atualizar:", display_df['ID'].tolist() if not display_df.empty else [])


            


            if ticket_to_update:


                # Re-fetch current status properly


                current_status = tickets_df[tickets_df['id'] == ticket_to_update]['status'].iloc[0]


                


                colu1, colu2 = st.columns([2, 1])


                with colu1:


                    new_status = st.selectbox("Novo Estado:", ["Pendente", "Em Análise", "Resolvido", "Cancelado"], index=["Pendente", "Em Análise", "Resolvido", "Cancelado"].index(current_status))


                with colu2:


                    if st.button("Actualizar Estado"):


                        update_ticket_status(ticket_to_update, new_status)


                        st.success(f"Ticket #{ticket_to_update} atualizado para {new_status}!")


                        st.rerun()





if __name__ == "__main__":


    admin_panel()


