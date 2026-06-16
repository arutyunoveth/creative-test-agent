import os

import json as _json

from src.shared.config.settings import get_settings
from src.shared.db.repository import db_session, json_dumps, json_loads

from .models import BrandbookDocument
from .schemas import BrandbookContextResult, BrandbookDocumentResponse


def create_brandbook_from_text(title: str, document_type: str, text_content: str,
                                client_id: str | None = None,
                                project_id: str | None = None,
                                brand_profile_id: str | None = None,
                                metadata: dict | None = None) -> BrandbookDocumentResponse:
    with db_session() as db:
        doc = BrandbookDocument(
            client_id=client_id,
            project_id=project_id,
            brand_profile_id=brand_profile_id,
            title=title,
            document_type=document_type,
            text_content=text_content,
            extracted_text=text_content,
            metadata_json=json_dumps(metadata),
        )
        db.add(doc)
        db.flush()
        db.refresh(doc)
        return _to_response(doc)


def create_brandbook_from_file(title: str, document_type: str, file_path: str,
                                extracted_text: str,
                                client_id: str | None = None,
                                project_id: str | None = None,
                                brand_profile_id: str | None = None,
                                metadata: dict | None = None) -> BrandbookDocumentResponse:
    with db_session() as db:
        doc = BrandbookDocument(
            client_id=client_id,
            project_id=project_id,
            brand_profile_id=brand_profile_id,
            title=title,
            document_type=document_type,
            file_path=file_path,
            text_content=None,
            extracted_text=extracted_text,
            metadata_json=json_dumps(metadata),
        )
        db.add(doc)
        db.flush()
        db.refresh(doc)
        return _to_response(doc)


def list_brandbooks(client_id: str | None = None, project_id: str | None = None) -> list[BrandbookDocumentResponse]:
    with db_session() as db:
        q = db.query(BrandbookDocument)
        if client_id:
            q = q.filter(BrandbookDocument.client_id == client_id)
        if project_id:
            q = q.filter(BrandbookDocument.project_id == project_id)
        docs = q.order_by(BrandbookDocument.created_at.desc()).all()
        return [_to_response(d) for d in docs]


def get_brandbook(doc_id: str) -> BrandbookDocumentResponse | None:
    with db_session() as db:
        doc = db.query(BrandbookDocument).filter(BrandbookDocument.id == doc_id).first()
        return _to_response(doc) if doc else None


def get_brandbook_context(project_id: str | None = None,
                           brand_profile_id: str | None = None) -> BrandbookContextResult:
    snippets: list[str] = []
    total_chars = 0
    with db_session() as db:
        q = db.query(BrandbookDocument)
        if project_id:
            q = q.filter(BrandbookDocument.project_id == project_id)
        if brand_profile_id:
            q = q.filter(BrandbookDocument.brand_profile_id == brand_profile_id)
        docs = q.all()
        for doc in docs:
            text = doc.extracted_text or doc.text_content or ""
            if text.strip():
                snippets.append(text.strip())
                total_chars += len(text.strip())
    return BrandbookContextResult(snippets=snippets, total_chars=total_chars)


