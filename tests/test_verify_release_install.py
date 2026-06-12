async def test_verify_release_install_script_imports():
    from scripts.verify_release_install import run_checks, main
    assert callable(run_checks)
    assert callable(main)
