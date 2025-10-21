#!/usr/bin/env python3
"""
Script para testar partes específicas do parceiro de estudos
"""

import json
from study_partner import StudyPartner, StudySession, QuestionItem

def test_reformulation():
    print("Testando reformulação de perguntas...")
    
    # Criar uma sessão de teste
    questions = [QuestionItem(question="Qual é a capital do Brasil?", answer="Brasília")]
    session = StudySession(questions=questions)
    
    # Testar reformulação
    original = "Qual é a capital do Brasil?"
    reformulated = session._reformulate_question(original)
    print(f"Original: {original}")
    print(f"Reformulada: {reformulated}")
    print()

def test_multiple_choice():
    print("Testando geração de múltiplas escolhas...")
    
    # Criar uma sessão de teste
    questions = [QuestionItem(question="Qual é a fórmula química da água?", answer="H2O")]
    session = StudySession(questions=questions)
    
    # Testar geração de múltiplas escolhas
    wrong_choices = session._generate_multiple_choices(questions[0])
    print(f"Pergunta: {questions[0].question}")
    print(f"Resposta correta: {questions[0].answer}")
    print(f"Respostas incorretas geradas: {wrong_choices}")
    print()

def test_spaced_repetition():
    print("Testando algoritmo de repetição espaçada...")
    
    from study_partner import SpacedRepetitionState
    from datetime import datetime, timedelta
    
    state = SpacedRepetitionState()
    print(f"Estado inicial - Intervalo: {state.difficulty} dias, Fator de facilidade: {state.easiness_factor}")
    
    # Simular resposta correta
    state.update(correct=True)
    print(f"Após resposta correta - Intervalo: {state.difficulty:.2f} dias, Fator de facilidade: {state.easiness_factor:.2f}")
    
    # Simular outra resposta correta
    state.update(correct=True)
    print(f"Após segunda resposta correta - Intervalo: {state.difficulty:.2f} dias, Fator de facilidade: {state.easiness_factor:.2f}")
    
    # Simular resposta incorreta
    state.update(correct=False)
    print(f"Após resposta incorreta - Intervalo: {state.difficulty:.2f} dias, Fator de facilidade: {state.easiness_factor:.2f}")
    print()

def test_full_session():
    print("Testando sessão completa de estudo...")
    
    partner = StudyPartner(model='gemma3:latest', voice='pf_dora')
    
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
        }
    ]
    
    partner.load_questionnaire(sample_questions)
    
    # Obter uma pergunta
    question = partner.session.get_next_question()
    if question:
        print(f"Pergunta original: {sample_questions[0]['question']}")
        print(f"Pergunta reformulada: {question.question}")
        print(f"Resposta correta: {question.correct_answer}")
        print(f"Respostas incorretas: {question.wrong_answers}")
        
        # Testar resposta correta
        is_correct = partner.session.check_answer(question.correct_answer)
        print(f"Resposta correta detectada: {is_correct}")
        
        # Testar resposta incorreta
        wrong_answer = question.wrong_answers[0] if question.wrong_answers else "Resposta errada"
        is_correct = partner.session.check_answer(wrong_answer)
        print(f"Resposta incorreta detectada: {not is_correct}")
        
    print()

if __name__ == "__main__":
    print("Executando testes do Parceiro de Estudos")
    print("="*50)
    
    test_reformulation()
    test_multiple_choice()
    test_spaced_repetition()
    test_full_session()
    
    print("Testes concluídos!")