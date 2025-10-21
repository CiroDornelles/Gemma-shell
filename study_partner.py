#!/usr/bin/env python3
"""
Study Partner Agent - Um parceiro de estudos baseado em IA que faz perguntas
usando questionários e fornece experiência de aprendizado fluida com áudio.
"""
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import ollama
from pydantic import BaseModel, Field
from pathlib import Path

# Importando as funções existentes do TTS
from tts_response import get_kokoro_audio, play_audio_from_bytes


class Question(BaseModel):
    """Representa uma pergunta com múltiplas respostas"""
    question: str
    correct_answer: str
    wrong_answers: List[str] = Field(default_factory=list)


class QuestionItem(BaseModel):
    """Item de pergunta do dicionário original (antes de transformação)"""
    question: str
    answer: str


class SpacedRepetitionState(BaseModel):
    """Estado de repetição espaçada para uma pergunta específica (modelo SM-2)"""
    difficulty: float = 1.0  # Intervalo em dias para próxima revisão
    repetition_count: int = 0  # Número de vezes que a pergunta foi respondida corretamente
    last_review: Optional[datetime] = None
    easiness_factor: float = 2.5  # Fator de facilidade (quanto mais alto, mais fácil)
    next_review: Optional[datetime] = None

    def update(self, correct: bool):
        """Atualiza o estado com base na resposta do usuário usando o modelo SM-2"""
        quality = 5 if correct else 2  # Qualidade da resposta (1-5, 1=errada, 5=perfeita)
        
        # Atualiza o fator de facilidade com base na qualidade
        self.easiness_factor = max(1.3, self.easiness_factor + 0.1 - (5.0 - quality) * (0.08 + (5.0 - quality) * 0.02))
        
        if correct:
            if self.repetition_count == 0:
                # Primeira vez: intervalo de 1 dia
                self.difficulty = 1.0
            elif self.repetition_count == 1:
                # Segunda vez: intervalo de 6 dias
                self.difficulty = 6.0
            else:
                # Subsequentes: intervalo baseado no SM-2
                self.difficulty *= self.easiness_factor
        else:
            # Se errar, volta para o início
            self.repetition_count = max(0, self.repetition_count - 1)
            self.difficulty = 1.0  # Recomeça com 1 dia

        # Atualiza contagem de repetições se acertou
        if correct:
            self.repetition_count += 1
        
        self.last_review = datetime.now()
        self.next_review = datetime.now() + timedelta(days=self.difficulty)


