import json
import subprocess
import ollama
import sys
import argparse
import warnings
from pydantic import BaseModel, Field
from typing import Literal, Union, List, Optional, Dict, Any
from pathlib import Path
import os
import tempfile
import time
from datetime import datetime
import threading
import queue

# Suprimir todos os avisos
warnings.filterwarnings("ignore")

# Importando as funções existentes do main.py
from main import run_agent_interactive

# Importando as funções do TTS
from tts_response import get_kokoro_audio, play_audio_from_bytes


class Message(BaseModel):
    """Representa uma mensagem no histórico de conversa"""
    role: str  # 'user' ou 'assistant'
    content: str
    timestamp: float = Field(default_factory=time.time)


class ConversationMemory:
    """Classe para gerenciar a memória da conversa"""
    
    def __init__(self, max_messages: int = 20):
        self.messages: List[Message] = []
        self.max_messages = max_messages
    
    def add_message(self, role: str, content: str):
        """Adiciona uma mensagem ao histórico"""
        message = Message(role=role, content=content)
        self.messages.append(message)
        
        # Mantém apenas as mensagens mais recentes
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """Retorna o contexto da conversa no formato necessário para o Ollama"""
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in self.messages
        ]
    
    def clear(self):
        """Limpa o histórico de mensagens"""
        self.messages = []
    
    def get_summary(self) -> str:
        """Retorna um resumo do histórico de mensagens"""
        if not self.messages:
            return "Nenhuma conversa realizada ainda."
        
        summary = f"Conversa com {len(self.messages)} mensagens:\n"
        for i, msg in enumerate(self.messages[-5:], 1):  # Mostra as últimas 5 mensagens
            role = "Usuário" if msg.role == "user" else "Assistente"
            content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
            timestamp = datetime.fromtimestamp(msg.timestamp).strftime("%H:%M:%S")
            summary += f"{i}. {role} ({timestamp}): {content_preview}\n"
        
        return summary


def run_agent_with_memory(
    user_input: str, 
    memory: ConversationMemory, 
    model: str = 'gemma3:latest', 
    execute: bool = False, 
    explain: bool = False
):
    """
    Runs the agent with conversation memory to maintain context
    """
    # Adiciona a entrada do usuário ao histórico
    memory.add_message("user", user_input)
    
    # Define o schema para saída estruturada
    schema = {
        "type": "object",
        "properties": {
            "thought": {
                "type": "string",
                "description": "The reasoning behind the response"
            },
            "response": {
                "type": "string",
                "description": "The actual response to the user"
            },
            "function": {
                "type": "object",
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "function_name": {"const": "open_program"},
                            "program_name": {"type": "string", "description": "Name of the program to open"},
                            "arguments": {
                                "type": "array",
                                "items": {"type": "string"},
                                "default": []
                            }
                        },
                        "required": ["function_name", "program_name"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "function_name": {"const": "execute_command"},
                            "command": {"type": "string", "description": "The shell command to execute"},
                            "arguments": {
                                "type": "array",
                                "items": {"type": "string"},
                                "default": []
                            }
                        },
                        "required": ["function_name", "command"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "function_name": {"const": "list_directory"},
                            "path": {"type": "string", "description": "Path to the directory to list"}
                        },
                        "required": ["function_name"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "function_name": {"const": "read_file"},
                            "path": {"type": "string", "description": "Path to the file to read"}
                        },
                        "required": ["function_name", "path"]
                    }
                ],
                "discriminator": {
                    "propertyName": "function_name"
                }
            }
        },
        "required": ["thought", "response"]
    }

    # Prepara as mensagens com histórico
    messages = memory.get_context()
    
    # Adiciona a nova mensagem do usuário
    messages.append({
        'role': 'user',
        'content': f'{user_input}\n\nInstruções:\n- Responda com um pensamento e uma resposta clara\n- Se apropriado, inclua uma função a ser executada\n- Mantenha o contexto da conversa'
    })

    # Chama o modelo com histórico de conversa
    # Adicionando instruções para não usar markdown
    formatted_messages = []
    for msg in messages:
        if msg['role'] == 'user':
            # Adiciona instrução para não usar markdown
            content = msg['content'] + "\n\nPor favor, responda sem usar formatação markdown (sem asteriscos, negrito, itálico, etc.)."
            formatted_messages.append({'role': msg['role'], 'content': content})
        else:
            formatted_messages.append(msg)

    response = ollama.chat(
        model=model,
        messages=formatted_messages,
        options={
            'temperature': 0.7  # Um pouco mais criativo para conversas
        },
        format=schema
    )

    # Parse the response
    response_content = response['message']['content']
    if isinstance(response_content, str):
        try:
            parsed_response = json.loads(response_content)
        except json.JSONDecodeError:
            print(f"Não foi possível analisar a resposta como JSON: {response_content}")
            return "Erro ao analisar a resposta do modelo"
    else:
        parsed_response = response_content

    # Adiciona a resposta do assistente ao histórico
    response_text = parsed_response.get('response', 'Desculpe, não consegui processar sua solicitação.')
    memory.add_message("assistant", response_text)
    
    return response_text


