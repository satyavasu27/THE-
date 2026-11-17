import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_matrix import inspect_task


def test_matrix_has_all_six_method_dataset_slots_and_no_source_data_results():
    config = json.loads((ROOT / "configs/experiment_matrix.json").read_text())
    tasks = config["experiments"]
    assert len(tasks) == 6
    assert len({(t["dataset"], t["method"]) for t in tasks}) == 6
    statuses = [inspect_task(t, config)["status"] for t in tasks]
    # This checkout has no downloaded source datasets. A matrix dry-run must block, not fit.
    assert statuses == ["BLOCKED_DATA_FILE_MISSING"] * 6
