"""Unit tests for ``RuleBasedIntentDetector``.

Covers each supported intent with at least one representative message,
plus edge cases: case-insensitivity, empty input, and the priority rule
that resolves overlapping keywords (e.g. "не интересно" containing the
substring "интересно").
"""

from __future__ import annotations

import pytest

from app.core.conversation.context import ConversationContext
from app.core.conversation.customer_intent import CustomerIntent
from app.core.conversation.intent_detector import RuleBasedIntentDetector


@pytest.fixture
def detector() -> RuleBasedIntentDetector:
    """A fresh ``RuleBasedIntentDetector`` for each test."""
    return RuleBasedIntentDetector()


@pytest.fixture
def context() -> ConversationContext:
    """A minimal ``ConversationContext``; the rule-based detector ignores it."""
    return ConversationContext(session_id="test-session")


@pytest.mark.parametrize(
    ("message", "expected_intent"),
    [
        ("Здравствуйте!", CustomerIntent.GREETING),
        ("Добрый день", CustomerIntent.GREETING),
        ("Сколько стоит ваш фильтр?", CustomerIntent.REQUEST_PRICE),
        ("Какая цена на комплект?", CustomerIntent.REQUEST_PRICE),
        ("Пришлите, пожалуйста, каталог", CustomerIntent.REQUEST_MATERIALS),
        ("Можно презентацию посмотреть?", CustomerIntent.REQUEST_MATERIALS),
        ("Соедините меня с менеджером", CustomerIntent.REQUEST_HUMAN),
        ("Хочу поговорить с человеком", CustomerIntent.REQUEST_HUMAN),
        ("Мне не интересно", CustomerIntent.REFUSAL),
        ("Не нужно, спасибо", CustomerIntent.REFUSAL),
        ("Это слишком дорого для нас", CustomerIntent.OBJECTION),
        ("Мне это интересно, расскажите подробнее", CustomerIntent.INTEREST),
        ("До свидания", CustomerIntent.GOODBYE),
        ("Всего доброго", CustomerIntent.GOODBYE),
        ("А как это работает?", CustomerIntent.QUESTION),
        ("Случайный текст без ключевых слов", CustomerIntent.UNKNOWN),
    ],
)
def test_detect_returns_expected_intent(
    detector: RuleBasedIntentDetector,
    context: ConversationContext,
    message: str,
    expected_intent: CustomerIntent,
) -> None:
    """Each representative message should map to its expected intent."""
    assert detector.detect(message, context) == expected_intent


def test_detect_is_case_insensitive(
    detector: RuleBasedIntentDetector, context: ConversationContext
) -> None:
    """Matching should not depend on letter case."""
    assert detector.detect("ЗДРАВСТВУЙТЕ", context) == CustomerIntent.GREETING
    assert detector.detect("СКОЛЬКО СТОИТ", context) == CustomerIntent.REQUEST_PRICE


def test_detect_empty_message_is_unknown(
    detector: RuleBasedIntentDetector, context: ConversationContext
) -> None:
    """An empty or whitespace-only message should be classified as UNKNOWN."""
    assert detector.detect("", context) == CustomerIntent.UNKNOWN
    assert detector.detect("   ", context) == CustomerIntent.UNKNOWN


def test_refusal_takes_priority_over_interest_keyword_overlap(
    detector: RuleBasedIntentDetector, context: ConversationContext
) -> None:
    """"не интересно" contains the substring "интересно" (interest), but
    must still resolve to REFUSAL, not INTEREST.
    """
    assert detector.detect("Спасибо, не интересно", context) == CustomerIntent.REFUSAL


def test_request_human_takes_priority_over_question_mark(
    detector: RuleBasedIntentDetector, context: ConversationContext
) -> None:
    """A message that both asks a question and requests a human should
    resolve to REQUEST_HUMAN, since that rule is checked earlier.
    """
    assert (
        detector.detect("Можно позвать менеджера?", context)
        == CustomerIntent.REQUEST_HUMAN
    )
