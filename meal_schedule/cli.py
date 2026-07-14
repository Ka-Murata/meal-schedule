"""献立履歴を扱うコマンドライン入口。"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Sequence

from .models import ValidationError, validate_plan, validate_preferences
from .render import render_plan_markdown, render_plans_html
from .store import PlanStore, dish_names


def load_json(path: Path, label: str) -> Any:
    try:
        with path.open(encoding="utf-8") as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationError(f"{label}を読み込めません: {path}: {error}") from error


def load_preferences(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    preferences = load_json(path, "設定")
    return validate_preferences(preferences)


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("YYYY-MM-DD 形式で指定してください") from error


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="meal-schedule", description="献立の検証・保存・参照")
    parser.add_argument("--data-dir", type=Path, default=Path("data/plans"))
    parser.add_argument("--preferences", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate-preferences", help="利用者設定JSONを検証する")

    validate_parser = subparsers.add_parser("validate", help="献立JSONを検証する")
    validate_parser.add_argument("plan", type=Path)

    save_parser = subparsers.add_parser("save", help="確認済みの献立を保存する")
    save_parser.add_argument("plan", type=Path)
    save_parser.add_argument("--overwrite", action="store_true")

    show_parser = subparsers.add_parser("show", help="保存済み献立を期間で表示する")
    show_parser.add_argument("--from", dest="start", type=parse_date)
    show_parser.add_argument("--to", dest="end", type=parse_date)
    show_parser.add_argument(
        "--format", choices=("markdown", "json", "html"), default="markdown"
    )
    show_parser.add_argument("--output", type=Path, help="表示結果をファイルへ保存する")

    recent_parser = subparsers.add_parser("recent-dishes", help="最近の料理名を提案用に表示する")
    recent_parser.add_argument("--days", type=int, default=28)
    recent_parser.add_argument("--as-of", type=parse_date, default=date.today())
    return parser


def run(arguments: Sequence[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(arguments)
    try:
        preferences = load_preferences(args.preferences)
        store = PlanStore(args.data_dir)
        if args.command == "validate-preferences":
            if args.preferences is None:
                raise ValidationError("validate-preferences には --preferences が必要です")
            print("設定は有効です")
            return 0
        if args.command in {"validate", "save"}:
            plan = load_json(args.plan, "献立")
            validate_plan(plan, preferences)
            if args.command == "validate":
                print("献立は有効です")
            else:
                destination = store.save(
                    plan, preferences, overwrite=args.overwrite
                )
                print(destination)
            return 0
        if args.command == "show":
            plans = list(store.iter_plans(args.start, args.end, preferences))
            if not plans:
                print("指定期間の献立はありません")
                return 0
            if args.format == "json":
                rendered = json.dumps(plans, ensure_ascii=False, indent=2) + "\n"
            elif args.format == "html":
                if args.output is None:
                    raise ValidationError("--format html には --output が必要です")
                rendered = render_plans_html(plans)
            else:
                rendered = "\n".join(
                    render_plan_markdown(plan).rstrip() for plan in plans
                ) + "\n"
            if args.output is None:
                print(rendered, end="")
            else:
                try:
                    args.output.parent.mkdir(parents=True, exist_ok=True)
                    args.output.write_text(rendered, encoding="utf-8")
                except OSError as error:
                    raise ValidationError(
                        f"表示結果を書き込めません: {args.output}: {error}"
                    ) from error
                print(args.output)
            return 0
        if args.command == "recent-dishes":
            if args.days <= 0:
                raise ValidationError("--days は正の整数で指定してください")
            start = args.as_of - timedelta(days=args.days - 1)
            names = dish_names(store.iter_plans(start, args.as_of, preferences))
            if names:
                print("\n".join(names))
            else:
                print("指定期間の料理履歴はありません")
            return 0
    except ValidationError as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 2
    parser.error("未知のコマンドです")
    return 2
