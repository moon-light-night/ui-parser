"""
Шаблоны промптов для vision-анализа и контекстного чата через Ollama.

Все промпты компактны и детерминированы:
  - явная JSON-схема в промпте для анализа
  - инструкции по привязке к контексту в системном промпте чата
  - никаких открытых директив "будь креативен"
"""
from __future__ import annotations

import json


# Промпт для анализа скриншота

_ANALYSIS_SCHEMA = json.dumps(
    {
        "screen_type": "landing_page | dashboard | form | settings | modal | mobile_screen | unknown",
        "summary": "One paragraph overview of the screen",
        "sections": [{"name": "string", "description": "string"}],
        "ui_issues": [
            {
                "title": "string",
                "severity": "low | medium | high",
                "description": "string",
                "evidence": "Specific visual element or area",
                "recommendation": "Actionable fix",
            }
        ],
        "ux_suggestions": [{"title": "string", "description": "string"}],
        "implementation_tasks": [
            {"title": "string", "description": "string", "priority": "low | medium | high"}
        ],
    },
    indent=2,
)

ANALYSIS_SYSTEM_PROMPT = """\
Вы — старший UX-инженер, проводящий анализ скриншотов интерфейса.
Отвечайте ТОЛЬКО одним JSON-объектом — без markdown-разметки, без текста до или после.
JSON должен точно соответствовать этой схеме:

{schema}

Правила:
- screen_type должен быть одним из значений перечисления.
- severity и priority должны быть "low", "medium" или "high".
- ui_issues должны охватывать реальные, наблюдаемые проблемы, видимые на изображении.
- evidence должен ссылаться на конкретный видимый элемент (например, подпись кнопки, название секции).
- recommendation должен быть конкретным и действенным.
- Возвращайте не более 5 ui_issues и не более 5 implementation_tasks.
- Если вы не уверены в чём-либо, лучше пропустите это, чем угадывайте.
- Все текстовые поля в JSON (summary, description, evidence, recommendation, title и т.д.) пишите на русском языке.
""".format(schema=_ANALYSIS_SCHEMA)

ANALYSIS_USER_PROMPT = """\
Проанализируйте приложенный скриншот интерфейса.
Верните JSON-ответ в соответствии со схемой из системного промпта.
Не включайте никакого текста за пределами JSON-объекта.\
"""


# Промпт для генерации заголовка сессии

TITLE_SYSTEM_PROMPT = """\
Вы — помощник по наименованию. По первому сообщению пользователя в сессии чата для ревью интерфейса \
ответьте кратким заголовком из 3-6 слов, отражающим тему разговора. \
Выводите ТОЛЬКО заголовок — без знаков препинания в конце, без кавычек, без пояснений. Заголовок должен быть на русском языке.\
"""

def build_title_user_prompt(user_message: str) -> str:
    return f"User's first message: {user_message[:500]}"


# Системный промпт чата (только текст, использует сохранённый анализ как контекст)

def build_chat_system_prompt(
    *,
    original_filename: str,
    screen_type: str,
    summary: str,
    analysis_json: str,
) -> str:
    """
    Формирует привязанный к контексту системный промпт, передающий LLM полный анализ.

    Модели явно указывается оставаться в рамках скриншота
    и сохранённого анализа, а также обозначать неуверенность вместо галлюцинаций.
    """
    context_block = ""
    if analysis_json:
        try:
            parsed = json.loads(analysis_json)
            # Компактно суммируем проблемы и задачи, чтобы сэкономить контекстное окно
            issues_lines = "\n".join(
                f"  [{i.get('severity','?')}] {i.get('title','')} — {i.get('description','')}"
                for i in parsed.get("ui_issues", [])[:5]
            )
            tasks_lines = "\n".join(
                f"  [{t.get('priority','?')}] {t.get('title','')} — {t.get('description','')}"
                for t in parsed.get("implementation_tasks", [])[:5]
            )
            sections_lines = "\n".join(
                f"  {s.get('name','')}: {s.get('description','')}"
                for s in parsed.get("sections", [])[:6]
            )
            suggestions_lines = "\n".join(
                f"  {s.get('title','')}: {s.get('description','')}"
                for s in parsed.get("ux_suggestions", [])[:4]
            )
            context_block = f"""
Sections identified:
{sections_lines}

UI issues found:
{issues_lines}

UX suggestions:
{suggestions_lines}

Implementation tasks:
{tasks_lines}
""".strip()
        except (json.JSONDecodeError, AttributeError):
            pass

    no_context_note = (
        "Анализ ещё не был выполнен. "
        "Отвечайте на основе общих знаний UX и укажите, что изображение недоступно."
    ) if not analysis_json else ""

    return f"""\
Вы - сфокусированный UI/UX-ассистент, анализирующий конкретный скриншот.

Скриншот: {original_filename}
Тип экрана: {screen_type or "неизвестен"}
Обзор: {summary or "Нет описания."}

{context_block or no_context_note}

Инструкции:
- Отвечайте на вопросы строго на основе скриншота и анализа выше.
- Если вопрос касается чего-то, не охваченного анализом, скажите об этом прямо.
- При необходимости ссылайтесь на конкретные названия секций, заголовки проблем или описания элементов.
- Не придумывайте детали, отсутствующие в анализе.
- Давайте чёткие и краткие ответы (2–5 предложений, если не требуется больше).
- Если вы не уверены - скажите об этом явно.
- Всегда отвечайте на русском языке.\
"""


def build_chat_messages(
    *,
    system_prompt: str,
    history: list[dict],
    user_message: str,
) -> list[dict]:
    """
    Формирует массив сообщений Ollama для одного хода чата.

    Элементы history: [{"role": "user"|"assistant"|"system", "content": "..."}]
    Из истории включаются только сообщения user/assistant (system задаётся один раз выше).
    История ограничена 20 ходами, чтобы не переполнить контекстное окно.
    """
    messages: list[dict] = [{"role": "system", "content": system_prompt}]

    recent = [m for m in history if m.get("role") in {"user", "assistant"}][-20:]
    messages.extend({"role": m["role"], "content": m["content"]} for m in recent)
    messages.append({"role": "user", "content": user_message})
    return messages
