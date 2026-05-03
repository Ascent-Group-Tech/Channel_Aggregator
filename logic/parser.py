from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


_CURRENCY_BY_EMOJI = {
    "💲": "USD",
    "💵": "USD",
    "₴": "UAH",
}

# Emoji + number. Number may contain spaces and decimal separator "." or ",".
_PRICE_PATTERN = re.compile(
    r"(?P<emoji>💲|💵|₴)\s*(?P<number>\d(?:[\d\s]*\d)?(?:[.,]\d+)?)"
)

# Unsupported "range" format after a found price, e.g. "💲100-200" / "₴ 100 – 200".
_RANGE_AFTER_PRICE_PATTERN = re.compile(r"^\s*[-–—]\s*\d")


@dataclass(frozen=True)
class ParsedMessage:
    is_product: bool
    price: Optional[float]
    currency: Optional[str]
    final_price: Optional[float]
    original_substring: Optional[str] = None  # Точний збіг, напр. "₴ 100"
    emoji: Optional[str] = None


def parse_message(
    text: str,
    min_length: int = 1,
    markup_percent: float = 15.0,
) -> ParsedMessage:
    """
    Parse message text and extract product pricing info.

    Rules:
    - price format: currency emoji + number
    - supported emojis: 💲, 💵 (USD), ₴ (UAH)
    - number may include spaces and decimal separator "." or ","
    - message is a product when a valid single price is found and text length > min_length
    - final_price = price with markup, rounded to 2 decimals
    """
    if not isinstance(text, str):
        text = str(text)

    matches = list(_PRICE_PATTERN.finditer(text))

    # Unsupported / ambiguous cases: no price or multiple prices.
    if len(matches) != 1:
        return ParsedMessage(
            is_product=False,
            price=None,
            currency=None,
            final_price=None,
        )

    match = matches[0]

    # Reject unsupported range format right after the first number.
    if _RANGE_AFTER_PRICE_PATTERN.match(text[match.end() :]):
        return ParsedMessage(
            is_product=False,
            price=None,
            currency=None,
            final_price=None,
        )

    raw_number = match.group("number").replace(" ", "").replace(",", ".")
    emoji = match.group("emoji")

    try:
        price = float(raw_number)
    except ValueError:
        return ParsedMessage(
            is_product=False,
            price=None,
            currency=None,
            final_price=None,
        )

    if price <= 0:
        return ParsedMessage(
            is_product=False,
            price=None,
            currency=None,
            final_price=None,
        )

    is_product = len(text) > min_length
    if not is_product:
        return ParsedMessage(
            is_product=False,
            price=None,
            currency=None,
            final_price=None,
        )

    final_price = round(price * (1 + markup_percent / 100.0), 2)

    return ParsedMessage(
        is_product=True,
        price=price,
        currency=_CURRENCY_BY_EMOJI[emoji],
        final_price=final_price,
        original_substring=match.group(0),
        emoji=emoji
    )
def updated_message(parsed: ParsedMessage, text: str) -> str:
    
    final_p = int(parsed.final_price) if parsed.final_price.is_integer() else parsed.final_price

    new_price_str = f"{parsed.emoji} {final_p}"
    new_caption = text.replace(parsed.original_substring, new_price_str)

    return new_caption
