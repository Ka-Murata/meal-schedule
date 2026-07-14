"""献立を後から読みやすいMarkdownへ整形する。"""

from __future__ import annotations

from typing import Any

from .shopping import build_shopping_list


def render_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        f"# {plan['title']}",
        "",
        f"期間: {plan['start_date']}〜{plan['end_date']} / {plan['servings']}人分",
        "",
    ]
    for meal in sorted(plan["meals"], key=lambda value: (value["date"], value["meal_type"])):
        lines.extend([f"## {meal['date']} {meal['meal_type']}", ""])
        for dish in meal["dishes"]:
            lines.extend([f"### {dish['name']}", "", "材料:", ""])
            for ingredient in dish["ingredients"]:
                lines.append(
                    f"- {ingredient['name']}: {ingredient['quantity']}{ingredient['unit']}"
                )
            lines.extend(["", "手順:", ""])
            for number, step in enumerate(dish["steps"], start=1):
                lines.append(f"{number}. {step}")
            lines.append("")
    lines.extend(["## 買い物リスト", ""])
    current_category: str | None = None
    for item in build_shopping_list(plan):
        if item["category"] != current_category:
            current_category = item["category"]
            lines.extend([f"### {current_category}", ""])
        sources = "、".join(item["sources"])
        lines.append(f"- [ ] {item['name']}: {item['quantity']}{item['unit']}（{sources}）")
    if plan.get("notes"):
        lines.extend(["", "## メモ", "", plan["notes"]])
    return "\n".join(lines).rstrip() + "\n"
