# Bash Aliases for Agent and Study Partner

This file contains bash aliases for all the functionality of the Agent and Study Partner programs.

## Installation

To use these aliases, add the following line to your `~/.bashrc` or `~/.zshrc`:

```bash
source /path/to/your/agent/agent_aliases.sh
```

Where `/path/to/your/agent/` is the directory where you have cloned or placed the agent repository.

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

The aliases use dynamic path resolution, so they will work regardless of where the repository is located on your system.

## Available Aliases

### Terminal Agent (ShellGPT-like functionality)
- `agent` - Run the main agent with structured outputs
- `agent-explain` - Run agent with explanations
- `agent-execute` - Run agent and execute commands automatically
- `agent-shell` - Run agent for shell commands
- `agent-interact` - Run agent in interactive mode
- `agent-gemma` - Run agent with specific gemma model
- `agent-check` - Check if ollama and required models are available

### Text-to-Speech (TTS)
- `tts` - Run TTS response
- `tts-text` - Run TTS with text-only output
- `demo-tts` - Run TTS demonstration

### Study Partner (Learning Assistant)
- `study` - Start study session with audio
- `study-text` - Start study session with text only
- `study-sample` - Start study with sample questions
- `study-history` - Start study with history questions
- `study-science` - Start study with science questions
- `study-topic [general|science|history]` - Start study on specific topic
- `study-custom <file.json>` - Start study with custom question file
- `study-pf_dora` - Start study with pf_dora voice
- `study-fernando` - Start study with fernando voice

### Interactive Agent with Memory
- `agent-mem` - Start interactive agent with memory
- `agent-mem-text` - Interactive agent with memory (text only)
- `agent-mem-interact` - Interactive agent with memory in interactive mode

### Demo Scripts
- `demo-study` - Run study partner demonstration
- `demo-study-text` - Run study partner demo in text mode
- `demo-agent` - Run interactive agent demonstration

### Notes
All aliases now use `uv run` for proper dependency management, ensuring all required packages are available.

### Utility Functions
- `create-questionnaire <filename.json>` - Create a template for a new questionnaire
- `agent-clipboard` - Run agent with input from clipboard
- `study-topic [general|science|history]` - Start study on specific topic

## Examples

### Terminal Agent Examples
```bash
agent "how to check disk usage"
agent-explain "show me the top 5 processes by memory usage"
agent-execute "list files in current directory"
```

### Study Partner Examples
```bash
study                          # Start study session with audio
study-text                     # Start study session with text only
study-custom my_questions.json # Use custom question file
study-topic general            # Study general knowledge questions
create-questionnaire my_questions.json  # Create new questionnaire template
```

### Using UV (Recommended)
```bash
uv-study                      # Start study session (recommended)
uv-study-text                 # Study session, text only
uv-agent "what is python?"    # Run agent through uv
```

## Configuration

The aliases use the following defaults:
- Model: gemma3:latest
- Voice: pf_dora (for TTS)
- Question file: sample_questions.json (for study sessions)

You can change these by modifying the aliases or using the command-line options directly.