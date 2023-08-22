from pathlib import Path

# @pytest.fixture
# def testdatadir(request: Node) -> str:
#     return os.path.join(request.fspath.dirname, "../test-data")

TEST_DATA_DIR = Path(__file__).parent.parent.resolve() / 'test-data'