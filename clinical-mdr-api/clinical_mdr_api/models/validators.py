"""Reusable pydantic validator functions"""

import re
from datetime import datetime, timezone
from typing import Any

from pydantic import ValidationInfo

from clinical_mdr_api.domains._utils import get_iso_lang_data
from clinical_mdr_api.domains.concepts.utils import EN_LANGUAGE, ENG_LANGUAGE
from common.exceptions import ValidationException

FLOAT_REGEX = "^[0-9]+\\.?[0-9]*$"


def validate_string_represents_boolean(value, info: ValidationInfo):
    """
    Validates whether a string value represents a boolean value.

    Args:
        cls: The class to which the field belongs.
        value: The value to validate.
        info: ValidationInfo

    Returns:
        str: The validated value.

    Raises:
        ValidationException: If the value does not represent a boolean value.
    """
    if not value:
        return "false"

    truthy = ("y", "yes", "t", "true", "on", "1")
    falsy = ("n", "no", "f", "false", "off", "0")

    ValidationException.raise_if(
        value.lower() not in (truthy + falsy),
        msg=f"Unsupported boolean value '{value}' for field '{info.field_name}'. Allowed values are: {truthy + falsy}.",
    )

    return value


def validate_name_only_contains_letters(value, info: ValidationInfo):
    """
    Validates whether a string value contains only letters.

    Args:
        cls: The class to which the field belongs.
        value: The value to validate.
        info: ValidationInfo

    Returns:
        str: The validated value.

    Raises:
        ValueError: If the value contains characters other than letters.
    """
    if re.search("[^a-zA-Z]", value):
        raise ValueError(
            f"Provided value '{value}' for '{info.field_name}' is invalid. Must only contain letters."
        )
    return value


def validate_regex(value, info: ValidationInfo):
    """
    Validates whether a string value is a valid regular expression.

    Args:
        cls: The class to which the field belongs.
        value: The value to validate.
        info: ValidationInfo

    Returns:
        str: The validated regular expression.

    Raises:
        ValueError: If the value is not a valid regular expression.
    """
    if value:
        try:
            re.compile(value)
            return value
        except re.error as exc:
            raise ValueError(
                f"Provided regex value '{value}' for field '{info.field_name}' is invalid."
            ) from exc
    return value


def transform_to_utc(value: datetime | None, info: ValidationInfo):
    if not value:
        return None

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    try:
        return value.astimezone(timezone.utc)
    except OverflowError as exc:
        raise ValueError(
            f"Provided value '{value}' for '{info.field_name}' is invalid. {exc}"
        ) from exc


def is_language_supported(value: str):
    if not value:
        return None

    keys = ["639-3", "639-2/B", "639-2/T", "639-1"]

    for key in keys:
        try:
            # This function will throw an exception if the language isn't found
            get_iso_lang_data(query=value, key=key, return_key=key)  # type: ignore[call-overload]
            return value
        except ValidationException:
            if key == keys[-1]:
                raise

    return None


def has_english_description(descriptions: list[Any]):
    """
    Ensures that at least one description is in English (`eng` or `en`).

    Args:
        descriptions (list[Any]): List of descriptions.

    Returns:
        list[Any]: The original list if valid.

    Raises:
        ValidationException: If no English description is found.
    """

    if not descriptions or any(
        desc.language in {ENG_LANGUAGE, EN_LANGUAGE} for desc in descriptions
    ):
        return descriptions

    raise ValidationException(
        msg="At least one description must be in English ('eng' or 'en')."
    )
