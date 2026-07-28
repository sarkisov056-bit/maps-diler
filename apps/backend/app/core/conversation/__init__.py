"""Conversation state core package.

Contains the platform-agnostic building blocks for tracking where a
conversation stands: the ``ConversationState`` enum and the
``StateMachine`` that enforces which state transitions are allowed.

This package has no dependency on FastAPI, HTTP, OpenAI, or CRM
integrations — it is a pure, framework-free core component.
"""
