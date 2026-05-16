import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import os
import sqlite3
import hashlib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def load_faq_data(file_path):
    """Carrega o dataset de FAQs."""
    df = pd.read_csv(file_path, sep=';')
    return df

def build_retriever(df):
    """Cria o motor de recuperação baseado em TF-IDF."""
    df['text_for_retrieval'] = df['pergunta'].astype(str) + " " + df['tags'].fillna('').astype(str)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['text_for_retrieval'])
    return vectorizer, tfidf_matrix

def find_best_faq_rag(query, df, vectorizer, tfidf_matrix):
    """Procura a FAQ mais relevante usando TF-IDF (RAG Retrieval)."""
    query_vec = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    best_idx = cosine_similarities.argsort()[-1]
    score = cosine_similarities[best_idx]
    
    if score > 0.2:
        row = df.iloc[best_idx]
        return {
            'pergunta': row['pergunta'],
            'resposta': row['resposta'],
            'categoria': row['categoria'],
            'requer_revisao_humana': row.get('requer_revisao_humana', 'Não'),
            'motivo_revisao': row.get('motivo_revisao', ''),
            'score': float(score)
        }
    return None

def get_ai_response(user_query, faq_match=None, user_name=None):
    """Gera uma resposta amigável usando OpenRouter."""
    model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
    active_df = load_active_datasets()
    dominios = ", ".join(active_df['categoria'].unique()) if not active_df.empty else "seguros"
    addressing = f", tratando o utilizador como {user_name}" if user_name else ""
    
    system_prompt = (
        f"És um assistente virtual especializado da seguradora InsurCode. "
        f"Atualmente tens conhecimento sobre: {dominios}. "
        f"O teu objetivo é ajudar o segurado de forma profissional, clara e empática{addressing}. "
        "Se for fornecida uma resposta de FAQ, deves usá-la como base, mas podes torná-la mais conversacional. "
        "Responde sempre de acordo com o domínio da pergunta do cliente."
    )
    
    context = ""
    if faq_match:
        context = f"\\nInformação correta da FAQ para esta dúvida:\\nPergunta: {faq_match['pergunta']}\\nResposta: {faq_match['resposta']}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Dúvida do cliente: {user_query}{context}"}
    ]
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Desculpe, ocorreu um erro ao processar a sua solicitação: {str(e)}"

