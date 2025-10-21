#!/usr/bin/env python3
"""
Script de teste para a funcionalidade TTS
"""
from tts_response import generate_tts_response

def test_tts():
    print("Testando a funcionalidade TTS...")
    
    # Testar com uma pergunta simples
    user_input = "Qual é a capital do Brasil?"
    
    print(f"\nPergunta: {user_input}")
    response = generate_tts_response(user_input, model='gemma3:latest', voice='pf_dora', repo_id='hexgrad/Kokoro-82M')
    
    print(f"\nResposta textual: {response}")

if __name__ == "__main__":
    test_tts()