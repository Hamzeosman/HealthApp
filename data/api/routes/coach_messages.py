"""
Coach messages endpoint — kunskapsbas för AI-coachmeddelanden.
Används av C# IPythonApiClient.GetCoachMessagesAsync(category?).
"""
from fastapi import APIRouter
from sqlalchemy import text
from core.db import get_engine
from typing import Optional

router = APIRouter(tags=["ai"])
engine = get_engine()

@router.get("/coach-messages")
def coach_messages(category: Optional[str] = None):
    with engine.connect() as conn:
        if category:
            rows = conn.execute(text("""
                SELECT category, trigger_type, message_sv, message_en,
                       tone, language, priority
                FROM coach_messages
                WHERE category = :cat
                ORDER BY priority ASC
            """), {"cat": category}).fetchall()
        else:
            rows = conn.execute(text("""
                SELECT category, trigger_type, message_sv, message_en,
                       tone, language, priority
                FROM coach_messages
                ORDER BY priority ASC
            """)).fetchall()
        return [dict(zip(
            ["category","trigger_type","message_sv","message_en","tone","language","priority"], r
        )) for r in rows]
