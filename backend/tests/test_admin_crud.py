"""
backend/tests/test_admin_crud.py
Integration tests for all 7 admin bug fixes.
Run with: backend/venv/bin/python backend/tests/test_admin_crud.py
"""
import sys, os, json, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from app.services import content_service

PAIR_ID = "fr-en"
BASE_DATA = Path("backend/data/languages")
PAIRS_JSON = Path("backend/data/language_pairs.json")

def cleanup():
    """Remove test pair and restore state."""
    if (BASE_DATA / "fr" / "en").exists():
        shutil.rmtree(BASE_DATA / "fr" / "en")
    if (BASE_DATA / "fr").exists() and not any((BASE_DATA / "fr").iterdir()):
        (BASE_DATA / "fr").rmdir()
    pairs = content_service.get_all_pairs()
    pairs = [p for p in pairs if p["pairId"] != PAIR_ID]
    with open(PAIRS_JSON, "w", encoding="utf-8") as f:
        json.dump(pairs, f, indent=2)

PASS = "✅ PASS"
FAIL = "❌ FAIL"

def test_create_pair_creates_all_json_files():
    """Bug 2: create_pair_directory should physically write all 8 activity JSON files."""
    cleanup()
    content_service.create_pair_directory(
        PAIR_ID, src_id="fr", tgt_id="en",
        src_name="French", tgt_name="English",
        src_flag="🇫🇷", tgt_flag="🇺🇸", total_months=1
    )
    # Check M1B1_lesson.json exists
    for b in range(1, 7):
        for act_type in content_service.ACTIVITY_TYPES:
            path = BASE_DATA / "fr" / "en" / "month_1" / f"block_{b}" / f"M1B{b}_{act_type}.json"
            if not path.exists():
                print(f"{FAIL} test_create_pair_creates_all_json_files — missing: {path}")
                return False
    print(f"{PASS} test_create_pair_creates_all_json_files — all 48 activity files created")
    return True


def test_add_month_creates_json_files():
    """Bug 2: add_month should write activity files for all 6 blocks in the new month."""
    # Ensure pair exists with meta
    meta = content_service._build_meta_skeleton(
        PAIR_ID, src_id="fr", tgt_id="en",
        src_name="French", tgt_name="English",
        src_flag="🇫🇷", tgt_flag="🇺🇸",
        total_months=1, blocks_per_month=6
    )
    content_service.write_meta(PAIR_ID, meta)
    content_service.add_month(PAIR_ID)
    # Month 2 should now have all files
    for b in range(1, 7):
        for act_type in content_service.ACTIVITY_TYPES:
            path = BASE_DATA / "fr" / "en" / "month_2" / f"block_{b}" / f"M2B{b}_{act_type}.json"
            if not path.exists():
                print(f"{FAIL} test_add_month_creates_json_files — missing: {path}")
                return False
    print(f"{PASS} test_add_month_creates_json_files — all 48 files created in month_2")
    return True


def test_add_block_creates_json_files():
    """Bug 2: add_block should write 8 activity JSON files for the new block."""
    content_service.add_block(PAIR_ID, 1)
    meta = content_service.get_meta(PAIR_ID)
    month1 = next(m for m in meta["months"] if m["month"] == 1)
    new_block_num = max(b["block"] for b in month1["blocks"])
    for act_type in content_service.ACTIVITY_TYPES:
        path = BASE_DATA / "fr" / "en" / "month_1" / f"block_{new_block_num}" / f"M1B{new_block_num}_{act_type}.json"
        if not path.exists():
            print(f"{FAIL} test_add_block_creates_json_files — missing: {path}")
            return False
    print(f"{PASS} test_add_block_creates_json_files — all 8 files created for block_{new_block_num}")
    return True


