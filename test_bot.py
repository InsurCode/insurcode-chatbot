from utils import load_faq_data, find_best_faq, get_ai_response
import os
from dotenv import load_dotenv

def test_system():
    print("--- Testando Sistema de FAQ ---")
    df = load_faq_data("data/faqs_seguro_auto_200_linhas.csv")
    
    test_queries = [
        "Como contrato um seguro?",
        "O que cobre o seguro obrigatório?",
        "Bati com o carro, o que faço?"
    ]
    
    for q in test_queries:
        print(f"\nPergunta: {q}")
        match = find_best_faq(q, df)
        if match:
            print(f"FAQ Encontrada: {match['pergunta']}")
            # response = get_ai_response(q, match)
            # print(f"IA: {response[:100]}...")
        else:
            print("Nenhuma FAQ correspondente encontrada.")

if __name__ == "__main__":
    test_system()
