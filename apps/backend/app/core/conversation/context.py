"""The unified conversation state object.

This module defines ``ConversationContext``, a single plain data holder
meant to represent everything known about one conversation at a given
point in time. It has no behavior of its own — it exists so that
``ConversationService``, the future Decision Engine, ``MemoryService``,
CRM integrations, and Telephony can all share one common view of a
conversation's state, instead of each component inventing its own
partial representation.

This module has no dependency on FastAPI, OpenAI, or any CRM — it is a
pure, framework-free data structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.ai.conversation.models import ConversationMessage
from app.core.conversation.conversation_state import ConversationState
from app.core.conversation.customer_intent import CustomerIntent


@dataclass
class ConversationContext:
    """Everything known about a single conversation at a point in time.

    ``ConversationContext`` is a plain data holder (no behavior) intended
    to become the single shared representation of conversation state
    across the platform. Rather than each component (``ConversationService``,
    the Decision Engine, ``MemoryService``, CRM integrations, Telephony)
    tracking its own partial view of a conversation, they are all meant
    to read from and write to one ``ConversationContext`` instance per
    session.

    Attributes:
        session_id: Unique identifier of the conversation session.
        current_state: The conversation's current ``ConversationState``
            (see ``conversation_state.py``).
        customer_intent: The customer's most recently classified
            ``CustomerIntent``, or ``None`` if it has not been
            classified yet.
        customer_name: The customer's name, or ``None`` if not yet known.
        company_name: The customer's company name, or ``None`` if not
            yet known or not applicable.
        phone: The customer's phone number, or ``None`` if not yet known.
        email: The customer's email address, or ``None`` if not yet
            known.
        region: The customer's region, or ``None`` if not yet known.
        interest_level: The customer's estimated level of interest, on a
            scale from 0 (no interest) to 100 (fully interested).
        needs_human: Whether the conversation currently requires human
            intervention.
        summary: A short, human-readable summary of the conversation so
            far.
        history: The conversation's message history, in chronological
            order.
    """

    session_id: str
    current_state: ConversationState = ConversationState.GREETING
    customer_intent: CustomerIntent | None = None
    customer_name: str | None = None
    company_name: str | None = None
    phone: str | None = None
    email: str | None = None
    region: str | None = None
    interest_level: int = 0
    needs_human: bool = False
    summary: str = ""
    history: list[ConversationMessage] = field(default_factory=list)
