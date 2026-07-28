"""Conversation state machine.

This module defines ``StateMachine``, which tracks the current
``ConversationState`` of a single conversation and enforces which
transitions between states are allowed. It contains no AI, no HTTP, and
no CRM logic — it is a pure, framework-free core component responsible
solely for state and transition rules.

In addition to the regular, per-state transition table, this module
enforces one cross-cutting rule: escalation is a universal interrupt
state available from any active conversation state. A transition to
``ConversationState.ESCALATION`` is allowed from any current state
except ``ConversationState.FINISHED``, regardless of the regular
transition table.
"""

from __future__ import annotations

from app.core.conversation.conversation_state import ConversationState


class InvalidStateTransitionError(Exception):
    """Raised when an attempted conversation state transition is not allowed.

    This is the only exception ``StateMachine`` raises for transition
    errors, so callers never need to know about or catch any other
    exception type when calling ``transition_to``.
    """


class StateMachine:
    """Tracks a conversation's current state and enforces valid transitions.

    ``StateMachine`` holds no AI logic: it only knows the fixed set of
    allowed transitions between ``ConversationState`` values and enforces
    them. Each instance owns its own current state — there is no global
    or singleton state, so multiple independent conversations can each
    have their own ``StateMachine`` instance without interfering with
    one another.

    Regular (non-escalation) transitions (source -> targets):
        GREETING -> QUALIFICATION
        QUALIFICATION -> NEED_DISCOVERY
        NEED_DISCOVERY -> PRESENTATION
        PRESENTATION -> OBJECTION, AGREEMENT
        OBJECTION -> PRESENTATION
        AGREEMENT -> FINISHED

    Escalation is a universal interrupt state available from any active
    conversation state: regardless of the table above, a transition to
    ``ESCALATION`` is always allowed as long as the conversation is not
    already ``FINISHED``. This is enforced as a separate rule (see
    ``can_transition``), layered on top of — not merged into — the
    regular transition table, so the table itself never needs to list
    ``ESCALATION`` as a target for every source state.

    ``ESCALATION`` and ``FINISHED`` remain terminal with respect to the
    regular transition table: no outgoing *regular* transitions are
    defined for them. ``FINISHED`` is also excluded from the universal
    escalation rule, since a finished conversation cannot be escalated.
    """

    _ALLOWED_TRANSITIONS: dict[ConversationState, frozenset[ConversationState]] = {
        ConversationState.GREETING: frozenset({ConversationState.QUALIFICATION}),
        ConversationState.QUALIFICATION: frozenset({ConversationState.NEED_DISCOVERY}),
        ConversationState.NEED_DISCOVERY: frozenset({ConversationState.PRESENTATION}),
        ConversationState.PRESENTATION: frozenset(
            {ConversationState.OBJECTION, ConversationState.AGREEMENT}
        ),
        ConversationState.OBJECTION: frozenset({ConversationState.PRESENTATION}),
        ConversationState.AGREEMENT: frozenset({ConversationState.FINISHED}),
        ConversationState.ESCALATION: frozenset(),
        ConversationState.FINISHED: frozenset(),
    }

    def __init__(self, initial_state: ConversationState = ConversationState.GREETING) -> None:
        """Initialize the state machine.

        Args:
            initial_state: The state the conversation starts in, and the
                state ``reset()`` will return it to. Defaults to
                ``ConversationState.GREETING``.
        """
        self._initial_state = initial_state
        self._current_state = initial_state

    def current_state(self) -> ConversationState:
        """Return the conversation's current state.

        Returns:
            The current ``ConversationState``.
        """
        return self._current_state

    def can_transition(self, target_state: ConversationState) -> bool:
        """Check whether a transition to ``target_state`` is currently allowed.

        Two independent rules are checked, in order:

        1. The universal escalation rule: escalation is a universal
           interrupt state available from any active conversation
           state, so a transition to ``ESCALATION`` is allowed from any
           current state except ``FINISHED``.
        2. The regular transition table, for every other target state.

        Args:
            target_state: The state to check a potential transition to.

        Returns:
            ``True`` if moving from the current state to ``target_state``
            is an allowed transition, ``False`` otherwise.
        """
        if target_state is ConversationState.ESCALATION:
            return self._current_state is not ConversationState.FINISHED

        allowed_targets = self._ALLOWED_TRANSITIONS.get(self._current_state, frozenset())
        return target_state in allowed_targets

    def transition_to(self, target_state: ConversationState) -> ConversationState:
        """Move the conversation to ``target_state``, if allowed.

        Args:
            target_state: The state to transition to.

        Returns:
            The new current state (equal to ``target_state``) after a
            successful transition.

        Raises:
            InvalidStateTransitionError: If moving from the current state
                to ``target_state`` is not an allowed transition.
        """
        if not self.can_transition(target_state):
            raise InvalidStateTransitionError(
                f"Cannot transition from {self._current_state.name} "
                f"to {target_state.name}."
            )
        self._current_state = target_state
        return self._current_state

    def reset(self) -> ConversationState:
        """Reset the conversation back to its initial state.

        Returns:
            The initial ``ConversationState`` the machine was constructed
            with.
        """
        self._current_state = self._initial_state
        return self._current_state
