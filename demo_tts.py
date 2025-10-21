#!/usr/bin/env python3
"""
Script de demonstração para a funcionalidade TTS
"""
from tts_response import generate_tts_response
import argparse

def main():
    parser = argparse.ArgumentParser(description="Demonstração da funcionalidade TTS")
    parser.add_argument('prompt', nargs='*', help='Prompt para o agente executar', default=[])
    parser.add_argument('--model', '-m', default='gemma3:latest', help='Modelo Ollama a ser usado')
    parser.add_argument('--voice', '-v', default='pf_dora', help='Voz do Kokoro TTS a ser usada')
    parser.add_argument('--text-only', action='store_true', help='Apenas gerar texto, sem áudio')
    
    args = parser.parse_args()
    
    # Combina os argumentos do prompt
    prompt = " ".join(args.prompt) if args.prompt else "Explique como o ShellGPT pode ser útil para programadores."
    
    print(f"Executando demonstração TTS com o prompt: {prompt}")
    
    if args.text_only:
        # Apenas gerar texto
        from main import run_agent_interactive
        result = run_agent_interactive(prompt, model=args.model, execute=False, explain=False)
        if isinstance(result, dict):
            print(result.get('command', ''))
        else:
            print(result)
    else:
        # Gerar texto e áudio
        response = generate_tts_response(prompt, model=args.model, voice=args.voice, repo_id='hexgrad/Kokoro-82M')
        print(f"\nResposta textual completa:\n{response}")

if __name__ == "__main__":
    main()