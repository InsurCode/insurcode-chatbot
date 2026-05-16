# Guia de Testes Passo a Passo - InsurCode Chatbot 🤖🛡️

Este guia orienta os utilizadores nos testes das principais funcionalidades da plataforma InsurCode v2.2.

## 📋 Pré-requisitos
1. Certifique-se de que o ambiente virtual está ativo.
2. Execute a aplicação: `streamlit run app.py`.
3. Tenha o ficheiro `.env` configurado com a sua `OPENROUTER_API_KEY`.

---

## 🏗️ Cenário 1: Gestão Inicial de Segurados (Admin)
*Objetivo: Preparar a base de dados para testes de identificação.*

1. No menu lateral, mude para **Painel Admin**.
2. Insira as credenciais (**User**: `admin` | **Senha**: `admin123`).
3. Vá ao separador **👤 Segurados**.
4. Clique em **➕ Registar Novo Segurado** e adicione:
   - **ID**: `101`
   - **Nome**: `Arsenio Teste`
   - **Email**: `arsenio@exemplo.com`
   - **Contacto**: `912345678`
5. Confirme que o nome aparece na **Lista de Segurados** abaixo.

---

## 👤 Cenário 2: Identificação Inteligente (Chat)
*Objetivo: Testar o reconhecimento por ID.*

1. Mude a navegação na barra lateral para **Chatbot**.
2. O bot pedirá o seu nome. Digite apenas o ID: `101`.
3. **Verificação**: O bot deve responder: *"Olá Arsenio Teste! Como posso ajudar..."*.
4. **Verificação**: Note o escudo `🛡️ Segurado: Arsenio Teste` na barra lateral.

---

## Cenário 3: Interação RAG (IA & FAQs) 🧠
*Objetivo: Testar respostas automáticas baseadas em documentos.*

1. Pergunte: *"Como posso participar um sinistro automóvel?"*
2. **Verificação**: O bot deve responder com base no FAQ "Participar Sinistro", mas com um tom conversacional amigável.
3. Clique em **Participar Sinistro** na barra lateral (Serviços Rápidos).
4. **Verificação**: O chat deve injetar a pergunta automaticamente e a IA deve responder.

---

## 🔧 Cenário 4: Escalação Humana (Escalação Iterativa)
*Objetivo: Testar o fluxo de criação de tickets.*

1. Pergunte algo fora do âmbito mas relacionado com seguros, ex: *"Quem é o CEO da seguradora?"* ou *"Quero reclamar de um técnico específico."*
2. O bot poderá indicar que a dúvida requer um técnico humano. Clique em **"Sim, fornecer detalhes"**.
3. Siga o fluxo:
   - Digite o detalhe: *"O técnico não apareceu na hora marcada."*
   - O bot perguntará se deseja adicionar mais. Diga que não (ou envie o detalhe final).
   - O bot apresentará um resumo: *"Detalhes a submeter: ..."*.
   - Confirme a submissão.
4. **Verificação**: O bot deve confirmar que o ticket foi gerado com sucesso.

---

## 📂 Cenário 5: Gestão de Tickets (Admin)
*Objetivo: Verificar a recepção do ticket no painel.*

1. Volte ao **Painel Admin -> Revisão Humana**.
2. **Verificação**: O ticket de "Arsenio Teste" deve aparecer no topo da lista.
3. Teste os filtros de data ou categoria para isolar o ticket.
4. Mude o estado para **"Em Análise"** e clique em **Atualizar Status**.

---

## Cenário 6: CMS e Curadoria (IA) 🧠
*Objetivo: Testar a evolução da base de conhecimento.*

1. No Admin, vá a **🧠 Curadoria de IA**.
2. **Verificação**: Verifique se a sua pergunta sobre o CEO ou reclamação (Cenário 4) aparece na lista de "Perguntas Não Respondidas".
3. Vá a **📝 CMS (Editor)** e adicione manualmente uma FAQ para testar a atualização em tempo real.

---

## 🚪 Cenário 7: Logout e Sessão
*Objetivo: Testar a segurança e limpeza de estado.*

1. No Painel Admin, clique no botão **"🚪 Sair do Painel"** na barra lateral.
2. **Verificação**: O sistema deve voltar imediatamente para o ecrã inicial do Chatbot.
3. Tente voltar ao Admin. **Verificação**: O sistema deve pedir login novamente (Sessão limpa).

---

### ✅ Conclusão dos Testes
Se todos os passos acima foram concluídos com sucesso, o seu sistema **InsurCode v2.2** está totalmente operacional e estável! 🚀
