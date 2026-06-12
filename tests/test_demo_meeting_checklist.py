import os


def test_demo_meeting_checklist_exists():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "client_pilot", "demo_meeting_checklist_ru.md")
    assert os.path.isfile(path), "Demo meeting checklist not found"
