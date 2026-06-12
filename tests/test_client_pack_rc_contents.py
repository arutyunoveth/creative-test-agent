async def test_client_pack_includes_release_docs():
    from scripts.build_client_pilot_pack import SOURCE_DIRS, SOURCE_FILES
    dirs_joined = " ".join(SOURCE_DIRS.keys())
    files_joined = " ".join(SOURCE_FILES)
    assert "docs/releases" in dirs_joined or "docs/releases" in files_joined
    assert "docs/deployment" in dirs_joined or "docs/deployment" in files_joined
    assert "scripts/build_release_manifest.py" in files_joined
    assert "scripts/run_pilot_smoke.py" in files_joined
    assert "scripts/verify_release_install.py" in files_joined
