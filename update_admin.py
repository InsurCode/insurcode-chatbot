import os

path = 'admin_page.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update imports
old_import = "get_all_faqs, update_faq, delete_faq, add_custom_faq, get_missed_questions,\n                    log_audit, get_audit_logs, get_tickets, update_ticket_status)"
new_import = "get_all_faqs, update_faq, delete_faq, add_custom_faq, get_missed_questions,\n                    log_audit, get_audit_logs, get_tickets, update_ticket_status,\n                    get_segurados, add_segurado, update_segurado, delete_segurado, find_segurado_by_id)"

if "get_segurados" not in text:
    text = text.replace(old_import, new_import)

# 2. Update Tabs
old_tabs = 'tabs = st.tabs(["📊 Analítica", "📂 Gestão de Dados", "📝 CMS (Editor)", "🧠 Curadoria de IA", "📜 Auditoria", "🔧 Revisão Humana"])'
new_tabs = 'tabs = st.tabs(["📊 Analítica", "📂 Gestão de Dados", "👤 Segurados", "📝 CMS (Editor)", "🧠 Curadoria de IA", "📜 Auditoria", "🔧 Revisão Humana"])'

old_tab_vars = 'tab_dash, tab_data, tab_cms, tab_ia, tab_audit, tab_tickets = tabs'
new_tab_vars = 'tab_dash, tab_data, tab_insured, tab_cms, tab_ia, tab_audit, tab_tickets = tabs'

text = text.replace(old_tabs, new_tabs)
text = text.replace(old_tab_vars, new_tab_vars)

# 3. Insert Tab Content
tab_insured_content = """
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
"""

if "with tab_insured:" not in text:
    # Insert before tab_cms
    text = text.replace("    with tab_cms:", tab_insured_content + "\n    with tab_cms:")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated admin_page.py successfully.")