class StudySession(BaseModel):
    """Representa uma sessão de estudo"""
    questions: List[QuestionItem]
    current_question: Optional[Question] = None
    question_states: Dict[str, SpacedRepetitionState] = Field(default_factory=dict)
    answered_questions: List[Dict[str, Any]] = Field(default_factory=list)
    score: int = 0
    total_questions: int = 0

    def get_next_question(self) -> Optional[Question]:
        """Obtém a próxima pergunta com base na repetição espaçada"""
        # Filtra perguntas que estão prontas para revisão
        now = datetime.now()
        reviewable = []
        
        for q in self.questions:
            question_text = q.question
            if question_text not in self.question_states:
                self.question_states[question_text] = SpacedRepetitionState()
            
            state = self.question_states[question_text]
            
            # Se não houver próxima revisão ou está na hora de revisar
            if state.next_review is None or state.next_review <= now:
                reviewable.append(q)
        
        if not reviewable:
            # Se nenhuma pergunta estiver pronta, retorna uma aleatória
            if self.questions:
                random.shuffle(self.questions)
                reviewable = [self.questions[0]]
        
        if not reviewable:
            return None
        
        # Pega uma pergunta aleatória entre as revisáveis
        selected_question = random.choice(reviewable)
        
        # Reformular a pergunta para evitar monotonia
        reformulated_question = self._reformulate_question(selected_question.question)
        
        # Gerar opções de múltipla escolha
        choices = self._generate_multiple_choices(selected_question)
        
        # Criar a pergunta reformulada
        reformulated_q = Question(
            question=reformulated_question,
            correct_answer=selected_question.answer,
            wrong_answers=choices
        )
        
        self.current_question = reformulated_q
        return reformulated_q

    def _reformulate_question(self, original_question: str) -> str:
        """Reformula a pergunta para evitar monotonia"""
        # Define o schema para reformulação de perguntas
        schema = {
            "type": "object",
            "properties": {
                "reformulated_question": {
                    "type": "string",
                    "description": "A pergunta reformulada de forma diferente do original"
                }
            },
            "required": ["reformulated_question"]
        }

        # Prompt para reformular a pergunta
        prompt = f"""
        Reformule a seguinte pergunta de forma diferente, mas mantendo o mesmo conteúdo e significado:
        
        Pergunta original: {original_question}
        
        Siga estas diretrizes:
        - Use palavras diferentes
        - Mude a estrutura da frase
        - Mantenha o mesmo conteúdo e significado
        - Torne mais natural ou informal se possível
        - Evite repetir exatamente as mesmas palavras
        """

        try:
            response = ollama.chat(
                model='gemma3:latest',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.8},
                format=schema
            )

            response_content = response['message']['content']
            if isinstance(response_content, str):
                try:
                    parsed_response = json.loads(response_content)
                except json.JSONDecodeError:
                    parsed_response = {"reformulated_question": original_question}
            else:
                parsed_response = response_content

            reformulated = parsed_response.get('reformulated_question', original_question)
            # Se a reformulação não for diferente, tenta retornar a original
            return reformulated if reformulated != original_question else original_question
        except Exception as e:
            print(f"Erro ao reformular pergunta: {e}")
            return original_question

    def _generate_multiple_choices(self, question_item: QuestionItem) -> List[str]:
        """Gera 3 opções de resposta incorretas usando IA"""
        # Obter respostas erradas usando IA
        schema = {
            "type": "object",
            "properties": {
                "wrong_answers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "3 respostas incorretas plausíveis relacionadas à pergunta"
                }
            },
            "required": ["wrong_answers"]
        }

        prompt = f"""
        Gere 3 respostas incorretas plausíveis para a seguinte pergunta.
        As respostas devem parecer corretas à primeira vista, mas serem claramente erradas.
        Seja criativo e evite respostas óbvias que são claramente erradas.
        
        Pergunta: {question_item.question}
        Resposta correta: {question_item.answer}
        
        Lembre-se:
        - As respostas devem ser plausíveis para desafiar o estudante
        - Evite respostas óbvias ou absurdas
        - Elas devem estar relacionadas ao tema da pergunta
        - Cada resposta deve ser única
        - Tente criar respostas que sejam semelhantes à correta mas com pequenas diferenças
        """

        try:
            response = ollama.chat(
                model='gemma3:latest',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.8},
                format=schema
            )

            response_content = response['message']['content']
            if isinstance(response_content, str):
                try:
                    parsed_response = json.loads(response_content)
                except json.JSONDecodeError:
                    # Em caso de erro de parsing, tentar extrair respostas do texto
                    content = response_content.lower()
                    wrong_answers = []
                    for i in range(1, 4):
                        if f"resposta incorreta {i}" in content or f"opcao {i}" in content:
                            wrong_answers.append(f"Resposta incorreta {i}")
                    if not wrong_answers:
                        wrong_answers = [f"Resposta incorreta {i}" for i in range(1, 4)]
                    return wrong_answers
            else:
                parsed_response = response_content

            wrong_answers = parsed_response.get('wrong_answers', [])
            
            # Se não tivermos 3 respostas, completar com respostas padrão
            while len(wrong_answers) < 3:
                wrong_answers.append(f"Resposta incorreta {len(wrong_answers) + 1}")
            
            # Limitar a 3 respostas, se houver mais
            return wrong_answers[:3]
        except Exception as e:
            print(f"Erro ao gerar respostas incorretas: {e}")
            return [f"Resposta incorreta 1", f"Resposta incorreta 2", f"Resposta incorreta 3"]

    def check_answer(self, selected_answer: str) -> bool:
        """Verifica se a resposta selecionada está correta"""
        if not self.current_question:
            return False

        is_correct = selected_answer == self.current_question.correct_answer
        
        # Atualizar o estado de repetição espaçada
        if self.current_question:
            question_text = [q.question for q in self.questions if q.answer == self.current_question.correct_answer][0]
            if question_text in self.question_states:
                self.question_states[question_text].update(is_correct)
        
        # Registrar a resposta
        self.answered_questions.append({
            'question': self.current_question.question,
            'correct_answer': self.current_question.correct_answer,
            'selected_answer': selected_answer,
            'is_correct': is_correct,
            'timestamp': datetime.now().isoformat()
        })
        
        self.total_questions += 1
        if is_correct:
            self.score += 1
        
        return is_correct


