"""Customer intent detection.

This module defines ``IntentDetector``, the abstract interface for
classifying a customer's message into a ``CustomerIntent``, and
``RuleBasedIntentDetector``, a simple keyword/rule-based implementation
that does not call any AI provider.

Note: this module reuses the existing ``CustomerIntent`` enum from
``customer_intent.py`` rather than defining a new one, so that there is
exactly one ``CustomerIntent`` type shared by ``ConversationContext`` and
every intent detector implementation (rule-based today, AI-based later).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.conversation.context import ConversationContext
from app.core.conversation.customer_intent import CustomerIntent


class IntentDetector(ABC):
    """Abstract interface for classifying a customer message's intent.

    Any component that wants to classify customer messages into a
    ``CustomerIntent`` (whether by keyword rules today, or by an AI model
    later) must implement this interface. Consumers should depend only
    on this abstraction, not on a specific detection strategy, so
    detectors can be swapped without changing calling code.
    """

    @abstractmethod
    def detect(self, message: str, context: ConversationContext) -> CustomerIntent:
        """Classify a customer message into a ``CustomerIntent``.

        Args:
            message: The customer's message text to classify.
            context: The conversation's current ``ConversationContext``.
                Implementations may use it (e.g. current state, prior
                intent) to inform classification, or ignore it entirely.

        Returns:
            The classified ``CustomerIntent``.
        """
        raise NotImplementedError()


class RuleBasedIntentDetector(IntentDetector):
    """Keyword/rule-based ``CustomerIntent`` classifier.

    This implementation does not call OpenAI or any other AI provider —
    it classifies a message by checking, in a fixed priority order,
    whether it contains any keyword associated with a given intent. The
    first matching rule wins; if no rule matches, the intent is
    classified as ``CustomerIntent.UNKNOWN``.

    Rule order matters: some intents' keywords could otherwise overlap
    (e.g. a refusal like "не интересно" contains the word "интересно",
    which would otherwise also match the interest rule), so refusal is
    checked before interest. The ``context`` parameter is accepted for
    interface compatibility but is not used by this simple
    implementation; it exists so that future, more advanced detectors
    (e.g. AI-based ones) can use conversation context without requiring
    a different interface.
    """

    _REFUSAL_KEYWORDS: tuple[str, ...] = (
        "не интерес",
        "неинтерес",
        "не нужно",
        "не надо",
    )
    _GREETING_KEYWORDS: tuple[str, ...] = (
        "здравствуйте",
        "добрый день",
        "добрый вечер",
        "доброе утро",
        "привет",
    )
    _GOODBYE_KEYWORDS: tuple[str, ...] = (
        "до свидания",
        "всего доброго",
        "пока",
    )
    _REQUEST_HUMAN_KEYWORDS: tuple[str, ...] = (
        "менеджер",
        "руководител",
        "человек",
        "оператор",
    )
    _REQUEST_PRICE_KEYWORDS: tuple[str, ...] = (
        "цена",
        "цену",
        "цене",
        "ценой",
        "стоимост",
        "прайс",
        "сколько стоит",
    )
    _REQUEST_MATERIALS_KEYWORDS: tuple[str, ...] = (
        "каталог",
        "презентаци",
        "материал",
        "информаци",
    )
    _OBJECTION_KEYWORDS: tuple[str, ...] = (
        "дорого",
        "не подходит",
        "сомнева",
    )
    _INTEREST_KEYWORDS: tuple[str, ...] = (
        "интерес",
        "хочу узнать",
        "расскажите подробнее",
    )

    def detect(self, message: str, context: ConversationContext) -> CustomerIntent:
        """Classify ``message`` using keyword rules.

        Args:
            message: The customer's message text to classify.
            context: The conversation's current ``ConversationContext``.
                Not used by this implementation.

        Returns:
            The first matching ``CustomerIntent``, checked in priority
            order (refusal, greeting, goodbye, request-human,
            request-price, request-materials, objection, interest,
            question), or ``CustomerIntent.UNKNOWN`` if nothing matches
            and the message contains no keywords or question mark.
        """
        normalized_message = message.strip().lower()

        if not normalized_message:
            return CustomerIntent.UNKNOWN

        if self._contains_any(normalized_message, self._REFUSAL_KEYWORDS):
            return CustomerIntent.REFUSAL
        if self._contains_any(normalized_message, self._GREETING_KEYWORDS):
            return CustomerIntent.GREETING
        if self._contains_any(normalized_message, self._GOODBYE_KEYWORDS):
            return CustomerIntent.GOODBYE
        if self._contains_any(normalized_message, self._REQUEST_HUMAN_KEYWORDS):
            return CustomerIntent.REQUEST_HUMAN
        if self._contains_any(normalized_message, self._REQUEST_PRICE_KEYWORDS):
            return CustomerIntent.REQUEST_PRICE
        if self._contains_any(normalized_message, self._REQUEST_MATERIALS_KEYWORDS):
            return CustomerIntent.REQUEST_MATERIALS
        if self._contains_any(normalized_message, self._OBJECTION_KEYWORDS):
            return CustomerIntent.OBJECTION
        if self._contains_any(normalized_message, self._INTEREST_KEYWORDS):
            return CustomerIntent.INTEREST
        if "?" in normalized_message:
            return CustomerIntent.QUESTION

        return CustomerIntent.UNKNOWN

    @staticmethod
    def _contains_any(normalized_message: str, keywords: tuple[str, ...]) -> bool:
        """Check whether any of ``keywords`` appears in ``normalized_message``.

        Args:
            normalized_message: The already-lowercased, stripped message.
            keywords: The keywords to look for.

        Returns:
            ``True`` if at least one keyword is a substring of the
            message, ``False`` otherwise.
        """
        return any(keyword in normalized_message for keyword in keywords)
