import os
import pytest
from _pytest.nodes import Node


@pytest.fixture
def testdatadir(request: Node) -> str:
    return os.path.join(request.fspath.dirname, "../test-data")