def init_db():
    """Inicializa a base de dados SQLite para o histórico e analítica."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    
    # Tabela de Mensagens
    c.execute("PRAGMA table_info(messages)")
    columns = [row[1] for row in c.fetchall()]
    if not columns:
        c.execute('''CREATE TABLE messages
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      user_id TEXT,
                      role TEXT, 
                      content TEXT, 
                      timestamp DATETIME)''')
    elif 'user_id' not in columns:
        c.execute("ALTER TABLE messages ADD COLUMN user_id TEXT DEFAULT 'default_user'")
    
    # Tabela de Analítica
    c.execute("PRAGMA table_info(analytics)")
    ana_cols = [row[1] for row in c.fetchall()]
    if not ana_cols:
        c.execute('''CREATE TABLE analytics
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT,
                      query TEXT,
                      faq_pergunta TEXT,
                      faq_score REAL,
                      response_time REAL,
                      sentiment TEXT,
                      timestamp DATETIME)''')
    else:
        if 'response_time' not in ana_cols:
            c.execute("ALTER TABLE analytics ADD COLUMN response_time REAL")
        if 'sentiment' not in ana_cols:
            c.execute("ALTER TABLE analytics ADD COLUMN sentiment TEXT")
                  
    # Tabela de Datasets
    c.execute('''CREATE TABLE IF NOT EXISTS datasets
                 (filename TEXT PRIMARY KEY,
                  is_active INTEGER DEFAULT 0)''')
                  
    # Tabela de Admins
    c.execute('''CREATE TABLE IF NOT EXISTS admins
                 (username TEXT PRIMARY KEY,
                  password_hash TEXT,
                  role TEXT)''')
    
    c.execute("SELECT COUNT(*) FROM admins")
    if c.fetchone()[0] == 0:
        default_hash = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO admins (username, password_hash, role) VALUES (?, ?, ?)", 
                  ("admin", default_hash, "SuperAdmin"))

    # Tabela de Auditoria
    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  action TEXT,
                  timestamp DATETIME)''')
                  
    # Tabela de FAQs (CMS)
    c.execute("PRAGMA table_info(faqs)")
    faq_cols = [row[1] for row in c.fetchall()]
    if not faq_cols:
        c.execute('''CREATE TABLE faqs
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      categoria TEXT,
                      pergunta TEXT,
                      resposta TEXT,
                      tags TEXT,
                      source_file TEXT,
                      requer_revisao_humana TEXT DEFAULT 'Não',
                      motivo_revisao TEXT,
                      timestamp DATETIME)''')
    else:
        if 'requer_revisao_humana' not in faq_cols:
            c.execute("ALTER TABLE faqs ADD COLUMN requer_revisao_humana TEXT DEFAULT 'Não'")
        if 'motivo_revisao' not in faq_cols:
            c.execute("ALTER TABLE faqs ADD COLUMN motivo_revisao TEXT")
                  
    # Tabela de Tickets (Revisão Humana)
    c.execute("PRAGMA table_info(tickets)")
    ticket_cols = [row[1] for row in c.fetchall()]
    if not ticket_cols:
        c.execute('''CREATE TABLE tickets
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT,
                      original_query TEXT,
                      details TEXT,
                      categoria TEXT,
                      status TEXT DEFAULT 'Pendente',
                      timestamp DATETIME)''')
    else:
        if 'categoria' not in ticket_cols:
            c.execute("ALTER TABLE tickets ADD COLUMN categoria TEXT")
                  
    # Tabela de Segurados
    c.execute('''CREATE TABLE IF NOT EXISTS segurados
                 (id TEXT PRIMARY KEY,
                  nome TEXT,
                  email TEXT,
                  contacto TEXT,
                  timestamp DATETIME)''')
                  
    conn.commit()
    conn.close()

def verify_admin(username, password):
    """Verifica as credenciais do admin usando SHA256."""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT role FROM admins WHERE username = ? AND password_hash = ?", (username, password_hash))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def log_audit(username, action):
    """Regista uma ação administrativa."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO audit_logs (username, action, timestamp) VALUES (?, ?, ?)", 
              (username, action, datetime.now()))
    conn.commit()
    conn.close()

def get_audit_logs():
    """Recupera os logs de auditoria."""
    conn = sqlite3.connect('chat_history.db')
    df = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 100", conn)
    conn.close()
    return df