def _to_response(doc: BrandbookDocument) -> BrandbookDocumentResponse:
    return BrandbookDocumentResponse(
        id=doc.id,
        client_id=doc.client_id,
        project_id=doc.project_id,
        brand_profile_id=doc.brand_profile_id,
        title=doc.title,
        document_type=doc.document_type,
        text_content=doc.text_content or doc.extracted_text,
        extracted_text=doc.extracted_text,
        file_path=doc.file_path,
        analysis=json_loads(doc.analysis_json) if doc.analysis_json else None,
        metadata=json_loads(doc.metadata_json),
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


ANALYSIS_PROMPT_RU = """Ты — бренд-стратег. Проанализируй брендбук и дай заключение.

СТРОГОЕ ПРАВИЛО: Пиши ТОЛЬКО по-русски. КАЖДОЕ слово должно быть русским. Никакого украинского языка. Если сомневаешься — используй русское слово.

Примеры по-русски: " Tone", "аудитория", "позиционирование", "рекомендации", "ограничения", "сильные стороны", "слабые стороны".

Текст брендбука:
---
{brandbook_text}
---

JSON ответ (без markdown):
{{
  "brand_name": "название бренда",
  "brand_summary": "резюме на русском",
  "tone_of_voice": "тон на русском",
  "target_audience": "аудитория на русском",
  "visual_identity": "визуал на русском",
  "key_messages": ["сообщения на русском"],
  "restrictions": ["ограничения на русском"],
  "compliance_rules": ["правила на русском"],
  "brand_values": ["ценности на русском"],
  "positioning": "позиционирование на русском",
  "strengths": ["сильные стороны на русском"],
  "weaknesses": ["слабые стороны на русском"],
  "recommendations": ["рекомендации на русском"]
}}"""

ANALYSIS_PROMPT_EN = """You are a brand strategist and creative director. Analyze this brandbook document and provide a structured expert assessment.

Brandbook text:
---
{brandbook_text}
---

Respond in valid JSON only (no markdown fences) with this exact structure:
{{
  "brand_name": "detected brand name or 'unknown'",
  "brand_summary": "2-3 sentence summary of what this brand is about",
  "tone_of_voice": "primary tone and communication style",
  "target_audience": "who this brand speaks to",
  "visual_identity": "visual style guidelines if mentioned",
  "key_messages": ["list of core messages the brand communicates"],
  "restrictions": ["list of things the brand forbids or restricts"],
  "compliance_rules": ["specific rules creatives must follow"],
  "brand_values": ["core brand values if mentioned"],
  "positioning": "how the brand positions itself vs competitors",
  "strengths": ["brand strengths identified from the document"],
  "weaknesses": ["gaps or weaknesses in the brandbook"],
  "recommendations": ["actionable recommendations for creatives working with this brand"]
}}"""


def analyze_brandbook(doc_id: str, lang: str = "ru") -> dict:
    doc = get_brandbook(doc_id)
    if doc is None:
        raise ValueError(f"brandbook_not_found: {doc_id}")
    text = doc.extracted_text or doc.text_content or ""
    if not text.strip():
        raise ValueError(f"brandbook_empty: {doc_id}")

    from src.shared.llm.factory import get_llm_provider
    provider = get_llm_provider()
    template = ANALYSIS_PROMPT_RU if lang == "ru" else ANALYSIS_PROMPT_EN
    prompt = template.format(brandbook_text=text[:12000])
    result = provider.generate(prompt)
    content = result.get("content", "")

    analysis = {}
    try:
        content_clean = content.strip()
        if content_clean.startswith("```"):
            lines = content_clean.split("\n")
            content_clean = "\n".join(lines[1:-1])
        start = content_clean.find("{")
        end = content_clean.rfind("}") + 1
        if start != -1 and end > start:
            content_clean = content_clean[start:end]
        analysis = _json.loads(content_clean)
    except _json.JSONDecodeError:
        analysis = {"raw_response": content, "parse_error": "Could not parse LLM response as JSON"}

    analysis = _postprocess_ru(analysis)

    with db_session() as db:
        db_doc = db.query(BrandbookDocument).filter(BrandbookDocument.id == doc_id).first()
        if db_doc:
            db_doc.analysis_json = _json.dumps(analysis, ensure_ascii=False)
            db.flush()

    return analysis


_UK_TO_RU = {
    "аудиторія": "аудитория", "аудиторії": "аудитории", "аудиторію": "аудиторию",
    "підход": "подход", "підходи": "подходы",
    "позиціонування": "позиционирование",
    "рекомендації": "рекомендации", "рекомендацію": "рекомендацию",
    "обмеження": "ограничения", "обмежень": "ограничений",
    "правила": "правила", "правилами": "правилами",
    "комунікації": "коммуникации", "комунікація": "коммуникация",
    "візуальний": "визуальный", "візуальна": "визуальная", "візуальні": "визуальные",
    "стиль": "стиль", "стилю": "стиля",
    "ключові": "ключевые", "ключових": "ключевых", "ключових повідомлень": "ключевых сообщений",
    "повідомлення": "сообщения", "повідомлень": "сообщений",
    "цінності": "ценности", "цінностей": "ценностей",
    "позиціонує": "позиционирует",
    "конкурентів": "конкурентов",
    "сильні": "сильные", "сильних": "сильных",
    "слабкі": "слабые", "слабких": "слабых",
    "сторони": "стороны", "сторон": "сторон",
    "бренда": "бренда", "брендів": "брендов",
    "компанія": "компания", "компанії": "компании",
    "спеціалізується": "специализируется",
    "автоматизація": "автоматизация", "автоматизації": "автоматизации",
    "процесів": "процессов", "процеси": "процессы",
    "впровадженні": "внедрении", "впровадження": "внедрение",
    "рішень": "решений", "рішення": "решение",
    "простір": "пространство", "простору": "пространства",
    "для кого бренд говорить": "для кого бренд говорит",
    "якщо згадуються": "если упоминаются",
    "якщо згадується": "если упоминается",
    "як бренд позиціонує себе": "как бренд позиционирует себя",
    "виявлені з документа": "выявленные из документа",
    "пробели або слабкі": "пробелы или слабые",
    "документа": "документа",
    "практичні рекомендації": "практические рекомендации",
    "для роботи з цим брендом": "для работы с этим брендом",
    "визуального стиля": "визуального стиля",
    "основний тон": "основной тон",
    "стиль комунікації": "стиль коммуникации",
    "говорить": "говорит",
    "для кого": "для кого",
    "не відомо": "неизвестно",
}


def _fix_ukrainian(text: str) -> str:
    if not text:
        return text
    result = text
    for uk, ru in sorted(_UK_TO_RU.items(), key=lambda x: -len(x[0])):
        result = result.replace(uk, ru)
    return result


def _postprocess_ru(analysis: dict) -> dict:
    if not analysis or analysis.get("parse_error"):
        return analysis
    fixed = {}
    for key, value in analysis.items():
        if isinstance(value, str):
            fixed[key] = _fix_ukrainian(value)
        elif isinstance(value, list):
            fixed[key] = [_fix_ukrainian(item) if isinstance(item, str) else item for item in value]
        else:
            fixed[key] = value
    return fixed
