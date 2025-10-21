#!/bin/bash
# Bash aliases for the Agent and Study Partner programs

# Get the directory where this script is located
AGENT_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Terminal agent with structured outputs (using uv for proper dependencies)
alias agent='uv run python "$AGENT_SCRIPT_DIR/main.py"'
alias agent-explain='uv run python "$AGENT_SCRIPT_DIR/main.py" --explain'
alias agent-execute='uv run python "$AGENT_SCRIPT_DIR/main.py" --execute'
alias agent-shell='uv run python "$AGENT_SCRIPT_DIR/main.py" --shell'
alias agent-interact='uv run python "$AGENT_SCRIPT_DIR/main.py" --interaction'

# TTS (Text-to-Speech) responses
alias tts='uv run python "$AGENT_SCRIPT_DIR/tts_response.py"'
alias tts-text='uv run python "$AGENT_SCRIPT_DIR/tts_response.py" --text-only'

# Study Partner - Learning assistant
alias study='uv run python "$AGENT_SCRIPT_DIR/run_study_partner.py"'
alias study-text='uv run python "$AGENT_SCRIPT_DIR/run_study_partner.py" --text-only'
alias study-sample='uv run python "$AGENT_SCRIPT_DIR/run_study_partner.py" --question-file "$AGENT_SCRIPT_DIR/sample_questions.json"'
alias study-history='uv run python "$AGENT_SCRIPT_DIR/run_study_partner.py" --question-file "$AGENT_SCRIPT_DIR/questionnaires.json" --model gemma3:latest'
alias study-science='uv run python "$AGENT_SCRIPT_DIR/run_study_partner.py" --question-file "$AGENT_SCRIPT_DIR/questionnaires.json" --model gemma3:latest'

# Demo scripts
alias demo-tts='uv run python "$AGENT_SCRIPT_DIR/demo_tts.py"'
alias demo-agent='uv run python "$AGENT_SCRIPT_DIR/demo_ia_agent.py"'
alias demo-study='uv run python "$AGENT_SCRIPT_DIR/demo_study_partner.py"'
alias demo-study-text='uv run python "$AGENT_SCRIPT_DIR/demo_study_partner.py" <<< "1"'

# Interactive agent with memory
alias agent-mem='uv run python "$AGENT_SCRIPT_DIR/ia_agent.py"'
alias agent-mem-text='uv run python "$AGENT_SCRIPT_DIR/ia_agent.py" --text-only'
alias agent-mem-interact='uv run python "$AGENT_SCRIPT_DIR/ia_agent.py" --interactive'

# Quick access with different models and voices
alias agent-gemma='uv run python "$AGENT_SCRIPT_DIR/main.py" --model gemma3:latest'
alias study-pf_dora='uv run python "$AGENT_SCRIPT_DIR/run_study_partner.py" --voice pf_dora'
alias study-fernando='uv run python "$AGENT_SCRIPT_DIR/run_study_partner.py" --voice fernando'

# Common study topics shortcuts
function study-topic() {
    case $1 in
        "general")
            uv run python "$AGENT_SCRIPT_DIR/run_study_partner.py" --question-file "$AGENT_SCRIPT_DIR/sample_questions.json"
            ;;
        "science")
            echo "Using science questions from questionnaires.json with specific filters would require custom handling"
            uv run python "$AGENT_SCRIPT_DIR/run_study_partner.py" --question-file "$AGENT_SCRIPT_DIR/sample_questions.json"
            ;;
        "history")
            uv run python "$AGENT_SCRIPT_DIR/run_study_partner.py" --question-file "$AGENT_SCRIPT_DIR/sample_questions.json"
            ;;
        *)
            echo "Usage: study-topic [general|science|history]"
            echo "Defaulting to general study..."
            uv run python "$AGENT_SCRIPT_DIR/run_study_partner.py"
            ;;
    esac
}

# Function to start study session with custom question file
function study-custom() {
    if [ -z "$1" ]; then
        echo "Usage: study-custom <question_file.json>"
        echo "Example: study-custom my_questions.json"
    else
        uv run python "$AGENT_SCRIPT_DIR/run_study_partner.py" --question-file "$1"
    fi
}

# Function to run agent with input from clipboard (if xclip is available)
function agent-clipboard() {
    if command -v xclip &> /dev/null; then
        input=$(xclip -selection clipboard -o)
        uv run python "$AGENT_SCRIPT_DIR/main.py" "$input"
    elif command -v pbpaste &> /dev/null; then
        input=$(pbpaste)
        uv run python "$AGENT_SCRIPT_DIR/main.py" "$input"
    else
        echo "Clipboard utility not found. Please install xclip (Linux) or use pbpaste (macOS)"
    fi
}

# Create a new question file template
function create-questionnaire() {
    if [ -z "$1" ]; then
        echo "Usage: create-questionnaire <filename.json>"
        echo "Creates a template for a new questionnaire file"
    else
        cat > "$1" << 'EOL'
[
  {
    "question": "Sua pergunta aqui",
    "answer": "Resposta correta aqui"
  },
  {
    "question": "Outra pergunta",
    "answer": "Outra resposta correta"
  }
]
EOL
        echo "Created questionnaire template: $1"
        echo "Edit this file to add your questions and answers in the format: {\"question\": \"...\", \"answer\": \"...\"}"
    fi
}

# Helper functions to check if models are available
function check-ollama() {
    if ! command -v ollama &> /dev/null; then
        echo "Error: ollama is not installed or not in PATH"
        echo "Please install ollama from https://ollama.ai/"
        return 1
    else
        echo "Ollama is available"
        return 0
    fi
}

function check-model() {
    if check-ollama; then
        if ollama list | grep -q "gemma3"; then
            echo "gemma3:latest model is available"
        else
            echo "Warning: gemma3:latest model not found. You may need to run: ollama pull gemma3:latest"
        fi
    fi
}

# Run preflight checks
alias agent-check='check-ollama && check-model'