#!/usr/bin/env python3
"""
Script para iniciar o parceiro de estudos
"""

from study_partner import StudyPartner
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="Iniciar o Parceiro de Estudos")
    parser.add_argument('--model', '-m', default='gemma3:latest', help='Modelo Ollama a ser usado')
    parser.add_argument('--voice', '-v', default='pf_dora', help='Voz do Kokoro TTS a ser usada')
    parser.add_argument('--text-only', action='store_true', help='Apenas texto, sem áudio')
    parser.add_argument('--question-file', '-q', default='sample_questions.json', help='Arquivo JSON com perguntas e respostas')
    
    args = parser.parse_args()
    
    # Criar parceiro de estudos
    partner = StudyPartner(model=args.model, voice=args.voice)
    
    # Carregar perguntas do arquivo
    try:
        with open(args.question_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
    except FileNotFoundError:
        print(f"Arquivo {args.question_file} não encontrado. Usando perguntas padrão.")
        questions_data = [
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
    
    partner.load_questionnaire(questions_data)
    partner.start_study_session(text_only=args.text_only)

if __name__ == "__main__":
    main()