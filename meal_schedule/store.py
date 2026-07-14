"""検証済み献立を安全に保存し、期間で検索する。"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Iterable

from .models import ValidationError, validate_plan


class PlanStore:
    def __init__(self, data_dir: Path | str = "data/plans") -> None:
        self.data_dir = Path(data_dir)

    def path_for(self, plan: dict[str, Any]) -> Path:
        return self.data_dir / f"{plan['start_date']}.json"

    def save(
        self,
        plan: dict[str, Any],
        preferences: dict[str, Any] | None = None,
        *,
        overwrite: bool = False,
    ) -> Path:
        validate_plan(plan, preferences)
        destination = self.path_for(plan)
        if destination.exists() and not overwrite:
            raise ValidationError(f"既存の献立があります: {destination}（上書きには --overwrite）")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            "w", encoding="utf-8", dir=destination.parent, delete=False
        ) as temporary:
            json.dump(plan, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, destination)
        return destination

    def load_file(
        self, path: Path, preferences: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        try:
            with path.open(encoding="utf-8") as source:
                plan = json.load(source)
        except (OSError, json.JSONDecodeError) as error:
            raise ValidationError(f"献立を読み込めません: {path}: {error}") from error
        # preferences は後方互換のため受け取るが、過去の確定記録には適用しない。
        # 人数や禁止食材設定を変更しても、保存時点で有効だった履歴を参照可能にする。
        validate_plan(plan)
        return plan

    def iter_plans(
        self,
        start: date | None = None,
        end: date | None = None,
        preferences: dict[str, Any] | None = None,
    ) -> Iterable[dict[str, Any]]:
        if not self.data_dir.exists():
            return
        for path in sorted(self.data_dir.glob("*.json")):
            plan = self.load_file(path)
            plan_start = date.fromisoformat(plan["start_date"])
            plan_end = date.fromisoformat(plan["end_date"])
            if start is not None and plan_end < start:
                continue
            if end is not None and plan_start > end:
                continue
            yield plan


def dish_names(plans: Iterable[dict[str, Any]]) -> list[str]:
    return [
        dish["name"]
        for plan in plans
        for meal in plan["meals"]
        for dish in meal["dishes"]
    ]
