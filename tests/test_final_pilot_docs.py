import os


def test_product_overview_docs_exist():
    for path in [
        "docs/product_overview_ru.md",
        "docs/operator_guide_ru.md",
        "docs/final_pilot_checklist_ru.md",
    ]:
        full = os.path.join(os.path.dirname(os.path.dirname(__file__)), path)
        assert os.path.isfile(full), f"Missing: {path}"


def test_readme_links_new_docs():
    readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
    assert os.path.isfile(readme_path)
    with open(readme_path) as f:
        content = f.read()
    assert "product_overview_ru.md" in content or "Documentation" in content