class StudyPartner:
    """Agente parceiro de estudos com memória e TTS"""
    
    def __init__(self, model: str = 'gemma3:latest', voice: str = 'pf_dora'):
        self.model = model
        self.voice = voice
        self.session: Optional[StudySession] = None
        self.running = False

    def load_questionnaire(self, questionnaire_data: List[Dict[str, str]]) -> None:
        """Carrega um conjunto de perguntas e respostas"""
        questions = [QuestionItem(question=q['question'], answer=q['answer']) for q in questionnaire_data]
        self.session = StudySession(questions=questions)

    def start_study_session(self, text_only: bool = False):
        """Inicia uma sessão de estudo interativa"""
        if not self.session:
            print("Nenhum questionário carregado. Use load_questionnaire primeiro.")
            return

        self.running = True
        print("Iniciando sessão de estudo com o Parceiro de Estudos.")
        print("O parceiro fará perguntas com múltipla escolha para você responder.")
        print("Digite 'sair' para encerrar a sessão.")
        print("-" * 60)

        while self.running:
            try:
                # Obter próxima pergunta
                question = self.session.get_next_question()
                if not question:
                    print("Não há mais perguntas disponíveis no momento.")
                    break
                
                # Exibir pergunta
                print(f"\nPergunta: {question.question}")
                
                # Gerar opções de resposta
                all_options = [question.correct_answer] + question.wrong_answers
                random.shuffle(all_options)
                
                # Exibir opções numeradas
                for i, option in enumerate(all_options, 1):
                    print(f"{i}. {option}")
                
                # Converter para áudio se não for apenas texto
                if not text_only:
                    try:
                        # Primeiro, falar a pergunta
                        question_audio, sample_rate = get_kokoro_audio(
                            f"{question.question}", 
                            voice=self.voice, 
                            repo_id='hexgrad/Kokoro-82M'
                        )
                        
                        if len(question_audio) > 0:
                            print("Reproduzindo pergunta em áudio...")
                            play_audio_from_bytes(question_audio, sample_rate)
                        
                        # Depois, falar as opções
                        options_text = "Opções: "
                        for i, option in enumerate(all_options, 1):
                            options_text += f"{i}, {option}. "
                        
                        options_audio, sample_rate = get_kokoro_audio(
                            options_text, 
                            voice=self.voice, 
                            repo_id='hexgrad/Kokoro-82M'
                        )
                        
                        if len(options_audio) > 0:
                            print("Reproduzindo opções em áudio...")
                            play_audio_from_bytes(options_audio, sample_rate)
                        
                    except Exception as e:
                        print(f"Erro na reprodução de áudio: {e}")
                
                # Obter resposta do usuário
                user_input = input("\nSua resposta (número da opção ou 'sair'): ").strip()
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    print("Encerrando sessão de estudo...")
                    self.running = False
                    break
                
                try:
                    option_index = int(user_input) - 1
                    if 0 <= option_index < len(all_options):
                        selected_answer = all_options[option_index]
                        is_correct = self.session.check_answer(selected_answer)
                        
                        if is_correct:
                            print("✅ Resposta correta!")
                            response_text = f"Correto! Parabéns! A resposta é: {question.correct_answer}"
                        else:
                            print(f"❌ Resposta incorreta. A resposta correta é: {question.correct_answer}")
                            response_text = f"Incorreto. A resposta correta é: {question.correct_answer}. Continue praticando!"
                        
                        # Falar a resposta
                        if not text_only:
                            try:
                                audio_array, sample_rate = get_kokoro_audio(
                                    response_text, 
                                    voice=self.voice, 
                                    repo_id='hexgrad/Kokoro-82M'
                                )
                                
                                if len(audio_array) > 0:
                                    print("Reproduzindo feedback em áudio...")
                                    play_audio_from_bytes(audio_array, sample_rate)
                            except Exception as e:
                                print(f"Erro na reprodução de áudio: {e}")
                        
                    else:
                        print("Opção inválida. Por favor, escolha um número da lista.")
                    
                except ValueError:
                    print("Por favor, digite um número válido da opção.")
                
                # Pausa antes da próxima pergunta
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n\nSessão de estudo interrompida pelo usuário.")
                self.running = False
                break
            except Exception as e:
                print(f"Erro durante a sessão de estudo: {e}")
                continue
        
        # Mostrar resumo da sessão
        if self.session:
            print(f"\nResumo da sessão:")
            print(f"Perguntas respondidas: {self.session.total_questions}")
            print(f"Acertos: {self.session.score}")
            print(f"Taxa de acerto: {(self.session.score / max(1, self.session.total_questions) * 100):.1f}%")

    def get_session_summary(self) -> str:
        """Retorna um resumo da sessão de estudo"""
        if not self.session:
            return "Nenhuma sessão ativa."
        
        total_questions = self.session.total_questions
        correct_answers = self.session.score
        accuracy = (correct_answers / max(1, total_questions)) * 100 if total_questions > 0 else 0
        
        summary = f"Sessão de Estudo:\n"
        summary += f"- Perguntas respondidas: {total_questions}\n"
        summary += f"- Acertos: {correct_answers}\n"
        summary += f"- Taxa de acerto: {accuracy:.1f}%\n"
        
        return summary


