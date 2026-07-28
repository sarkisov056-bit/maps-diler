"""Conversation state definitions.

This module defines ``ConversationState``, the fixed set of states a
conversation can be in, as described in ``docs/core/decision_engine.md``.
It contains no behavior — only the enumeration itself. Enforcing which
transitions between states are allowed is the responsibility of
``StateMachine`` (see ``state_machine.py``).
"""

from __future__ import annotations

from enum import Enum


class ConversationState(Enum):
    """The possible states of a single conversation.

    These states mirror the "Conversation States" section of the
    Decision Engine architecture document. Each member represents a
    distinct stage a conversation can be in; ``StateMachine`` is
    responsible for deciding which transitions between them are valid.

    Members:
        GREETING: The conversation has just started; initial greeting.
        QUALIFICATION: Determining who the customer is and whether they
            fit the intended scenario.
        NEED_DISCOVERY: Uncovering the customer's underlying need.
        PRESENTATION: Presenting the product/solution to the customer.
        OBJECTION: Handling a customer objection.
        AGREEMENT: The customer has expressed agreement/readiness to
            proceed.
        ESCALATION: The conversation has been handed off to a human.
        FINISHED: The conversation has ended.
    """

    GREETING = "greeting"
    QUALIFICATION = "qualification"
    NEED_DISCOVERY = "need_discovery"
    PRESENTATION = "presentation"
    OBJECTION = "objection"
    AGREEMENT = "agreement"
    ESCALATION = "escalation"
    FINISHED = "finished"
