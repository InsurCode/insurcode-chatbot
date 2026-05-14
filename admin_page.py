import streamlit as st
import pandas as pd
import plotly.express as px
from utils import (get_analytics_data, load_faq_data, get_datasets_config, 
                   update_dataset_status, load_active_datasets, build_retriever,
                   get_all_faqs, update_faq, delete_faq, add_custom_faq, get_missed_questions,
                   log_audit, get_audit_logs)
import os

def admin_panel(current_admin):
    st.title("🛡️ Painel de Administração")
    
    # Tab de Dashboards, Gestão, CMS e Auditoria
    tabs = st.tabs(["📊 Analítica", "📂 Gestão de Dados", "📝 CMS (Editor)", "🧠 Curadoria de IA", "📜 Auditoria"])
    tab_dash, tab_data, tab_cms, tab_ia, tab_audit = tabs
    
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
                    st.plotly_chart(fig_sent, use_container_width=True)
            
            with col_perf:
                st.subheader("Performance da IA")
                if 'response_time' in df_analytics.columns:
                    fig_perf = px.line(df_analytics, x='timestamp', y='response_time', title="Tempo de Resposta ao Longo do Tempo")
                    st.plotly_chart(fig_perf, use_container_width=True)

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
            st.dataframe(logs, use_container_width=True)

if __name__ == "__main__":
    admin_panel()
