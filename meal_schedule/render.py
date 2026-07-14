"""献立を後から読みやすいMarkdownまたはHTMLへ整形する。"""

from __future__ import annotations

from html import escape
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


def _text(value: Any) -> str:
    return escape(str(value), quote=True)


def render_plans_html(plans: list[dict[str, Any]]) -> str:
    """複数の保存済み献立を自己完結したHTML文書へ整形する。"""

    if not plans:
        raise ValueError("HTML表示には1件以上の献立が必要です")

    meals = [meal for plan in plans for meal in plan["meals"]]
    first_date = min(plan["start_date"] for plan in plans)
    last_date = max(plan["end_date"] for plan in plans)
    day_count = len({meal["date"] for meal in meals})
    navigation: list[str] = []
    plan_sections: list[str] = []

    for plan_index, plan in enumerate(plans):
        meal_sections: list[str] = []
        sorted_meals = sorted(
            plan["meals"], key=lambda value: (value["date"], value["meal_type"])
        )
        for meal_index, meal in enumerate(sorted_meals):
            meal_id = f"meal-{plan_index}-{meal_index}"
            navigation.append(
                f'<a href="#{meal_id}"><span>{_text(meal["date"])}</span>'
                f'{_text(meal["meal_type"])}</a>'
            )
            dishes: list[str] = []
            for dish in meal["dishes"]:
                ingredients = "".join(
                    "<li><span>"
                    f'{_text(ingredient["name"])}</span><strong>'
                    f'{_text(ingredient["quantity"])}{_text(ingredient["unit"])}</strong></li>'
                    for ingredient in dish["ingredients"]
                )
                steps = "".join(f"<li>{_text(step)}</li>" for step in dish["steps"])
                dishes.append(
                    '<details class="dish" open>'
                    f'<summary><span>{_text(dish["name"])}</span>'
                    f'<small>{_text(dish["servings"])}人分</small></summary>'
                    '<div class="recipe"><div><h4>材料</h4>'
                    f'<ul class="ingredients">{ingredients}</ul></div>'
                    f'<div><h4>手順</h4><ol class="steps">{steps}</ol></div></div>'
                    "</details>"
                )
            meal_sections.append(
                f'<article class="meal" id="{meal_id}"><header>'
                f'<time datetime="{_text(meal["date"])}">{_text(meal["date"])}</time>'
                f'<span>{_text(meal["meal_type"])}</span></header>{"".join(dishes)}</article>'
            )

        shopping_items: list[str] = []
        current_category: str | None = None
        for item_index, item in enumerate(build_shopping_list(plan)):
            if item["category"] != current_category:
                if current_category is not None:
                    shopping_items.append("</ul>")
                current_category = item["category"]
                shopping_items.append(f'<h3>{_text(current_category)}</h3><ul>')
            checkbox_id = f"shopping-{plan_index}-{item_index}"
            sources = "、".join(item["sources"])
            shopping_items.append(
                f'<li><input type="checkbox" id="{checkbox_id}">'
                f'<label for="{checkbox_id}"><span>{_text(item["name"])} '
                f'<strong>{_text(item["quantity"])}{_text(item["unit"])}</strong></span>'
                f'<small>{_text(sources)}</small></label></li>'
            )
        if current_category is not None:
            shopping_items.append("</ul>")

        notes = ""
        if plan.get("notes"):
            notes = f'<aside class="notes"><h3>メモ</h3><p>{_text(plan["notes"])}</p></aside>'
        plan_sections.append(
            '<section class="plan">'
            f'<div class="plan-title"><div><p>{_text(plan["start_date"])}〜'
            f'{_text(plan["end_date"])}</p><h2>{_text(plan["title"])}</h2></div>'
            f'<span>{_text(plan["servings"])}人分</span></div>'
            f'<div class="meal-list">{"".join(meal_sections)}</div>'
            '<section class="shopping"><div class="section-heading">'
            '<p>Shopping list</p><h2>買い物リスト</h2></div>'
            f'{"".join(shopping_items)}</section>{notes}</section>'
        )

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>保存済み献立</title>
  <style>
    :root {{ color-scheme: light dark; --bg: #f6f3ec; --surface: #fffdf8; --ink: #25251f; --muted: #706f63; --line: #dfdbcf; --accent: #b34a32; --accent-soft: #f2ddd4; --green: #315b43; }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: system-ui, -apple-system, "Hiragino Sans", "Yu Gothic UI", sans-serif; line-height: 1.65; }}
    .hero {{ padding: 3.5rem max(1.25rem, calc((100% - 70rem) / 2)); background: var(--green); color: #fffdf8; }}
    .eyebrow, .section-heading p {{ margin: 0 0 .35rem; font-size: .75rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }}
    h1 {{ margin: 0; font-family: ui-serif, "Yu Mincho", serif; font-size: clamp(2.2rem, 7vw, 4.8rem); font-weight: 600; line-height: 1.15; }}
    .hero-meta {{ margin: 1rem 0 0; opacity: .8; }}
    .day-nav {{ display: flex; gap: .6rem; padding: 1rem max(1.25rem, calc((100% - 70rem) / 2)); overflow-x: auto; background: var(--surface); border-bottom: 1px solid var(--line); position: sticky; top: 0; z-index: 2; }}
    .day-nav a {{ min-width: max-content; padding: .5rem .8rem; color: var(--ink); text-decoration: none; border: 1px solid var(--line); border-radius: 999px; font-size: .85rem; }}
    .day-nav a span {{ margin-right: .45rem; font-weight: 700; }}
    main {{ width: min(70rem, calc(100% - 2rem)); margin: 2.5rem auto 5rem; }}
    .plan + .plan {{ margin-top: 4rem; padding-top: 4rem; border-top: 2px solid var(--line); }}
    .plan-title {{ display: flex; align-items: end; justify-content: space-between; gap: 1rem; margin-bottom: 1.25rem; }}
    .plan-title p {{ margin: 0; color: var(--muted); font-size: .85rem; }}
    h2 {{ margin: 0; font-family: ui-serif, "Yu Mincho", serif; font-size: clamp(1.7rem, 4vw, 2.6rem); line-height: 1.3; }}
    .plan-title > span {{ flex: none; padding: .35rem .75rem; color: var(--green); background: #dce8de; border-radius: 999px; font-size: .85rem; font-weight: 700; }}
    .meal-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 28rem), 1fr)); gap: 1rem; align-items: start; }}
    .meal {{ scroll-margin-top: 5rem; background: var(--surface); border: 1px solid var(--line); border-radius: 1rem; overflow: hidden; box-shadow: 0 8px 25px rgb(40 35 25 / 6%); }}
    .meal > header {{ display: flex; justify-content: space-between; padding: 1rem 1.15rem; background: var(--accent-soft); color: #662819; font-weight: 700; }}
    .dish + .dish {{ border-top: 1px solid var(--line); }}
    .dish summary {{ display: flex; justify-content: space-between; gap: 1rem; padding: 1.1rem 1.2rem; cursor: pointer; font-weight: 750; }}
    .dish summary small {{ color: var(--muted); font-weight: 500; white-space: nowrap; }}
    .recipe {{ display: grid; grid-template-columns: minmax(10rem, .8fr) minmax(14rem, 1.2fr); gap: 1.5rem; padding: 0 1.2rem 1.35rem; }}
    h4 {{ margin: 0 0 .45rem; color: var(--muted); font-size: .75rem; letter-spacing: .08em; }}
    .ingredients, .steps {{ margin: 0; padding-left: 1.25rem; }}
    .ingredients {{ padding: 0; list-style: none; }}
    .ingredients li {{ display: flex; justify-content: space-between; gap: 1rem; padding: .25rem 0; border-bottom: 1px dotted var(--line); }}
    .ingredients strong {{ white-space: nowrap; }}
    .steps li {{ padding: .2rem 0 .45rem .25rem; }}
    .shopping {{ margin-top: 1.5rem; padding: clamp(1.25rem, 4vw, 2.2rem); background: var(--surface); border: 1px solid var(--line); border-radius: 1rem; }}
    .section-heading {{ margin-bottom: 1rem; }}
    .section-heading p {{ color: var(--accent); }}
    .shopping h3 {{ margin: 1.3rem 0 .4rem; color: var(--green); font-size: 1rem; }}
    .shopping ul {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 19rem), 1fr)); gap: .5rem 1.4rem; margin: 0; padding: 0; list-style: none; }}
    .shopping li {{ display: flex; gap: .65rem; padding: .55rem 0; border-bottom: 1px solid var(--line); }}
    .shopping input {{ width: 1.15rem; height: 1.15rem; margin-top: .25rem; accent-color: var(--green); }}
    .shopping label {{ display: grid; cursor: pointer; }}
    .shopping label small {{ color: var(--muted); }}
    .shopping input:checked + label span {{ color: var(--muted); text-decoration: line-through; }}
    .notes {{ margin-top: 1rem; padding: 1rem 1.25rem; background: #fff4cc; color: #55420d; border-radius: .75rem; }}
    .notes h3, .notes p {{ margin: 0; }}
    @media (max-width: 42rem) {{ .hero {{ padding-top: 2.5rem; padding-bottom: 2.5rem; }} .recipe {{ grid-template-columns: 1fr; }} .plan-title {{ align-items: start; }} }}
    @media (prefers-color-scheme: dark) {{ :root {{ --bg: #191b18; --surface: #232620; --ink: #f3efe3; --muted: #b7b3a6; --line: #41443d; --accent-soft: #4d2b23; }} .meal > header {{ color: #ffd9cd; }} .plan-title > span {{ color: #d4efda; background: #294334; }} .notes {{ background: #473c19; color: #fff0b2; }} }}
    @media print {{ :root {{ color-scheme: light; --bg: #fff; --surface: #fff; }} .hero {{ padding: 1rem 0; color: var(--ink); background: #fff; }} .day-nav {{ display: none; }} main {{ width: 100%; margin: 1rem 0; }} .meal, .shopping {{ box-shadow: none; break-inside: avoid; }} details:not([open]) > *:not(summary) {{ display: block; }} }}
  </style>
</head>
<body>
  <header class="hero">
    <p class="eyebrow">Meal archive</p>
    <h1>保存済み献立</h1>
    <p class="hero-meta">{_text(first_date)}〜{_text(last_date)} ・ {day_count}日 ・ {len(meals)}食</p>
  </header>
  <nav class="day-nav" aria-label="献立の日付">{"".join(navigation)}</nav>
  <main>{"".join(plan_sections)}</main>
</body>
</html>
"""
