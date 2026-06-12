import os


def test_first_server_install_docs_exist():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "deployment", "first_server_install_ru.md")
    assert os.path.isfile(path), "First server install docs not found"
