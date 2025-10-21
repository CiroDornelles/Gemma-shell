#!/usr/bin/env python3
"""
Script de demonstração para o parceiro de estudos
"""

import json
from study_partner import StudyPartner

def demo_study_partner():
    print("Iniciando demonstração do Parceiro de Estudos")
    print("="*60)
    
    # Cria o parceiro de estudos
    partner = StudyPartner(model='gemma3:latest', voice='pf_dora')
    
    # Carregar questionário de exemplo
    sample_questions = [
        {
            "question": "Qual é a capital do Brasil?",
            "answer": "Brasília"
        },
        {
            "question": "Qual é a fórmula química da água?",
            "answer": "H2O"
        },
        {
            "question": "Quantos planetas existem no sistema solar?",
            "answer": "8"
        },
        {
            "question": "Qual é o maior oceano da Terra?",
            "answer": "Oceano Pacífico"
        },
        {
            "question": "Quem escreveu 'Dom Casmurro'?",
            "answer": "Machado de Assis"
        }
    ]
    
    partner.load_questionnaire(sample_questions)
    
    print("Questionário carregado com sucesso!")
    print(f"Total de perguntas: {len(sample_questions)}")
    print("\nIniciando sessão de estudo (apenas texto para demonstração)...")
    
    # Iniciar sessão de estudo (modo texto apenas para demonstração)
    partner.start_study_session(text_only=True)

def demo_with_audio():
    print("\n" + "="*60)
    print("Demonstração com áudio (TTS)")
    print("Este modo reproduzirá as perguntas e respostas em áudio")
    
    partner = StudyPartner(model='gemma3:latest', voice='pf_dora')
    
    # Carregar um questionário diferente para esta demonstração
    science_questions = [
        {
            "question": "Qual é o elemento mais abundante no universo?",
            "answer": "Hidrogênio"
        },
        {
            "question": "Quantos ossos tem um adulto humano?",
            "answer": "206"
        },
        {
            "question": "Qual é o maior órgão do corpo humano?",
            "answer": "Pele"
        }
    ]
    
    partner.load_questionnaire(science_questions)
    
    print("Iniciando sessão de estudo com áudio...")
    partner.start_study_session(text_only=False)


if __name__ == "__main__":
    print("Escolha o modo de demonstração:")
    print("1. Demonstração com apenas texto")
    print("2. Demonstração com áudio (requer audio funcionando)")
    print("3. Ambos")
    
    choice = input("Digite sua escolha (1, 2 ou 3): ").strip()
    
    if choice == "1":
        demo_study_partner()
    elif choice == "2":
        demo_with_audio()
    elif choice == "3":
        demo_study_partner()
        demo_with_audio()
    else:
        print("Escolha inválida. Saindo.")