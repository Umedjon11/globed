import os
import json
from random import choice
from google import genai
from google.genai import types

class AIService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def _call_gemini(self, prompt, is_json=False):
        if not self.client:
            if not self.api_key:
                self.api_key = os.getenv('GEMINI_API_KEY')
            if self.api_key:
                try:
                    self.client = genai.Client(api_key=self.api_key)
                except Exception:
                    return None
            else:
                return None

        try:
            config = None
            if is_json:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json"
                )

            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=config
            )

            text = response.text
            if not text:
                return None

            if is_json:
                return json.loads(text)
            return text
        except Exception:
            return None

    def generate_questions(self, target_universities, language='ru', count=12):
        uni_names = ", ".join([u.name for u in target_universities]) if target_universities else "Harvard, Stanford, MIT"
        prompt = f"""
        Generate {count} diagnostic multiple-choice questions for high school students preparing for top universities ({uni_names}).
        Language: {language}.
        Subjects to cover: Math (SAT level), English (Reading/Writing/Grammar), Critical Thinking, College Admissions Knowledge.
        Return a strict JSON array of objects with keys:
        - "id": integer 1 to {count}
        - "subject": string (e.g. "Математика (SAT)", "Английский язык", "Критическое мышление")
        - "question": string
        - "options": array of 4 strings
        - "correct_index": integer 0-3
        - "explanation": string
        """
        gemini_result = self._call_gemini(prompt, is_json=True)
        if gemini_result and isinstance(gemini_result, list) and len(gemini_result) >= 5:
            return gemini_result

        return [
            {
                "id": 1,
                "subject": "Английский язык (Reading)",
                "question": "Choose the word that best completes the sentence: 'The professor’s lecture was so _______ that even students with no background in physics found it engaging and clear.'",
                "options": ["lucid", "opaque", "redundant", "tedious"],
                "correct_index": 0,
                "explanation": "'Lucid' means clearly expressed and easy to understand."
            },
            {
                "id": 2,
                "subject": "Английский язык (Grammar)",
                "question": "Which of the following sentences adheres to standard written English conventions?",
                "options": [
                    "Neither the students nor the teacher were aware of the schedule change.",
                    "Neither the students nor the teacher was aware of the schedule change.",
                    "Neither the students or the teacher were aware of the schedule change.",
                    "Neither the students nor the teacher are aware yesterday."
                ],
                "correct_index": 1,
                "explanation": "When using 'neither... nor', the verb agrees with the subject closer to it ('the teacher was')."
            },
            {
                "id": 3,
                "subject": "Математика (Algebra)",
                "question": "Если 3x + 5 = 20, чему равно значение 6x - 4?",
                "options": ["26", "30", "15", "10"],
                "correct_index": 0,
                "explanation": "3x = 15 => x = 5. Тогда 6(5) - 4 = 30 - 4 = 26."
            },
            {
                "id": 4,
                "subject": "Математика (Geometry)",
                "question": "Площадь круга равна 36π. Какова длина его окружности?",
                "options": ["12π", "18π", "6π", "24π"],
                "correct_index": 0,
                "explanation": "S = πr² = 36π => r = 6. C = 2πr = 12π."
            },
            {
                "id": 5,
                "subject": "Критическое мышление",
                "question": "Все студенты Гарварда усердно учатся. Сардор учится в Гарварде. Следовательно:",
                "options": [
                    "Сардор обязательно получит диплом с отличием.",
                    "Сардор усердно учится.",
                    "Сардор изучает экономику.",
                    "Сардор приехал из Таджикистана."
                ],
                "correct_index": 1,
                "explanation": "Прямой дедуктивный вывод из посылок."
            },
            {
                "id": 6,
                "subject": "Поступление в вузы (Admissions)",
                "question": "Что такое 'Early Action' (EA) в системе подачи заявок в вузы США?",
                "options": [
                    "Подача заявки раньше обычного срока без обязательства поступать в случае одобрения",
                    "Обязательный контракт, требующий забрать заявки из всех остальных вузов",
                    "Программа получения стипендии исключительно по академическим оценкам",
                    "Подача документов весной после окончания школы"
                ],
                "correct_index": 0,
                "explanation": "Early Action — не связывающая (non-binding) ранняя подача."
            },
            {
                "id": 7,
                "subject": "Математика (Functions)",
                "question": "Функция f(x) = 2x² - 8x + 3 достигает своего минимума в точке x, равной:",
                "options": ["2", "4", "-2", "0"],
                "correct_index": 0,
                "explanation": "Вершина параболы x = -b / (2a) = 8 / 4 = 2."
            },
            {
                "id": 8,
                "subject": "Английский язык (Vocabulary)",
                "question": "What is the antonym of 'pragmatic'?",
                "options": ["practical", "idealistic", "cynical", "astute"],
                "correct_index": 1,
                "explanation": "'Pragmatic' means practical and realistic; 'idealistic' is its opposite."
            },
            {
                "id": 9,
                "subject": "Критическое мышление",
                "question": "В исследовании обнаружено, что студенты, завтракающие по утрам, получают более высокие баллы. Какой вывод наиболее обоснован?",
                "options": [
                    "Завтрак напрямую вызывает повышение интеллекта.",
                    "Между завтраком и оценками есть корреляция, но причинность требует проверки.",
                    "Оценки студентов не зависят от режима дня.",
                    "Всем студентам нужно завтракать три раза в день."
                ],
                "correct_index": 1,
                "explanation": "Корреляция не всегда означает прямую причинно-следственную связь."
            },
            {
                "id": 10,
                "subject": "Поступление в вузы (Admissions)",
                "question": "Какой элемент заявки в топовый вуз США наиболее важен для демонстрации личности и индивидуальности кандидата?",
                "options": [
                    "Выписка оценок (Transcript)",
                    "Личное эссе (Personal Statement / Common App Essay)",
                    "Тест SAT Subject Test",
                    "Копия паспорта"
                ],
                "correct_index": 1,
                "explanation": "Personal Statement раскрывает характер, ценности и уникальную историю заявителя."
            },
            {
                "id": 11,
                "subject": "Математика (Probability)",
                "question": "В колоде из 52 карт какова вероятность случайно вытащить туза?",
                "options": ["1/13", "1/4", "1/52", "4/13"],
                "correct_index": 0,
                "explanation": "В колоде 4 туза из 52 карт: 4/52 = 1/13."
            },
            {
                "id": 12,
                "subject": "Английский язык (Syntax)",
                "question": "Identify the dangling modifier in the sentence: 'Walking through the university campus, _______.'",
                "options": [
                    "the historic library caught my eye",
                    "I noticed the impressive architecture of the library",
                    "the bells chimed loudly",
                    "trees were gently swaying in the breeze"
                ],
                "correct_index": 1,
                "explanation": "The modifier 'Walking through...' logically belongs to the subject 'I'."
            }
        ]

    def evaluate_answers(self, questions, answers):
        correct_count = 0
        total = len(questions)
        subject_stats = {}

        for q in questions:
            qid = str(q['id'])
            user_ans = answers.get(qid)
            subj = q.get('subject', 'Общий')
            if subj not in subject_stats:
                subject_stats[subj] = {'correct': 0, 'total': 0}
            subject_stats[subj]['total'] += 1

            if user_ans is not None and int(user_ans) == int(q['correct_index']):
                correct_count += 1
                subject_stats[subj]['correct'] += 1

        overall_percent = int((correct_count / total) * 100) if total > 0 else 0

        levels = {}
        for subj, stats in subject_stats.items():
            pct = int((stats['correct'] / stats['total']) * 100) if stats['total'] > 0 else 0
            if pct >= 80:
                lvl = "Advanced"
            elif pct >= 50:
                lvl = "Intermediate"
            else:
                lvl = "Beginner"
            levels[subj] = {
                'level': lvl,
                'score': pct,
                'correct': stats['correct'],
                'total': stats['total']
            }

        return {
            'overall_percent': overall_percent,
            'correct_count': correct_count,
            'total_questions': total,
            'subject_levels': levels
        }

    def generate_lesson(self, subject, level='Intermediate', language='ru'):
        prompt = f"""
        Create a comprehensive academic lesson for a high school student applying to universities like Harvard/Stanford.
        Subject: {subject}
        Current level: {level}
        Language: {language}
        Return JSON object with keys:
        - "title": lesson title
        - "description": brief summary
        - "theory": array of paragraphs (strings)
        - "key_takeaways": array of 3 bullet points
        - "practice_quiz": array of 2 multiple-choice questions with "question", "options" (4 items), "correct_index", "explanation"
        """
        gemini_result = self._call_gemini(prompt, is_json=True)
        if gemini_result and isinstance(gemini_result, dict) and 'theory' in gemini_result:
            return gemini_result

        lessons_bank = {
            'Математика (SAT)': [
                {
                    "title": "Квадратичные функции и свойства параболы в SAT Math",
                    "description": "Разбор формулы вершины, симметрии параболы и нахождения экстремумов без калькулятора.",
                    "theory": [
                        "Квадратичная функция в общем виде задается уравнением f(x) = ax² + bx + c. Графиком является парабола с осью симметрии x = -b / (2a).",
                        "В вопросах секции Digital SAT Math часто требуется найти координаты вершины (h, k), где h = -b / (2a), а k = f(h). Если a > 0, ветви направлены вверх, и функция достигает минимума в вершине.",
                        "Форма с выделенным полным квадратом f(x) = a(x - h)² + k позволяет мгновенно определить вершину (h, k) и минимальное/максимальное значение."
                    ],
                    "key_takeaways": [
                        "Ось симметрии параболы всегда проходит через x = -b / (2a).",
                        "Форма f(x) = a(x - h)² + k сразу дает координаты вершины (h, k).",
                        "Количество пересечений с осью x определяется знаком дискриминанта D = b² - 4ac."
                    ],
                    "practice_quiz": [
                        {
                            "question": "В какой точке функция f(x) = x² - 6x + 14 достигает своего минимального значения?",
                            "options": ["(3, 5)", "(6, 14)", "(-3, 41)", "(0, 14)"],
                            "correct_index": 0,
                            "explanation": "x = -(-6)/(2*1) = 3. Подставляем: 3² - 6*3 + 14 = 9 - 18 + 14 = 5. Вершина (3, 5)."
                        },
                        {
                            "question": "Если дискриминант D < 0, сколько действительных корней имеет квадратное уравнение?",
                            "options": ["0", "1", "2", "Бесконечно много"],
                            "correct_index": 0,
                            "explanation": "При D < 0 график параболы не пересекает ось x, действительных корней нет."
                        }
                    ]
                },
                {
                    "title": "Системы линейных уравнений и анализ решений",
                    "description": "Как определять единственное решение, отсутствие решений и бесконечное число решений.",
                    "theory": [
                        "Система из двух линейных уравнений ax + by = c и dx + ey = f описывает две прямые на координатной плоскости.",
                        "Система не имеет решений (no solution), если прямые параллельны: a/d = b/e != c/f. Их угловые коэффициенты равны, но точки пересечения с осью y различны.",
                        "Система имеет бесконечно много решений (infinitely many solutions), если уравнения тождественны: a/d = b/e = c/f."
                    ],
                    "key_takeaways": [
                        "Параллельные прямые имеют одинаковый наклон (slope) и не пересекаются.",
                        "Совпадающие прямые дают бесконечное количество общих точек.",
                        "Пересекающиеся прямые имеют ровно одно общее решение."
                    ],
                    "practice_quiz": [
                        {
                            "question": "При каком значении k система 2x + 4y = 8 и 4x + ky = 20 не имеет решений?",
                            "options": ["8", "4", "2", "16"],
                            "correct_index": 0,
                            "explanation": "Для отсутствия решений наклоны должны совпадать: 2/4 = 4/k => 2k = 16 => k = 8."
                        },
                        {
                            "question": "Что означает, если прямые в системе имеют разные угловые коэффициенты (slopes)?",
                            "options": ["Ровно одно решение", "Нет решений", "Бесконечно много решений", "Решение зависит от знака константы"],
                            "correct_index": 0,
                            "explanation": "Прямые с разными наклонами всегда пересекаются в единственной точке."
                        }
                    ]
                }
            ],
            'Английский (Reading & Writing)': [
                {
                    "title": "Риторический анализ и логика связок (Transitions)",
                    "description": "Секреты выбора соединительных слов: furthermore, however, nevertheless, consequently.",
                    "theory": [
                        "Задания на слова-связки (Transitions) проверяют логическую связь между предложениями в тексте. Связки делятся на три главные категории: продолжение/дополнение (Addition), контраст (Contrast) и следствие/причина (Causation).",
                        "Для контраста используются: however, nonetheless, on the contrary, conversely. Они сигнализируют о смене направления мысли автора.",
                        "Для следствия используются: therefore, thus, consequently, as a result. Они связывают предпосылку с логическим выводом."
                    ],
                    "key_takeaways": [
                        "Определите отношение между идеями до того, как смотреть на варианты ответа.",
                        "Если два варианта ответа являются полными синонимами (например, therefore и consequently), обычно оба неверны.",
                        "Не выбирайте связку только потому, что она звучит академично — важна логика текста."
                    ],
                    "practice_quiz": [
                        {
                            "question": "Какое слово выражает логическое следствие из предыдущего утверждения?",
                            "options": ["Therefore", "However", "Similarly", "Conversely"],
                            "correct_index": 0,
                            "explanation": "'Therefore' выражает логический вывод или результат ('следовательно')."
                        },
                        {
                            "question": "Какое слово указывает на неожиданный контраст или уступку?",
                            "options": ["Nevertheless", "Furthermore", "In addition", "Consequently"],
                            "correct_index": 0,
                            "explanation": "'Nevertheless' означает 'тем не менее' и используется для контраста."
                        }
                    ]
                }
            ],
            'Критическое мышление': [
                {
                    "title": "Выявление логических ошибок и когнитивных искажений",
                    "description": "Анализ ошибок Ad Hominem, Post Hoc Ergo Propter Hoc и ложной дилеммы в академических тестах.",
                    "theory": [
                        "Критическое мышление — основа успешного обучения в вузах уровня Harvard и Stanford. Оно требует умения отличать валидные аргументы от ошибочных рассуждений.",
                        "Ошибка 'Post Hoc' заключается в предположении, что если событие B произошло после события A, значит A вызвало B. Корреляция во времени не доказывает причинно-следственную связь.",
                        "Ложная дилемма (False Dichotomy) искусственно сужает спектр выбора до двух взаимоисключающих вариантов, игнорируя промежуточные сценарии."
                    ],
                    "key_takeaways": [
                        "Всегда проверяйте скрытые допущения (assumptions) автора текста.",
                        "Временная последовательность событий не доказывает их причинность.",
                        "Сильный аргумент опирается на верифицируемые факты, а не на авторитет спикера."
                    ],
                    "practice_quiz": [
                        {
                            "question": "В чем заключается ошибка 'Post hoc ergo propter hoc'?",
                            "options": [
                                "Принятие временной последовательности за причинную связь",
                                "Атака на личность оппонента вместо критики аргумента",
                                "Искажение позиции оппонента для легкого опровержения",
                                "Использование эмоционально окрашенных слов"
                            ],
                            "correct_index": 0,
                            "explanation": "'После этого — значит по причине этого' — классическая ошибка ложной причинности."
                        },
                        {
                            "question": "Какое допущение обязательно должно быть истинным, чтобы вывод аргумента был валидным?",
                            "options": ["Необходимое допущение (Necessary assumption)", "Мнение большинства", "Любая непроверенная гипотеза", "Аналогия с историческим событием"],
                            "correct_index": 0,
                            "explanation": "Необходимое допущение — логический мост, без которого аргумент разрушается."
                        }
                    ]
                }
            ]
        }

        subj_key = 'Математика (SAT)'
        for k in lessons_bank.keys():
            if k.lower() in subject.lower() or subject.lower() in k.lower():
                subj_key = k
                break

        options = lessons_bank.get(subj_key, lessons_bank['Математика (SAT)'])
        return choice(options)

    def chat(self, history, user_message, student_context=None):
        context_str = ""
        if student_context:
            context_str = f"Student: {student_context.get('name')}, Grade: {student_context.get('grade')}, Targets: {student_context.get('targets')}. "

        prompt = f"""
        You are Globed.ai admissions mentor and tutor.
        Context: {context_str}
        Student message: {user_message}
        Respond politely, clearly, practically, and academically in the language matching the student query (Russian, English, or Tajik).
        Give concrete advice, deadlines, requirements, and encouragement.
        """
        gemini_result = self._call_gemini(prompt, is_json=False)
        if gemini_result:
            return gemini_result

        return (
            f"Отличный вопрос! При подготовке к поступлению важно помнить три ключевых аспекта:\n\n"
            f"1. **Академический профиль:** Поддерживайте высокий средний балл (GPA) и готовьтесь к стандартизированным тестам (SAT/IELTS).\n"
            f"2. **Внеучебная деятельность (Extracurriculars):** Университеты ищут инициативных лидеров. Развивайте 2-3 проекта, в которых у вас есть реальный измеримый результат.\n"
            f"3. **Эссе и мотивация:** Ваша история должна отвечать на вопрос 'Почему именно этот университет и как вы сделаете мир лучше?'.\n\n"
            f"Продолжайте ежедневную практику уроков на Globed.ai, чтобы систематически повышать свой балл!"
        )

ai_service = AIService()