def test_meta_filenames_use_correct_prefix():
    """Bug 2: meta.json should reference M{m}B{b}_{type}.json not plain {type}.json."""
    meta = content_service.get_meta(PAIR_ID)
    for month in meta["months"]:
        m = month["month"]
        for block in month["blocks"]:
            b = block["block"]
            for act in block["activities"]:
                expected_prefix = f"M{m}B{b}_"
                filename = act["file"].split("/")[-1]
                if not filename.startswith(expected_prefix):
                    print(f"{FAIL} test_meta_filenames_use_correct_prefix — bad filename: {act['file']}")
                    return False
    print(f"{PASS} test_meta_filenames_use_correct_prefix — all meta paths use M{{m}}B{{b}}_{{type}}.json")
    return True


def test_backend_pairs_api_returns_new_pair():
    """Bug 3: After registration, the pair must appear in language_pairs.json (the public pairs API source)."""
    content_service.register_pair(PAIR_ID, "fr", "en")
    pairs = content_service.get_all_pairs()
    found = any(p["pairId"] == PAIR_ID for p in pairs)
    if not found:
        print(f"{FAIL} test_backend_pairs_api_returns_new_pair — pair not in registry")
        return False
    print(f"{PASS} test_backend_pairs_api_returns_new_pair — pair '{PAIR_ID}' found in language_pairs.json")
    return True


def test_delete_pair_removes_source_folder_if_empty():
    """Bug 4: Deleting the only target pair for a source should also delete the source folder."""
    # The fr/ folder should only contain en/
    content_service.delete_pair(PAIR_ID)
    fr_dir = BASE_DATA / "fr"
    if fr_dir.exists():
        print(f"{FAIL} test_delete_pair_removes_source_folder_if_empty — fr/ dir still exists after deletion")
        return False
    print(f"{PASS} test_delete_pair_removes_source_folder_if_empty — fr/ parent dir correctly removed")
    return True


def test_delete_pair_keeps_source_if_other_targets_exist():
    """Bug 4: Deleting one target should NOT remove source folder if other targets remain."""
    # Create fr-en and fr-ja
    content_service.create_pair_directory("fr-en", src_id="fr", tgt_id="en", total_months=1)
    content_service.create_pair_directory("fr-ja", src_id="fr", tgt_id="ja", total_months=1)
    meta_en = content_service._build_meta_skeleton("fr-en", src_id="fr", tgt_id="en", src_name="French", tgt_name="English", src_flag="🇫🇷", tgt_flag="🇺🇸", total_months=1)
    meta_ja = content_service._build_meta_skeleton("fr-ja", src_id="fr", tgt_id="ja", src_name="French", tgt_name="Japanese", src_flag="🇫🇷", tgt_flag="🇯🇵", total_months=1)
    content_service.write_meta("fr-en", meta_en)
    content_service.write_meta("fr-ja", meta_ja)
    content_service.register_pair("fr-en", "fr", "en")
    content_service.register_pair("fr-ja", "fr", "ja")

    # Delete fr-en only
    content_service.delete_pair("fr-en")
    fr_dir = BASE_DATA / "fr"
    if not fr_dir.exists():
        print(f"{FAIL} test_delete_pair_keeps_source_if_other_targets_exist — fr/ removed even though fr-ja still exists!")
        # Cleanup leftover
        content_service.delete_pair("fr-ja")
        return False
    print(f"{PASS} test_delete_pair_keeps_source_if_other_targets_exist — fr/ preserved correctly")
    # Cleanup
    content_service.delete_pair("fr-ja")
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  LearnWise Admin CRUD Test Suite")
    print("="*60 + "\n")
    cleanup()
    results = [
        test_create_pair_creates_all_json_files(),
        test_add_month_creates_json_files(),
        test_add_block_creates_json_files(),
        test_meta_filenames_use_correct_prefix(),
        test_backend_pairs_api_returns_new_pair(),
        test_delete_pair_removes_source_folder_if_empty(),
        test_delete_pair_keeps_source_if_other_targets_exist(),
    ]
    cleanup()
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"  Results: {passed}/{total} tests passed")
    if passed == total:
        print("  🎉 ALL TESTS PASSED")
    else:
        print("  ⚠️  Some tests failed — check output above")
    print("="*60 + "\n")
    sys.exit(0 if passed == total else 1)
