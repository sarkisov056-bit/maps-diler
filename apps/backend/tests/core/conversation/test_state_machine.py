"""Unit tests for ``StateMachine``.

Covers the regular per-state transition table and the universal
escalation rule: escalation is a universal interrupt state available
from any active conversation state, except when the conversation has
already finished.
"""

from __future__ import annotations

import pytest

from app.core.conversation.conversation_state import ConversationState
from app.core.conversation.state_machine import InvalidStateTransitionError, StateMachine


def test_default_initial_state_is_greeting() -> None:
    """A freshly constructed machine starts in GREETING by default."""
    state_machine = StateMachine()

    assert state_machine.current_state() == ConversationState.GREETING


def test_regular_transition_path_greeting_to_presentation() -> None:
    """The regular happy-path transitions should still work as before."""
    state_machine = StateMachine()

    state_machine.transition_to(ConversationState.QUALIFICATION)
    state_machine.transition_to(ConversationState.NEED_DISCOVERY)
    state_machine.transition_to(ConversationState.PRESENTATION)

    assert state_machine.current_state() == ConversationState.PRESENTATION


def test_objection_and_agreement_branches_from_presentation() -> None:
    """PRESENTATION can branch to OBJECTION (and back) or to AGREEMENT."""
    state_machine = StateMachine(initial_state=ConversationState.PRESENTATION)

    assert state_machine.can_transition(ConversationState.OBJECTION) is True
    assert state_machine.can_transition(ConversationState.AGREEMENT) is True

    state_machine.transition_to(ConversationState.OBJECTION)
    state_machine.transition_to(ConversationState.PRESENTATION)
    state_machine.transition_to(ConversationState.AGREEMENT)
    state_machine.transition_to(ConversationState.FINISHED)

    assert state_machine.current_state() == ConversationState.FINISHED


def test_invalid_regular_transition_raises() -> None:
    """An out-of-order transition should still raise, as before."""
    state_machine = StateMachine()  # starts in GREETING

    assert state_machine.can_transition(ConversationState.PRESENTATION) is False
    with pytest.raises(InvalidStateTransitionError):
        state_machine.transition_to(ConversationState.PRESENTATION)


@pytest.mark.parametrize(
    "source_state",
    [
        ConversationState.GREETING,
        ConversationState.QUALIFICATION,
        ConversationState.NEED_DISCOVERY,
        ConversationState.PRESENTATION,
        ConversationState.OBJECTION,
        ConversationState.AGREEMENT,
    ],
)
def test_escalation_allowed_from_any_active_state(source_state: ConversationState) -> None:
    """Escalation should be reachable from every non-finished state."""
    state_machine = StateMachine(initial_state=source_state)

    assert state_machine.can_transition(ConversationState.ESCALATION) is True

    state_machine.transition_to(ConversationState.ESCALATION)

    assert state_machine.current_state() == ConversationState.ESCALATION


def test_greeting_to_escalation() -> None:
    """Explicit check: GREETING -> ESCALATION is allowed."""
    state_machine = StateMachine(initial_state=ConversationState.GREETING)

    state_machine.transition_to(ConversationState.ESCALATION)

    assert state_machine.current_state() == ConversationState.ESCALATION


def test_qualification_to_escalation() -> None:
    """Explicit check: QUALIFICATION -> ESCALATION is allowed."""
    state_machine = StateMachine(initial_state=ConversationState.QUALIFICATION)

    state_machine.transition_to(ConversationState.ESCALATION)

    assert state_machine.current_state() == ConversationState.ESCALATION


def test_presentation_to_escalation() -> None:
    """Explicit check: PRESENTATION -> ESCALATION is allowed."""
    state_machine = StateMachine(initial_state=ConversationState.PRESENTATION)

    state_machine.transition_to(ConversationState.ESCALATION)

    assert state_machine.current_state() == ConversationState.ESCALATION


def test_objection_to_escalation() -> None:
    """Explicit check: OBJECTION -> ESCALATION is allowed."""
    state_machine = StateMachine(initial_state=ConversationState.OBJECTION)

    state_machine.transition_to(ConversationState.ESCALATION)

    assert state_machine.current_state() == ConversationState.ESCALATION


def test_finished_to_escalation_is_forbidden() -> None:
    """FINISHED -> ESCALATION must be forbidden: a finished conversation
    cannot be escalated.
    """
    state_machine = StateMachine(initial_state=ConversationState.FINISHED)

    assert state_machine.can_transition(ConversationState.ESCALATION) is False
    with pytest.raises(InvalidStateTransitionError):
        state_machine.transition_to(ConversationState.ESCALATION)

    # The failed attempt must not have changed the current state.
    assert state_machine.current_state() == ConversationState.FINISHED


def test_escalation_itself_has_no_outgoing_transitions() -> None:
    """ESCALATION remains terminal with respect to the regular table."""
    state_machine = StateMachine(initial_state=ConversationState.ESCALATION)

    assert state_machine.can_transition(ConversationState.GREETING) is False
    with pytest.raises(InvalidStateTransitionError):
        state_machine.transition_to(ConversationState.GREETING)


def test_reset_returns_to_configured_initial_state() -> None:
    """reset() should restore the state the machine was constructed with,
    even after escalating.
    """
    state_machine = StateMachine(initial_state=ConversationState.QUALIFICATION)

    state_machine.transition_to(ConversationState.ESCALATION)
    assert state_machine.current_state() == ConversationState.ESCALATION

    state_machine.reset()

    assert state_machine.current_state() == ConversationState.QUALIFICATION
