"""Metric helpers for evaluating structured extraction outputs."""

from __future__ import annotations

from typing import Dict, Iterable, List


def set_prf1(pred: Iterable[str], gold: Iterable[str]) -> Dict[str, float]:
    """Compute precision, recall, and F1 over sets of strings."""

    pred_set = {item.strip().lower() for item in pred if item}
    gold_set = {item.strip().lower() for item in gold if item}

    tp = len(pred_set & gold_set)
    prec = tp / max(1, len(pred_set))
    rec = tp / max(1, len(gold_set))
    f1 = 0.0 if (prec + rec) == 0 else 2 * prec * rec / (prec + rec)
    return {"precision": prec, "recall": rec, "f1": f1}


def order_kendall_tau(pred: List[str], gold: List[str]) -> Dict[str, float]:
    """Kendall tau variant considering only shared items."""

    gold_positions = {item: idx for idx, item in enumerate(gold)}
    common = [item for item in pred if item in gold_positions]

    total_pairs = 0
    discordant = 0
    for i in range(len(common)):
        for j in range(i + 1, len(common)):
            total_pairs += 1
            if gold_positions[common[i]] > gold_positions[common[j]]:
                discordant += 1

    if total_pairs == 0:
        return {"kendall_tau": 0.0}
    tau = 1 - 2 * discordant / total_pairs
    return {"kendall_tau": tau}


def provenance_coverage(pred_events: List[Dict]) -> Dict[str, float]:
    """Portion of predicted events that include an explicit timestamp."""

    if not pred_events:
        return {"prov_coverage": 0.0}
    with_timestamp = sum(1 for evt in pred_events if evt.get("timestamp"))
    return {"prov_coverage": with_timestamp / len(pred_events)}
