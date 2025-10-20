import json
import subprocess
import ollama
import sys
import argparse
from pydantic import BaseModel, Field
from typing import Literal, Union, List, Optional
from pathlib import Path
import os


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


def explain_command(function_call):
    """
    Explica detalhadamente o comando e seus argumentos
    """
    func = function_call.function
    
    if func.function_name == "open_program":
        explanation = f"""
Comando: Abrir Programa (open_program)
Programa: {func.program_name}
Argumentos: {func.arguments or 'Nenhum'}
Descrição: Esta função abrirá o programa '{func.program_name}' no seu sistema com os argumentos fornecidos.

Detalhes:
- O programa '{func.program_name}' será iniciado como um processo em segundo plano
- Se houver argumentos, eles serão passados para o programa durante a inicialização
- Esta ação é equivalente a digitar '{func.program_name} {" ".join(func.arguments) if func.arguments else ""}' no terminal
        """
    elif func.function_name == "execute_command":
        explanation = f"""
Comando: Executar Comando Shell (execute_command)
Comando: {func.command}
Argumentos: {func.arguments or 'Nenhum'}
Descrição: Esta função executará o comando shell '{func.command}' com os argumentos fornecidos.

Detalhes:
- O comando '{func.command}' será executado no shell do sistema
- Se houver argumentos, eles serão adicionados ao comando
- Esta ação é equivalente a digitar '{func.command} {" ".join(func.arguments) if func.arguments else ""}' no terminal
- A saída do comando será capturada e retornada
        """
    elif func.function_name == "list_directory":
        explanation = f"""
Comando: Listar Diretório (list_directory)
Caminho: {func.path}
Descrição: Esta função listará o conteúdo do diretório '{func.path}'.

Detalhes:
- Será executado o comando 'ls -la {func.path}' no sistema
- Mostrará todos os arquivos e diretórios em formato detalhado
- Inclui arquivos ocultos e informações de permissões, proprietário, tamanho e data de modificação
        """
    elif func.function_name == "read_file":
        explanation = f"""
Comando: Ler Arquivo (read_file)
Caminho: {func.path}
Descrição: Esta função lerá o conteúdo do arquivo '{func.path}'.

Detalhes:
- O conteúdo completo do arquivo será lido e retornado
- O arquivo deve existir e você deve ter permissão de leitura
- O conteúdo será exibido como texto puro
        """
    else:
        explanation = f"Função desconhecida: {func.function_name}"
    
    return explanation.strip()


def get_command_string(function_call):
    """
    Retorna uma representação em string do comando a ser executado
    """
    func = function_call.function
    
    if func.function_name == "open_program":
        cmd = [func.program_name] + (func.arguments or [])
        return " ".join(cmd)
    elif func.function_name == "execute_command":
        cmd = [func.command] + (func.arguments or [])
        return " ".join(cmd)
    elif func.function_name == "list_directory":
        return f"ls -la {func.path}"
    elif func.function_name == "read_file":
        return f"cat {func.path}"
    else:
        return f"Função desconhecida: {func.function_name}"


def open_program(program_name: str, arguments: list[str] = None):
    """
    Opens a program on the system
    """
    if arguments is None:
        arguments = []
    
    try:
        # Construct the command
        cmd = [program_name] + arguments
        print(f"Opening program: {' '.join(cmd)}")
        
        # Execute the program in the background
        subprocess.Popen(cmd)
        return f"Successfully opened {program_name}"
    except FileNotFoundError:
        return f"Error: Program '{program_name}' not found"
    except Exception as e:
        return f"Error opening {program_name}: {str(e)}"


def execute_command(command: str, arguments: list[str] = None):
    """
    Executes a shell command
    """
    if arguments is None:
        arguments = []
    
    try:
        # If command contains spaces, split it to extract the base command and additional arguments
        command_parts = command.split()
        if len(command_parts) > 1:
            base_cmd = command_parts[0]
            additional_args = command_parts[1:] + arguments
        else:
            base_cmd = command
            additional_args = arguments
        
        # Construct the command
        cmd = [base_cmd] + additional_args
        print(f"Executing command: {' '.join(cmd)}")
        
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Command executed successfully:\n{result.stdout}"
        else:
            return f"Command failed:\n{result.stderr}"
    except FileNotFoundError:
        return f"Error: Command '{base_cmd}' not found"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def list_directory(path: str = "."):
    """
    Lists the contents of a directory
    """
    try:
        result = subprocess.run(["ls", "-la", path], capture_output=True, text=True)
        if result.returncode == 0:
            return f"Contents of {path}:\n{result.stdout}"
        else:
            return f"Error listing directory {path}: {result.stderr}"
    except Exception as e:
        return f"Error listing directory {path}: {str(e)}"


