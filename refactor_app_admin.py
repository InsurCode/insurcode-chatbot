import os

path = 'app.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Navigation and Logic block
old_block_start = 'app_mode = st.radio("Navegação", ["Chatbot", "Painel Admin"], key="navigation")'
if old_block_start not in text:
    old_block_start = 'app_mode = st.radio("Navegação", ["Chatbot", "Painel Admin"])'

new_nav_and_auth = """
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
            
            if st.button("Entrar", use_container_width=True):
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
"""

# We need to replace from app_mode definition until the next divider or significant block.
# Let's find the range.
start_idx = text.find(old_block_start)
end_token = 'st.divider()'
end_idx = text.find(end_token, start_idx) + len(end_token)

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + new_nav_and_auth + "\n    st.divider()" + text[end_idx:]

# 2. Update Admin Panel Call
old_panel_call = """if app_mode == "Painel Admin":
    admin_panel(admin_user)
    st.stop()"""

# Since we refactored, admin_user is now in session_state.
new_panel_call = """if app_mode == "Painel Admin":
    if st.session_state.get('admin_authenticated'):
        admin_panel(st.session_state.admin_user)
    st.stop()"""

# Use a more flexible replace for the admin panel call block
# In app.py lines 208-214 approx
import re
text = re.sub(r'if app_mode == "Painel Admin":\s+admin_panel\(admin_user\)\s+st.stop\(\)', new_panel_call, text)

# Also fix the NameError in admin_page.py if it still persists (just in case)
# Wait, I already fixed utils.py and admin_page.py imports.

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Refactored app.py successfully.")