def import_csv_to_db(file_path, filename):
    """Importa um CSV para a tabela de FAQs se ainda não estiver lá."""
    with open(file_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        separator = ';' if ';' in first_line else ','
    df = pd.read_csv(file_path, sep=separator)
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("DELETE FROM faqs WHERE source_file = ?", (filename,))
    for _, row in df.iterrows():
        rev_val = row.get('requer_revisao_humana', 'Não')
        c.execute("INSERT INTO faqs (categoria, pergunta, resposta, tags, source_file, requer_revisao_humana, motivo_revisao, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (row['categoria'], row['pergunta'], row['resposta'], row.get('tags', ''), filename, rev_val, row.get('motivo_revisao', ''), datetime.now()))
    conn.commit()
    conn.close()

def get_all_faqs():
    """Retorna todas as FAQs da base de dados."""
    conn = sqlite3.connect('chat_history.db')
    df = pd.read_sql_query("SELECT * FROM faqs ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def update_faq(faq_id, categoria, pergunta, resposta, tags):
    """Atualiza uma FAQ existente."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("UPDATE faqs SET categoria=?, pergunta=?, resposta=?, tags=? WHERE id=?", 
              (categoria, pergunta, resposta, tags, faq_id))
    conn.commit()
    conn.close()

def delete_faq(faq_id):
    """Apaga uma FAQ."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("DELETE FROM faqs WHERE id=?", (faq_id,))
    conn.commit()
    conn.close()

def add_custom_faq(categoria, pergunta, resposta, tags):
    """Adiciona uma nova FAQ manualmente via CMS."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO faqs (categoria, pergunta, resposta, tags, source_file, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (categoria, pergunta, resposta, tags, "manual_cms", datetime.now()))
    conn.commit()
    conn.close()

def sync_datasets():
    """Sincroniza os ficheiros na pasta data com a base de dados."""
    if not os.path.exists("data"): os.makedirs("data")
    data_files = [f for f in os.listdir("data") if f.endswith(".csv")]
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    for f in data_files:
        c.execute("INSERT OR IGNORE INTO datasets (filename, is_active) VALUES (?, ?)", (f, 0))
    c.execute("SELECT COUNT(*) FROM datasets WHERE is_active = 1")
    if c.fetchone()[0] == 0 and data_files:
        c.execute("UPDATE datasets SET is_active = 1 WHERE filename = ?", (data_files[0],))
    conn.commit()
    conn.close()

def get_datasets_config():
    """Retorna a lista de datasets e o seu estado."""
    sync_datasets()
    conn = sqlite3.connect('chat_history.db')
    df = pd.read_sql_query("SELECT * FROM datasets", conn)
    conn.close()
    return df

def update_dataset_status(filename, status):
    """Atualiza o estado de um dataset (ativo/inativo)."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("UPDATE datasets SET is_active = ? WHERE filename = ?", (1 if status else 0, filename))
    conn.commit()
    conn.close()

def load_active_datasets():
    """Sincroniza ficheiros ativos e carrega as FAQs da base de dados."""
    config = get_datasets_config()
    active_files = config[config['is_active'] == 1]['filename'].tolist()
    for f in active_files:
        path = os.path.join("data", f)
        if os.path.exists(path):
            import_csv_to_db(path, f)
    conn = sqlite3.connect('chat_history.db')
    if active_files:
        query = f"SELECT categoria, pergunta, resposta, tags, source_file, requer_revisao_humana, motivo_revisao FROM faqs WHERE source_file IN ({','.join(['?']*len(active_files))} , 'manual_cms')"
        df = pd.read_sql_query(query, conn, params=active_files)
    else:
        df = pd.read_sql_query("SELECT categoria, pergunta, resposta, tags, source_file, requer_revisao_humana, motivo_revisao FROM faqs WHERE source_file = 'manual_cms'", conn)
    conn.close()
    if df.empty: return pd.DataFrame(columns=['categoria', 'pergunta', 'resposta', 'tags'])
    df['normalized_pergunta'] = df['pergunta'].astype(str).str.lower().str.strip()
    df = df.sort_values(by='requer_revisao_humana', ascending=False)
    deduplicated_df = df.drop_duplicates(subset=['normalized_pergunta'], keep='first')
    return deduplicated_df.drop(columns=['normalized_pergunta'])

def get_missed_questions():
    """Recupera perguntas onde o RAG teve score baixo."""
    conn = sqlite3.connect('chat_history.db')
    df = pd.read_sql_query("SELECT * FROM analytics WHERE faq_score < 0.2 ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def log_analytics(user_id, query, faq_match=None, response_time=0.0, sentiment="Neutro"):
    """Regista um evento de analítica detalhado."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    faq_pergunta = faq_match['pergunta'] if faq_match else "Nenhuma correspondência"
    faq_score = faq_match['score'] if faq_match else 0.0
    c.execute("INSERT INTO analytics (user_id, query, faq_pergunta, faq_score, response_time, sentiment, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)", 
              (user_id, query, faq_pergunta, faq_score, response_time, sentiment, datetime.now()))
    conn.commit()
    conn.close()

def analyze_sentiment(text):
    """Analisa o sentimento da mensagem usando a IA."""
    model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
    prompt = f"Analisa o sentimento desta mensagem de um cliente de seguros e responde APENAS com uma destas palavras: [Positivo, Neutro, Negativo, Irritado]. Mensagem: '{text}'"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        sentiment = response.choices[0].message.content.strip()
        for s in ["Positivo", "Neutro", "Negativo", "Irritado"]:
            if s in sentiment: return s
        return "Neutro"
    except: return "Neutro"

def get_analytics_data():
    """Recupera dados para o dashboard."""
    conn = sqlite3.connect('chat_history.db')
    df_analytics = pd.read_sql_query("SELECT * FROM analytics", conn)
    df_messages = pd.read_sql_query("SELECT * FROM messages", conn)
    conn.close()
    return df_analytics, df_messages

def save_message(user_id, role, content):
    """Guarda uma mensagem na base de dados."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)", 
              (user_id, role, content, datetime.now()))
    conn.commit()
    conn.close()

def get_chat_history(user_id):
    """Recupera o histórico de mensagens."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
    history = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return history

def delete_chat_history(user_id):
    """Limpa o histórico de mensagens."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def register_ticket(user_id, query, details, categoria="Geral"):
    """Regista um pedido de revisão humana."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO tickets (user_id, original_query, details, categoria, timestamp) VALUES (?, ?, ?, ?, ?)",
              (user_id, query, details, categoria, datetime.now()))
    conn.commit()
    conn.close()

def get_tickets():
    """Recupera todos os pedidos de revisão humana."""
    conn = sqlite3.connect('chat_history.db')
    df = pd.read_sql_query("SELECT * FROM tickets ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def update_ticket_status(ticket_id, new_status):
    """Atualiza o estado de um ticket."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("UPDATE tickets SET status = ? WHERE id = ?", (new_status, ticket_id))
    conn.commit()
    conn.close()

def check_unresolved_issues(user_id):
    """Verifica se as últimas interações do utilizador tiveram score baixo."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT query, faq_score FROM analytics WHERE user_id = ? ORDER BY timestamp DESC LIMIT 3", (user_id,))
    results = c.fetchall()
    conn.close()
    unresolved = [r[0] for r in results if r[1] < 0.2]
    return unresolved[0] if unresolved else None

def is_insurance_related(query):
    """Verifica se a pergunta está relacionada com o domínio de seguros."""
    model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
    prompt = (
        f"Analisa se a seguinte pergunta de um utilizador está relacionada com o mundo dos seguros "
        f"(automóvel, saúde, vida, etc.) ou com a seguradora InsurCode. "
        f"Responde APENAS com 'Sim' ou 'Não'.\\n\\nPergunta: '{query}'"
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip().lower()
        return "sim" in result
    except: return False

def get_segurados():
    """Recupera todos os segurados registados."""
    conn = sqlite3.connect('chat_history.db')
    df = pd.read_sql_query("SELECT id, nome, email, contacto FROM segurados ORDER BY nome", conn)
    conn.close()
    return df

def add_segurado(sid, nome, email, contacto):
    """Adiciona um novo segurado."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO segurados (id, nome, email, contacto, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (sid, nome, email, contacto, datetime.now()))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def update_segurado(sid, nome, email, contacto):
    """Atualiza dados de um segurado."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("UPDATE segurados SET nome = ?, email = ?, contacto = ? WHERE id = ?",
              (nome, email, contacto, sid))
    conn.commit()
    conn.close()

def delete_segurado(sid):
    """Remove um segurado."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("DELETE FROM segurados WHERE id = ?", (sid,))
    conn.commit()
    conn.close()

def find_segurado_by_id(sid):
    """Procura um segurado pelo seu ID ou Nome exato."""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT id, nome FROM segurados WHERE id = ? OR LOWER(nome) = ?", (sid, sid.lower()))
    res = c.fetchone()
    conn.close()
    if res: return {'id': res[0], 'nome': res[1]}
    return None
