import os

path = 'app.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

handler_code = """
# --- GLOBAL: Logout Handler ---
if st.session_state.get('logout_triggered'):
    st.session_state.navigation = "Chatbot"
    st.session_state.admin_authenticated = False
    st.session_state.logout_triggered = False
    st.rerun()
"""

# Insert after set_page_config block
import re
# Match st.set_page_config(...) with any content inside
pattern = r'st\.set_page_config\s*\(.*?\)'
match = re.search(pattern, text, re.DOTALL)

if match:
    insert_point = match.end()
    text = text[:insert_point] + "\n" + handler_code + text[insert_point:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated app.py with logout handler.")
