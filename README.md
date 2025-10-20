# Gemma-shell

Um agente de linha de comando inteligente que utiliza o Ollama com saídas estruturadas e o modelo gemma3 para gerar e executar comandos shell com base em instruções em linguagem natural.

## Visão Geral

O Gemma-shell é uma ferramenta inspirada no [Shell GPT](https://github.com/TheR1D/shell_gpt) que permite ao usuário descrever em linguagem natural o que deseja fazer no terminal, e o agente gera e/ou executa o comando apropriado. Utiliza o poder do modelo gemma3 com saídas estruturadas do Ollama para garantir respostas consistentes e confiáveis.

## Recursos

- **Geração de comandos shell**: Descreva o que deseja fazer e o agente gera o comando apropriado
- **Execução automática**: Execute comandos gerados automaticamente ou em modo interativo
- **Modo explicativo**: Obtenha explicações detalhadas sobre os comandos gerados
- **Modo interativo**: Escolha entre executar, modificar, descrever ou abortar comandos
- **Funções estruturadas**: Utiliza saídas estruturadas do Ollama para garantir respostas consistentes
- **Suporte a múltiplas ações**: Abrir programas, executar comandos shell, listar diretórios e ler arquivos

## Instalação

1. Certifique-se de ter o [Ollama](https://ollama.ai/) instalado e em execução
2. Baixe o modelo gemma3:
   ```bash
   ollama pull gemma3:latest
   ```
3. Clone este repositório:
   ```bash
   git clone https://github.com/CiroDornelles/Gemma-shell.git
   cd Gemma-shell
   ```
4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   # ou se estiver usando uv:
   uv sync
   ```

## Uso

### Modo Simples
```bash
python main.py "como faço para verificar o uso de memória"
```

### Com Execução Automática
```bash
python main.py "listar arquivos no diretório atual" --execute
```

### Com Explicação
```bash
python main.py "abrir o editor kate" --explain
```

### Modo Interativo
```bash
python main.py "como parar o processo com PID 1234" --interaction
```

### Com Geração de Shell Commands
```bash
python main.py "verificar espaço em disco" --shell
```

## Opções Disponíveis

- `--shell, -s`: Gera e executa comandos shell
- `--execute, -e`: Executa comandos automaticamente
- `--explain, -x`: Explica o comando gerado
- `--interaction`: Modo interativo para escolher entre executar, modificar, descrever ou abortar
- `--model`: Especifica o modelo Ollama a ser usado (padrão: gemma3:latest)
- `--describe-shell, -d`: Descreve um comando shell

## Funcionalidades Suportadas

O agente pode executar as seguintes funções com base na entrada do usuário:

- **open_program**: Abrir programas no sistema (ex: kate, firefox, libreoffice)
- **execute_command**: Executar comandos shell (ex: ls, ps, grep, etc.)
- **list_directory**: Listar conteúdo de diretórios
- **read_file**: Ler conteúdo de arquivos

## Agradecimentos

Este projeto foi fortemente inspirado no [Shell GPT](https://github.com/TheR1D/shell_gpt) e nos agradecemos aos desenvolvedores por sua excelente ferramenta que serviu como base para esta implementação adaptada para o Ollama.

## Contribuindo

Contribuições são bem-vindas! Por favor, sinta-se à vontade para abrir issues e pull requests.

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.