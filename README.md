# Agent

Este é um agente de terminal baseado em IA com saídas estruturadas usando Ollama, similar ao ShellGPT, com adição de funcionalidade TTS (text-to-speech). Inclui também um parceiro de estudos com perguntas de múltipla escolha e repetição espaçada.

## Visão Geral

O Agent é uma ferramenta inspirada no [Shell GPT](https://github.com/TheR1D/shell_gpt) que permite ao usuário descrever em linguagem natural o que deseja fazer no terminal, e o agente gera e/ou executa o comando apropriado. Utiliza o poder do modelo gemma3 com saídas estruturadas do Ollama para garantir respostas consistentes e confiáveis. Adicionalmente, inclui funcionalidade de conversão de texto em fala (TTS) usando o Kokoro TTS e um parceiro de estudos com perguntas de múltipla escolha.

## Recursos

- **Geração de comandos shell**: Descreva o que deseja fazer e o agente gera o comando apropriado
- **Execução automática**: Execute comandos gerados automaticamente ou em modo interativo
- **Modo explicativo**: Obtenha explicações detalhadas sobre os comandos gerados
- **Modo interativo**: Escolha entre executar, modificar, descrever ou abortar comandos
- **Funções estruturadas**: Utiliza saídas estruturadas do Ollama para garantir respostas consistentes
- **Suporte a múltiplas ações**: Abrir programas, executar comandos shell, listar diretórios e ler arquivos
- **Resposta em texto e áudio (TTS)**: Integração com Kokoro TTS para converter respostas em áudio
- **Parceiro de Estudos**: Sistema de perguntas e respostas com múltipla escolha, reformulação de perguntas para evitar monotonia e algoritmo de repetição espaçada (SM-2)

## Instalação

1. Certifique-se de ter o [Ollama](https://ollama.ai/) instalado e em execução
2. Baixe o modelo gemma3:
   ```bash
   ollama pull gemma3:latest
   ```
3. Clone este repositório:
   ```bash
   git clone <url-do-repositorio>
   cd agent
   ```
4. Instale as dependências:
   ```bash
   # usando uv (recomendado)
   uv sync
   ```
   
   Ou se preferir usar pip:
   ```bash
   pip install -e .
   ```

## Uso

### Modo Simples
```bash
uv run python main.py "como faço para verificar o uso de memória"
```

### Com Execução Automática
```bash
uv run python main.py "listar arquivos no diretório atual" --execute
```

### Com Explicação
```bash
uv run python main.py "abrir o editor kate" --explain
```

### Modo Interativo
```bash
uv run python main.py "como parar o processo com PID 1234" --interaction
```

### Com Resposta em Áudio (TTS)
```bash
uv run python tts_response.py "Explique como o ShellGPT pode ser útil para programadores"
```

### Modo Demonstração TTS
```bash
uv run python demo_tts.py "Explique como o ShellGPT pode ser útil para programadores"
```

### Parceiro de Estudos
```bash
# Usando o script de execução
uv run python run_study_partner.py

# Ou carregando um arquivo de perguntas específico
uv run python run_study_partner.py --question-file meu_questionario.json

# Apenas texto (sem áudio)
uv run python run_study_partner.py --text-only
```

### Comando direto para o parceiro de estudos
```bash
# Se instalado como pacote
study-partner --question-file sample_questions.json
```

## Parceiro de Estudos - Funcionalidades

O parceiro de estudos inclui:

- **Reformulação de perguntas**: Cada pergunta é reformulada de forma diferente para evitar monotonia
- **Múltipla escolha**: Cada pergunta vem com 4 opções (1 correta + 3 distratores gerados pela IA)
- **Repetição espaçada (SM-2)**: Algoritmo que ajuda a otimizar o aprendizado com base na repetição espaçada
- **Experiência com áudio**: Perguntas e opções são lidas em áudio usando o Kokoro TTS
- **Acompanhamento de progresso**: Contabiliza acertos e fornece estatísticas da sessão

### Formato do arquivo de perguntas (JSON)
```json
[
  {
    "question": "Qual é a capital do Brasil?",
    "answer": "Brasília"
  },
  {
    "question": "Qual é a fórmula química da água?",
    "answer": "H2O"
  }
]
```

## Opções Disponíveis

### Para o agente principal:
- `--shell, -s`: Gera e executa comandos shell
- `--execute, -e`: Executa comandos automaticamente
- `--explain, -x`: Explica o comando gerado
- `--interaction`: Modo interativo para escolher entre executar, modificar, descrever ou abortar
- `--model`: Especifica o modelo Ollama a ser usado (padrão: gemma3:latest)
- `--describe-shell, -d`: Descreve um comando shell
- `--voice`: Voz do Kokoro TTS a ser usada (padrão: 'pf_dora')
- `--text-only`: Apenas gera texto, sem áudio

### Para o parceiro de estudos:
- `--question-file`: Caminho para arquivo JSON com perguntas e respostas
- `--model`: Modelo Ollama a ser usado (padrão: gemma3:latest)
- `--voice`: Voz do Kokoro TTS a ser usada (padrão: 'pf_dora')
- `--text-only`: Apenas texto, sem áudio

## Funcionalidades Suportadas

O agente pode executar as seguintes funções com base na entrada do usuário:

- **open_program**: Abrir programas no sistema (ex: kate, firefox, libreoffice)
- **execute_command**: Executar comandos shell (ex: ls, ps, grep, etc.)
- **list_directory**: Listar conteúdo de diretórios
- **read_file**: Ler conteúdo de arquivos
- **Text-to-Speech**: Converter respostas textuais em áudio com Kokoro TTS
- **Study Partner**: Sessões de estudo com perguntas de múltipla escolha e repetição espaçada

## Funcionalidades TTS

O projeto inclui suporte para conversão de texto em fala (TTS) usando o Kokoro TTS:

- Integração com o sistema de IA para converter respostas textuais em áudio
- Vozes configuráveis
- Reprodução direta de respostas em áudio

## Agradecimentos

Este projeto foi fortemente inspirado no [Shell GPT](https://github.com/TheR1D/shell_gpt) e nos agradecemos aos desenvolvedores por sua excelente ferramenta que serviu como base para esta implementação adaptada para o Ollama.

## Contribuindo

Contribuições são bem-vindas! Por favor, sinta-se à vontade para abrir issues e pull requests.

## Bash Aliases

Para facilitar o uso do sistema, criamos um conjunto de aliases Bash que cobrem todas as funcionalidades. Para usá-los:

1. O arquivo de aliases está localizado em `agent_aliases.sh`
2. Adicione ao seu `~/.bashrc` ou `~/.zshrc`:
   ```bash
   source /home/ciro/Documentos/scripts/agent/agent_aliases.sh
   ```
3. Recarregue seu shell: `source ~/.bashrc`

Consulte o arquivo `ALIASES_DOCS.md` para uma lista completa de aliases disponíveis e exemplos de uso.

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.