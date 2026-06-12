async def test_release_bundle_script_imports():
    from scripts.build_release_bundle import build_bundle, main
    assert callable(build_bundle)
    assert callable(main)


async def test_release_bundle_creates_output():
    import os, json, tempfile
    import sys
    from scripts.build_release_bundle import build_bundle
    # Temporarily override PROJECT_ROOT to a temp dir to test structure
    bundle_dir = build_bundle()
    assert os.path.isdir(bundle_dir), "Bundle directory not created"
    zip_path = f"{bundle_dir}.zip"
    assert os.path.isfile(zip_path), "Bundle zip not created"
    # Check bundle manifest
    manifest_path = os.path.join(bundle_dir, "bundle_manifest.json")
    assert os.path.isfile(manifest_path), "Bundle manifest not found"
    with open(manifest_path) as f:
        manifest = json.load(f)
    assert manifest["version"] == "0.1.0-rc1"
    assert manifest["local_only"] is True