def read_file(path: str):
    """
    Reads the content of a file
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            return f"Content of {path}:\n{content}"
    except FileNotFoundError:
        return f"Error: File '{path}' not found"
    except Exception as e:
        return f"Error reading file {path}: {str(e)}"


def interaction_loop(full_completion: str, model: str = 'gemma3:latest', explain: bool = False):
    """
    Interactive loop to handle command execution choices similar to SGPT
    """
    while True:
        try:
            print("\nOpções:")
            print("[E]xecute, [M]odify, [D]escribe, [A]bort")
            choice = input("Escolha uma opção: ").strip().lower()
            
            if choice in ('e', 'y'):  # Execute or Yes (for compatibility)
                # Execute the command
                print(f"Executando comando: {full_completion}")
                parts = full_completion.split()
                if parts:
                    cmd = parts[0]
                    args = parts[1:] if len(parts) > 1 else []
                    result = execute_command(cmd, args)
                    print(f"\nResultado: {result}")
                break
            elif choice == 'm':  # Modify
                # Allow user to modify the command
                new_command = input(f"Modifique o comando (atual: {full_completion}): ").strip()
                if new_command:
                    full_completion = new_command
                    print(f"Comando atualizado: {full_completion}")
                continue
            elif choice == 'd':  # Describe
                # Describe the command using AI
                print(f"Descrevendo o comando: {full_completion}")
                
                # Use AI to describe the command
                schema = {
                    "type": "object",
                    "properties": {
                        "explanation": {
                            "type": "string",
                            "description": "Detailed explanation of the command"
                        }
                    },
                    "required": ["explanation"]
                }
                
                response = ollama.chat(
                    model=model,
                    messages=[
                        {
                            'role': 'user', 
                            'content': f'Explique detalhadamente o seguinte comando shell: {full_completion}'
                        }
                    ],
                    format=schema
                )
                
                response_content = response['message']['content']
                if isinstance(response_content, str):
                    try:
                        parsed_response = json.loads(response_content)
                    except json.JSONDecodeError:
                        parsed_response = {"explanation": response_content}
                else:
                    parsed_response = response_content
                
                print(f"\nDescrição: {parsed_response['explanation']}")
                continue
            elif choice == 'a':  # Abort
                print("Operação abortada.")
                break
            else:
                print("Opção inválida. Por favor, escolha E, M, D ou A.")
        except KeyboardInterrupt:
            print("\nOperação abortada.")
            break


def run_agent_interactive(user_input: str, model: str = 'gemma3:latest', execute: bool = False, explain: bool = False):
    """
    Runs the agent with structured outputs to decide which function to call, with interactive options
    """
    # Define the schema for structured output with multiple possible functions
    schema = {
        "type": "object",
        "properties": {
            "thought": {
                "type": "string",
                "description": "The reasoning behind the function call"
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
        "required": ["thought", "function"]
    }

    # Call the model with structured output
    response = ollama.chat(
        model=model,
        messages=[
            {
                'role': 'user', 
                'content': f'A seguir está uma solicitação do usuário: "{user_input}". Decida qual ação tomar. Responda em formato JSON com os campos thought e function. A função deve ter function_name e os parâmetros apropriados. Para a entrada "{user_input}", retorne a chamada de função apropriada como JSON. Funções suportadas: open_program, execute_command, list_directory, read_file. Exemplos: "abrir o kate" -> open_program, "listar arquivos" -> list_directory, "ler arquivo.txt" -> read_file, "executar ls -la" -> execute_command.'
            }
        ],
        options={
            'temperature': 0  # For more deterministic output
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

    print(f"Resposta bruta: {parsed_response}")
    
    try:
        # Validate and execute the function
        function_call = FunctionCall.model_validate(parsed_response)
        
        print(f"\nPensamento: {function_call.thought}")
        
        # Show the command
        command_str = get_command_string(function_call)
        print(f"\nComando sugerido: {command_str}")
        
        if explain:
            explanation = explain_command(function_call)
            print(f"\nExplicação:")
            print(explanation)
        
        if execute:
            print(f"\nExecutando...")
            func = function_call.function
            if func.function_name == "open_program":
                result = open_program(func.program_name, func.arguments)
            elif func.function_name == "execute_command":
                result = execute_command(func.command, func.arguments)
            elif func.function_name == "list_directory":
                result = list_directory(func.path)
            elif func.function_name == "read_file":
                result = read_file(func.path)
            else:
                result = f"Função desconhecida: {func.function_name}"
            
            print(f"\nResultado: {result}")
            return result
        else:
            return {
                "command": command_str,
                "function_call": function_call,
                "thought": function_call.thought
            }
        
    except Exception as e:
        print(f"Erro ao validar resposta: {e}")
        print(f"A resposta foi: {parsed_response}")
        return "Erro ao processar a chamada de função"


def main():
    """
    Main function to run the agent with options similar to sgpt
    """
    parser = argparse.ArgumentParser(description="Agente com saídas estruturadas usando Ollama (Shell GPT-like)")
    parser.add_argument('prompt', nargs='*', help='Prompt para o agente executar', default=[])
    parser.add_argument('--model', '-m', default='gemma3:latest', help='Modelo Ollama a ser usado')
    parser.add_argument('--shell', '-s', action='store_true', help='Gerar e executar comandos shell')
    parser.add_argument('--execute', '-e', action='store_true', help='Executar comandos automaticamente')
    parser.add_argument('--explain', '-x', action='store_true', help='Explicar o comando gerado')
    parser.add_argument('--temperature', '-t', type=float, default=0.0, help='Temperatura para geracao (0.0-2.0)')
    parser.add_argument('--describe-shell', '-d', action='store_true', help='Descrever um comando shell')
    parser.add_argument('--interaction', action='store_true', help='Modo interativo para comandos shell')
    
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
    
    # Process the command with options
    result = run_agent_interactive(prompt, model=args.model, execute=args.execute or args.shell, explain=args.explain)
    
    # If shell interaction is enabled and result is a command string
    if args.interaction and isinstance(result, dict):
        command = result['command']
        print(f"\nComando gerado: {command}")
        interaction_loop(command, model=args.model, explain=args.explain)
    elif args.interaction and isinstance(result, str) and not result.startswith("Erro"):
        # If execute was already done but interaction was requested
        print("O comando já foi executado.")
    elif isinstance(result, dict):
        command = result['command']
        print(f"\nComando gerado: {command}")
        print("Execute com --execute para rodar automaticamente ou --interaction para modo interativo")


if __name__ == "__main__":
    main()