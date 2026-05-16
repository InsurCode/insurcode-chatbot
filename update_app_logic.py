import os

path = 'app.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_content = ""
skip = False
in_login_block = False

for i in range(len(lines)):
    line = lines[i]
    
    if 'if prompt := st.chat_input("Insira o seu nome aqui..."): ' in line or 'if prompt := st.chat_input("Insira o seu nome aqui..."): ' in line:
         in_login_block = True
    
    if in_login_block and 'st.session_state.current_user = prompt' in line:
        new_content += '        # Procura por ID ou Nome de Segurado\n'
        new_content += '        segurado = find_segurado_by_id(prompt)\n'
        new_content += '        if segurado:\n'
        new_content += "            st.session_state.current_user = segurado['nome']\n"
        new_content += '            st.session_state.is_insured = True\n'
        new_content += '        else:\n'
        new_content += '            st.session_state.current_user = prompt\n'
        new_content += '            st.session_state.is_insured = False\n'
        new_content += '        \n'
        new_content += '        # De aqui em diante usamos o current_user (que pode ser o nome real do segurado)\n'
        new_content += '        search_id = st.session_state.current_user\n'
        continue

    if in_login_block and 'history = get_chat_history(prompt)' in line:
         new_content += '        history = get_chat_history(st.session_state.current_user)\n'
         continue

    if in_login_block and 'msg = f"Olá **{prompt}**! Notei que já temos' in line:
         new_content += '            msg = f"Olá **{st.session_state.current_user}**! Notei que já temos um histórico de conversas anterior. Deseja recuperar a conversa anterior ou começar um novo chat?"\n'
         continue
         
    if in_login_block and 'msg = f"Muito prazer, **{prompt}**! Como posso ajudar' in line:
         new_content += '            msg = f"Muito prazer, **{st.session_state.current_user}**! Como posso ajudar com os seus seguros hoje?"\n'
         continue

    if 'st.rerun()' in line and in_login_block:
         new_content += line
         in_login_block = False
         continue
         
    new_content += line

# Add badge in sidebar
if 'if st.session_state.get(\'is_insured\'):' not in new_content:
    sidebar_part = '    if st.session_state.get(\'auth_step\') == "authenticated":\n'
    badge_part = '        if st.session_state.get(\'is_insured\'):\n            st.success(f"🛡️ Segurado: {st.session_state.current_user}")\n'
    new_content = new_content.replace(sidebar_part, sidebar_part + badge_part)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Updated app.py successfully.")