def main():
    """Função principal para executar o parceiro de estudos"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Parceiro de Estudos baseado em IA com TTS")
    parser.add_argument('--model', '-m', default='gemma3:latest', help='Modelo Ollama a ser usado')
    parser.add_argument('--voice', '-v', default='pf_dora', help='Voz do Kokoro TTS a ser usada')
    parser.add_argument('--text-only', action='store_true', help='Apenas texto, sem áudio')
    parser.add_argument('--questionnaire', '-q', help='Caminho para o arquivo JSON com perguntas e respostas')
    
    args = parser.parse_args()
    
    # Criar agente
    partner = StudyPartner(model=args.model, voice=args.voice)
    
    # Carregar questionário padrão se não for especificado
    if args.questionnaire:
        # Carregar do arquivo
        with open(args.questionnaire, 'r', encoding='utf-8') as f:
            questionnaire_data = json.load(f)
    else:
        # Carregar questionário de exemplo
        print("Usando questionário de exemplo...")
        questionnaire_data = [
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
            },
            {
                "question": "Qual é o maior oceano da Terra?",
                "answer": "Oceano Pacífico"
            },
            {
                "question": "Quem escreveu 'Dom Casmurro'?",
                "answer": "Machado de Assis"
            }
        ]
    
    partner.load_questionnaire(questionnaire_data)
    partner.start_study_session(text_only=args.text_only)


if __name__ == "__main__":
    main()