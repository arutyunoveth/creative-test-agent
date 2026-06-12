async def test_pilot_smoke_script_imports():
    from scripts.run_pilot_smoke import main
    assert callable(main)
