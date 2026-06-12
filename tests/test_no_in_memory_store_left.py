import re


def _find_pattern(filepath: str, pattern: str, label: str) -> list[str]:
    matches = []
    with open(filepath) as f:
        for i, line in enumerate(f, 1):
            if re.search(pattern, line):
                matches.append(f"  {filepath}:{i}: {line.rstrip()}")
    return matches


_KNOWN_EXCEPTIONS = {
    "src/shared/storage/local_storage.py",
    "src/modules/creative_assets/upload.py",
}


def test_no_in_memory_store_dicts():
    import pathlib

    src = pathlib.Path(__file__).resolve().parent.parent / "src"
    violations = []

    for pyfile in sorted(src.rglob("*.py")):
        rel = pyfile.relative_to(src.parent)

        # Only check files we know should be clean
        if str(rel) in _KNOWN_EXCEPTIONS:
            continue

        content = pyfile.read_text()
        if "_store = {" in content or "_store[" in content or "global _store" in content:
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if "_store =" in stripped and ("{" in stripped or "[" in stripped):
                    violations.append(f"  {rel}:{i}: {stripped}")
                elif "_store[" in stripped:
                    violations.append(f"  {rel}:{i}: {stripped}")
                elif "global _store" in stripped:
                    violations.append(f"  {rel}:{i}: {stripped}")

    assert not violations, (
        f"Found {len(violations)} in-memory _store pattern(s) in src/:\n"
        + "\n".join(violations)
        + "\n\nAll services must use db_session() from src/shared/db/repository.py."
    )


def test_no_store_dicts_in_tests():
    import pathlib

    tests = pathlib.Path(__file__).resolve().parent
    violations = []

    for pyfile in sorted(tests.rglob("test_*.py")):
        # Skip self-check — the test file defines the pattern as strings
        if pyfile.name == "test_no_in_memory_store_left.py":
            continue
        content = pyfile.read_text()
        rel = pyfile.relative_to(tests.parent)

        if "from src.modules." not in content:
            continue
        if "import _store" in content or "from.*import.*_store" in content:
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                if "_store" in line and ("import" in line or "from" in line):
                    violations.append(f"  {rel}:{i}: {line.rstrip()}")

    assert not violations, (
        f"Found {len(violations)} _store import(s) in tests/:\n"
        + "\n".join(violations)
        + "\n\nTests must not access in-memory stores directly."
    )
