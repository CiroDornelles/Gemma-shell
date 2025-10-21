#!/usr/bin/env python3
"""
Script de demonstração para o agente de IA com memória
"""
from ia_agent import IA_Agent

def demo():
    print("Iniciando demonstração do Agente de IA com Memória")
    print("="*60)
    
    # Cria o agente
    agent = IA_Agent(model='gemma3:latest', voice='pf_dora')
    
    # Exemplo de conversa com memória
    prompts = [
        "Olá, meu nome é João. Prazer em conhecê-lo!",
        "Como você se chama?",
        "O que você faz?",
        "Lembre-se do meu nome: João.",
        "Qual é o meu nome?",
    ]
    
    for i, prompt in enumerate(prompts):
        print(f"\n--- Interação {i+1} ---")
        agent.process_input(prompt, text_only=False)
        print("-" * 30)
    
    # Mostra o resumo da memória
    print(f"\nResumo da conversa:\n{agent.get_memory_summary()}")

def demo_interativo():
    print("\nIniciando modo interativo...")
    print("Digite 'sair' para encerrar, 'limpar' para limpar histórico, 'resumo' para ver resumo")
    
    agent = IA_Agent(model='gemma3:latest', voice='pf_dora')
    agent.start_conversation(text_only=False)

if __name__ == "__main__":
    print("Escolha o modo de demonstração:")
    print("1. Demonstração pré-programada")
    print("2. Modo interativo")
    
    choice = input("Digite sua escolha (1 ou 2): ").strip()
    
    if choice == "1":
        demo()
    elif choice == "2":
        demo_interativo()
    else:
        print("Escolha inválida. Saindo.")