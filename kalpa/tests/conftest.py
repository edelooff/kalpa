import pytest

from . base import Root


@pytest.fixture
def root():
    """Returns an instantiated root node."""
    return Root('mock_request')
