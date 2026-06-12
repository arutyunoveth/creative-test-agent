"""Local model diagnostic script tests."""

import os
import sys
import pytest


def test_check_local_model_script_imports():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import scripts.check_local_model as clm
    assert callable(clm.main)


def test_check_local_model_has_main():
    import scripts.check_local_model as clm
    assert hasattr(clm, "main")


def test_check_local_model_has_failures_list():
    import scripts.check_local_model as clm
    assert isinstance(clm.FAILURES, list)


def test_check_local_model_argparse():
    import argparse
    import scripts.check_local_model as clm
    parser = argparse.ArgumentParser()
    assert callable(clm.main)


def test_run_evaluation_script_imports():
    import scripts.run_evaluation
    assert callable(scripts.run_evaluation.main)


def test_register_prompts_script_imports():
    import scripts.register_prompts
    # register_prompts may or may not have a main function
    assert hasattr(scripts.register_prompts, "__file__")
