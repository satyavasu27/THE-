"""Non-destructive dataset audit helpers; no row synthesis or silent cleaning."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


def sha256(path: str | Path, block_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            h.update(block)
    return h.hexdigest()


def audit_frame(
    df: pd.DataFrame,
    target: str,
    patient_id: str | None = None,
    record_id: str | None = None,
) -> dict[str, Any]:
    if target not in df:
        raise KeyError(f"Target column {target!r} not found")
    valid = df.loc[df[target].notna()].copy()
    exact_dups = int(df.duplicated().sum())
    valid = valid.drop_duplicates()
    valid_after_dedup = len(valid)
    result: dict[str, Any] = {
        "original_rows": int(len(df)),
        "columns": int(df.shape[1]),
        "column_names": [str(c) for c in df.columns],
        "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
        "missing_by_column": {str(k): int(v) for k, v in df.isna().sum().items()},
        "missing_target": int(df[target].isna().sum()),
        "exact_duplicate_rows": exact_dups,
        "target_counts_including_na": {
            str(k): int(v) for k, v in df[target].value_counts(dropna=False).items()
        },
        "valid_target_rows_before_dedup": int(df[target].notna().sum()),
        "valid_target_rows_after_exact_dedup": int(valid_after_dedup),
        "target_counts_after_exact_dedup": {
            str(k): int(v) for k, v in valid[target].value_counts(dropna=False).items()
        },
        "minimum_rows_required": 2000,
    }
    if record_id and record_id in df:
        # Duplicate keys indicate repeated analytic records only if the source says this
        # key defines one observation. Conflicting targets are highlighted, never resolved silently.
        valid_key = valid[record_id].notna()
        duplicate_key_rows = valid.loc[valid_key, record_id].duplicated(keep=False)
        result["record_id_column"] = record_id
        result["unique_nonmissing_record_ids"] = int(valid.loc[valid_key, record_id].nunique())
        result["rows_with_missing_record_id"] = int(valid[record_id].isna().sum())
        result["rows_on_repeated_record_ids"] = int(duplicate_key_rows.sum())
        target_nunique = valid.loc[valid_key].groupby(record_id, dropna=True)[target].nunique()
        result["record_ids_with_conflicting_targets"] = int((target_nunique > 1).sum())
        # Count one source record per record ID only to compute a conservative row gate.
        # Conflicts remain flagged and must be investigated before model use.
        result["valid_record_units_after_record_id_dedup"] = int(
            valid.loc[valid_key, record_id].nunique() + valid[record_id].isna().sum()
        )
        gate_count = result["valid_record_units_after_record_id_dedup"]
    else:
        gate_count = valid_after_dedup
    result["valid_unique_records_for_size_gate"] = int(gate_count)
    result["size_gate_passed"] = bool(gate_count >= 2000)
    if patient_id and patient_id in df:
        result["patient_id_column"] = patient_id
        result["unique_nonmissing_patients"] = int(df[patient_id].nunique(dropna=True))
        result["rows_with_missing_patient_id"] = int(df[patient_id].isna().sum())
        result["patients_with_repeated_rows"] = int(
            (df[patient_id].value_counts(dropna=True) > 1).sum()
        )
    return result


def write_audit(
    path: str | Path,
    target: str,
    out: str | Path,
    patient_id: str | None = None,
    record_id: str | None = None,
) -> dict[str, Any]:
    path = Path(path)
    if path.suffix.lower() in {".parquet", ".pq"}:
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path, low_memory=False)
    result = audit_frame(df, target=target, patient_id=patient_id, record_id=record_id)
    result["file"] = str(path)
    result["sha256"] = sha256(path)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result
