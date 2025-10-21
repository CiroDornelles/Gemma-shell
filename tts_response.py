import json
import subprocess
import ollama
import sys
import argparse
import warnings
from pydantic import BaseModel, Field
from typing import Literal, Union, List, Optional
from pathlib import Path
import os
import tempfile

# Suprimir todos os avisos
warnings.filterwarnings("ignore")

# Importando as funções existentes do main.py
from main import run_agent_interactive


class OpenProgram(BaseModel):
    """Function to open a program on the system"""
    function_name: Literal["open_program"] = Field(description="The name of the function to call")
    program_name: str = Field(description="Name of the program to open (e.g., 'kate', 'firefox', 'libreoffice')")
    arguments: list[str] = Field(default=[], description="Additional arguments to pass to the program")


class ExecuteCommand(BaseModel):
    """Function to execute a shell command"""
    function_name: Literal["execute_command"] = Field(description="The name of the function to call")
    command: str = Field(description="The shell command to execute")
    arguments: list[str] = Field(default=[], description="Additional arguments to pass to the command")


class ListDirectory(BaseModel):
    """Function to list directory contents"""
    function_name: Literal["list_directory"] = Field(description="The name of the function to call")
    path: str = Field(default=".", description="Path to the directory to list")


class ReadFile(BaseModel):
    """Function to read a file"""
    function_name: Literal["read_file"] = Field(description="The name of the function to call")
    path: str = Field(description="Path to the file to read")


class FunctionCall(BaseModel):
    """Represents a function call from the AI model"""
    thought: str = Field(description="The reasoning behind the function call")
    function: Union[OpenProgram, ExecuteCommand, ListDirectory, ReadFile] = Field(description="The function to call")


def get_kokoro_audio(text: str, voice: str = 'pf_dora', language: str = 'p', repo_id: str = 'hexgrad/Kokoro-82M') -> tuple:
    """
    Gera áudio a partir de texto usando o Kokoro TTS
    
    Args:
        text: Texto a ser convertido em áudio
        voice: Voz a ser usada (padrão: 'pf_dora')
        language: Código do idioma (padrão: 'p' para português)
        repo_id: ID do repositório do modelo (padrão: 'hexgrad/Kokoro-82M')
    
    Returns:
        tuple: (array numpy com áudio, taxa de amostragem)
    """
    import numpy as np
    
    try:
        # Importar o kokoro dinamicamente para evitar erro se não estiver instalado
        from kokoro import KPipeline
        
        # Inicializar o pipeline do Kokoro com o repo_id explícito
        pipeline = KPipeline(language, repo_id=repo_id)
        
        # Gerar áudio a partir do texto
        audio_chunks = []
        for result in pipeline(text, voice=voice):
            # Armazenar os chunks de áudio
            audio_chunks.append(result.output.audio if result.output else None)
        
        # Filtrar valores None
        audio_chunks = [chunk for chunk in audio_chunks if chunk is not None]
        
        # Concatenar todos os chunks
        if audio_chunks:
            full_audio = np.concatenate(audio_chunks)
            # Retornar o array numpy e a taxa de amostragem padrão
            return full_audio, 24000
        else:
            print("Nenhum áudio gerado pelo Kokoro TTS.")
            return np.array([]), 24000
            
    except ImportError:
        print("O Kokoro TTS não está instalado. Por favor, instale com: pip install kokoro")
        return np.array([]), 24000
    except Exception as e:
        print(f"Erro ao gerar áudio com Kokoro TTS: {e}")
        return np.array([]), 24000


def play_audio_from_bytes(audio_array, sample_rate: int = 24000):
    """
    Reproduz áudio a partir de um array numpy
    
    Args:
        audio_array: Array numpy contendo os dados de áudio
        sample_rate: Taxa de amostragem (padrão: 24000)
    """
    try:
        import sounddevice as sd
        import numpy as np
        
        # Reproduzir o áudio usando sounddevice
        sd.play(audio_array, sample_rate)
        sd.wait()  # Espera até que a reprodução termine
        
    except ImportError:
        print("SoundDevice não está instalado. Por favor, instale com: pip install sounddevice")
    except Exception as e:
        print(f"Erro ao reproduzir áudio: {e}")


def generate_tts_response(user_input: str, model: str = 'gemma3:latest', voice: str = 'pf_dora', repo_id: str = 'hexgrad/Kokoro-82M'):
    """
    Gera resposta textual e converte para áudio usando Kokoro TTS
    
    Args:
        user_input: Entrada do usuário
        model: Modelo Ollama a ser usado
        voice: Voz do Kokoro TTS a ser usada
        repo_id: ID do repositório do modelo Kokoro
    
    Returns:
        str: Resposta textual gerada
    """
    # Obter a resposta textual do modelo
    result = run_agent_interactive(user_input, model=model, execute=False, explain=False)
    
    # Extrair a resposta textual
    if isinstance(result, dict):
        text_response = result.get('command', '')
    else:
        text_response = str(result)
    
    # Gerar áudio a partir da resposta textual
    audio_array, sample_rate = get_kokoro_audio(text_response, voice=voice, repo_id=repo_id)
    
    if len(audio_array) > 0:
        print("Reproduzindo resposta em áudio...")
        play_audio_from_bytes(audio_array, sample_rate)
    else:
        print("Não foi possível gerar o áudio da resposta.")
    
    return text_response


def main():
    """
    Main function to run the TTS response agent
    """
    parser = argparse.ArgumentParser(description="Agente com resposta em texto e áudio usando Ollama e Kokoro TTS")
    parser.add_argument('prompt', nargs='*', help='Prompt para o agente executar', default=[])
    parser.add_argument('--model', '-m', default='gemma3:latest', help='Modelo Ollama a ser usado')
    parser.add_argument('--voice', '-v', default='pf_dora', help='Voz do Kokoro TTS a ser usada')
    parser.add_argument('--text-only', action='store_true', help='Apenas gerar texto, sem áudio')
    
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
    
    if not prompt:
        print("Por favor, forneça um prompt")
        parser.print_help()
        return
    
    if args.text_only:
        # Apenas gerar texto
        result = run_agent_interactive(prompt, model=args.model, execute=False, explain=False)
        if isinstance(result, dict):
            print(result.get('command', ''))
        else:
            print(result)
    else:
        # Gerar texto e áudio
        response = generate_tts_response(prompt, model=args.model, voice=args.voice)
        print(f"\nResposta textual:\n{response}")


if __name__ == "__main__":
    main()