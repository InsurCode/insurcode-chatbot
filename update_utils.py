import os

path = 'utils.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if 'c.execute("ALTER TABLE tickets ADD COLUMN categoria TEXT")' in line:
        new_lines.append("\n")
        new_lines.append("    # Nova tabela de Segurados\n")
        new_lines.append("    c.execute('''CREATE TABLE IF NOT EXISTS segurados\n")
        new_lines.append("                 (id TEXT PRIMARY KEY,\n")
        new_lines.append("                  nome TEXT,\n")
        new_lines.append("                  email TEXT,\n")
        new_lines.append("                  contacto TEXT,\n")
        new_lines.append("                  timestamp DATETIME)''')\n")

# Cleanup duplicate get_tickets/update_ticket_status if they exist
content = "".join(new_lines)

# Define the new functions
new_functions = """
# --- GESTÃO DE SEGURADOS ---

def get_segurados():
    \"\"\"Recupera todos os segurados registados.\"\"\"
    conn = sqlite3.connect('chat_history.db')
    df = pd.read_sql_query(\"SELECT id, nome, email, contacto FROM segurados ORDER BY nome\", conn)
    conn.close()
    return df

def add_segurado(sid, nome, email, contacto):
    \"\"\"Adiciona um novo segurado.\"\"\"
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    try:
        c.execute(\"INSERT INTO segurados (id, nome, email, contacto, timestamp) VALUES (?, ?, ?, ?, ?)\",
                  (sid, nome, email, contacto, datetime.now()))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def update_segurado(sid, nome, email, contacto):
    \"\"\"Atualiza dados de um segurado.\"\"\"
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute(\"UPDATE segurados SET nome = ?, email = ?, contacto = ? WHERE id = ?\",
              (nome, email, contacto, sid))
    conn.commit()
    conn.close()

def delete_segurado(sid):
    \"\"\"Remove um segurado.\"\"\"
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute(\"DELETE FROM segurados WHERE id = ?\", (sid,))
    conn.commit()
    conn.close()

def find_segurado_by_id(sid):
    \"\"\"Procura um segurado pelo seu ID ou Nome exato.\"\"\"
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    # Tentar por ID primeiro, depois por nome exato
    c.execute(\"SELECT id, nome FROM segurados WHERE id = ? OR LOWER(nome) = ?\", (sid, sid.lower()))
    res = c.fetchone()
    conn.close()
    if res:
        return {'id': res[0], 'nome': res[1]}
    return None
"""

if "# --- GESTÃO DE SEGURADOS ---" not in content:
    content += new_functions

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated utils.py successfully.")
