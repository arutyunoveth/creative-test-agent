import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_seed_script_imports():
    sys.path.insert(0, PROJECT_ROOT)
    try:
        from scripts.seed_demo_data import seed_demo_data
        assert callable(seed_demo_data)
    finally:
        sys.path.pop(0)


def test_demo_creative_files_exist():
    files = [
        "data/demo/sample_creative_variant_a.md",
        "data/demo/sample_creative_variant_b.md",
        "data/demo/sample_creative_variant_c.md",
    ]
    for f in files:
        full_path = os.path.join(PROJECT_ROOT, f)
        assert os.path.isfile(full_path), f"Missing demo file: {f}"


def test_demo_creative_variant_a_content():
    path = os.path.join(PROJECT_ROOT, "data/demo/sample_creative_variant_a.md")
    with open(path) as fh:
        content = fh.read()
    assert "NovaBank" in content
    assert "Practical" in content


def test_demo_creative_variant_b_content():
    path = os.path.join(PROJECT_ROOT, "data/demo/sample_creative_variant_b.md")
    with open(path) as fh:
        content = fh.read()
    assert "NovaBank" in content
    assert "Freedom" in content


def test_demo_creative_variant_c_has_risky_claims():
    path = os.path.join(PROJECT_ROOT, "data/demo/sample_creative_variant_c.md")
    with open(path) as fh:
        content = fh.read()
    assert "guarantees" in content.lower()
    assert "zero hassle" in content.lower()
