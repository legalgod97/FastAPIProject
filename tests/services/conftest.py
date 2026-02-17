import uuid
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def session():
    return MagicMock()

@pytest.fixture
def id():
    return uuid.uuid4()