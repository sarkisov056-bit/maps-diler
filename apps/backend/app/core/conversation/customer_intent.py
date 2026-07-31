"""Customer intent definitions.

This module defines ``CustomerIntent``, the fixed set of intents a
customer's message can be classified as, as described in the "Customer
Intent" section of ``docs/core/decision_engine.md``. It contains no
behavior — only the enumeration itself. Classifying a message into one
of these intents is the responsibility of components built on top of
this enum (e.g. the future Decision Engine), not of this module.
"""

from __future__ import annotations

from enum import Enum


class CustomerIntent(Enum):
    """The possible intents behind a customer's message.

    These members mirror the "Customer Intent" section of the Decision
    Engine architecture document.

    Members:
        QUESTION: The customer is asking a question.
        INTEREST: The customer is expressing interest.
        OBJECTION: The customer is raising an objection.
        REFUSAL: The customer is refusing/declining.
        REQUEST_MATERIALS: The customer is asking for materials (e.g. a
            presentation or documents).
        REQUEST_PRICE: The customer is asking about price.
        REQUEST_HUMAN: The customer is asking to be connected to a human.
        UNKNOWN: The intent could not be determined.
    """

    QUESTION = "question"
    INTEREST = "interest"
    OBJECTION = "objection"
    REFUSAL = "refusal"
    REQUEST_MATERIALS = "request_materials"
    REQUEST_PRICE = "request_price"
    REQUEST_HUMAN = "request_human"
    UNKNOWN = "unknown"
