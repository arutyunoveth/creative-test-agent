import os


def test_creative_iterations_doc_exists():
    assert os.path.isfile("docs/creative_iterations.md")


def test_review_workflow_doc_exists():
    assert os.path.isfile("docs/review_workflow.md")


def test_human_feedback_learning_doc_exists():
    assert os.path.isfile("docs/human_feedback_learning.md")


def test_creative_iterations_doc_has_content():
    with open("docs/creative_iterations.md") as f:
        content = f.read()
    assert len(content) > 100
    assert "version" in content.lower()


def test_review_workflow_doc_has_content():
    with open("docs/review_workflow.md") as f:
        content = f.read()
    assert len(content) > 100
    assert "review" in content.lower()


def test_human_feedback_learning_doc_has_content():
    with open("docs/human_feedback_learning.md") as f:
        content = f.read()
    assert len(content) > 100
    assert "feedback" in content.lower()
