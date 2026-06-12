async def test_client_pack_builder_uses_source_dirs():
    from scripts.build_client_pilot_pack import SOURCE_DIRS, SOURCE_FILES
    assert isinstance(SOURCE_DIRS, dict)
    assert isinstance(SOURCE_FILES, list)
    assert len(SOURCE_DIRS) >= 1
    assert len(SOURCE_FILES) >= 3