class IA_Agent:
    """
    Agente de IA com memória que responde em texto e áudio
    """
    
    def __init__(self, model: str = 'gemma3:latest', voice: str = 'pf_dora'):
        self.model = model
        self.voice = voice
        self.memory = ConversationMemory()
        self.running = False
        self.audio_queue = queue.Queue()
    
    def process_input(self, user_input: str, text_only: bool = False):
        """
        Processa a entrada do usuário e retorna resposta em texto e/ou áudio
        """
        print(f"\nUsuário: {user_input}")
        
        # Obtém a resposta do modelo com memória
        response_text = run_agent_with_memory(
            user_input, 
            self.memory, 
            model=self.model, 
            execute=False, 
            explain=False
        )
        
        print(f"\nAssistente: {response_text}")
        
        if not text_only:
            # Gera e reproduz o áudio
            print("\nGerando áudio...")
            audio_array, sample_rate = get_kokoro_audio(response_text, voice=self.voice, repo_id='hexgrad/Kokoro-82M')
            
            if len(audio_array) > 0:
                print("Reproduzindo resposta em áudio...")
                play_audio_from_bytes(audio_array, sample_rate)
            else:
                print("Não foi possível gerar o áudio da resposta.")
        
        return response_text
    
    def start_conversation(self, text_only: bool = False):
        """
        Inicia uma conversa interativa com o usuário
        """
        self.running = True
        print("Iniciando conversa com o agente de IA.")
        print("Digite 'sair' para encerrar a conversa.")
        print("Digite 'limpar' para limpar o histórico da conversa.")
        print("Digite 'resumo' para ver um resumo da conversa.")
        print("-" * 50)
        
        while self.running:
            try:
                user_input = input("\nSua mensagem: ").strip()
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    print("Encerrando conversa...")
                    self.running = False
                    break
                elif user_input.lower() in ['limpar', 'clear']:
                    self.memory.clear()
                    print("Histórico da conversa limpo.")
                    continue
                elif user_input.lower() in ['resumo', 'resumo']:
                    print(f"\nResumo da conversa:\n{self.memory.get_summary()}")
                    continue
                elif user_input == "":
                    continue
                
                # Processa a entrada do usuário
                self.process_input(user_input, text_only)
                
            except KeyboardInterrupt:
                print("\n\nConversa interrompida pelo usuário.")
                self.running = False
                break
            except Exception as e:
                print(f"Erro durante a conversa: {e}")
                continue
    
    def get_memory_summary(self):
        """Retorna um resumo da memória da conversa"""
        return self.memory.get_summary()


def main():
    """
    Main function to run the IA agent with memory
    """
    parser = argparse.ArgumentParser(description="Agente de IA com memória e resposta em texto e áudio")
    parser.add_argument('prompt', nargs='*', help='Prompt para o agente executar', default=[])
    parser.add_argument('--model', '-m', default='gemma3:latest', help='Modelo Ollama a ser usado')
    parser.add_argument('--voice', '-v', default='pf_dora', help='Voz do Kokoro TTS a ser usada')
    parser.add_argument('--text-only', action='store_true', help='Apenas responder em texto, sem áudio')
    parser.add_argument('--interactive', '-i', action='store_true', help='Modo interativo')
    
    args = parser.parse_args()
    
    # Check for stdin input (when piped)
    stdin_passed = not sys.stdin.isatty()
    stdin = ""
    if stdin_passed:
        # Read from stdin
        stdin = sys.stdin.read()
    
    # Combine stdin and prompt if both are available
    prompt = " ".join(args.prompt) if args.prompt else ""
    if stdin and prompt:
        prompt = f"{stdin}\n\n{prompt}"
    elif stdin and not prompt:
        prompt = stdin
    
    # Create the IA agent
    agent = IA_Agent(model=args.model, voice=args.voice)
    
    if args.interactive or not prompt:
        # Interactive mode
        agent.start_conversation(text_only=args.text_only)
    else:
        # Single prompt mode
        response = agent.process_input(prompt, text_only=args.text_only)
        if args.text_only:
            print(f"\nResposta: {response}")


if __name__ == "__main__":
    main()