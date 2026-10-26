"""Einfache Tests mit pytest (siehe https://awesome-python.com/#testing)."""

import pytest


@pytest.mark.simple
def test_simple() -> None:
    # pylint: disable-next=comparison-of-constants, comparison-with-itself
    assert True  # NOSONAR


# https://docs.pytest.org/en/stable/how-to/skipping.html
@pytest.mark.skip(reason="Fail")
def test_always_fail() -> None:
    assert not True  # pylint: disable=comparison-of-constants
