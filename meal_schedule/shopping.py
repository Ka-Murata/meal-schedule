"""料理の材料から買い物リストを作る。"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any


def build_shopping_list(plan: dict[str, Any]) -> list[dict[str, Any]]:
    numeric: dict[tuple[str, str, str], Decimal] = defaultdict(Decimal)
    textual: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    sources: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    display_names: dict[tuple[str, str, str], str] = {}
    for meal in plan["meals"]:
        for dish in meal["dishes"]:
            for ingredient in dish["ingredients"]:
                name = ingredient["name"].strip()
                unit = ingredient["unit"].strip()
                category = ingredient.get("category", "その他").strip()
                key = (name.casefold(), unit.casefold(), category.casefold())
                display_names.setdefault(key, name)
                quantity = ingredient["quantity"]
                if isinstance(quantity, (int, float)) and not isinstance(quantity, bool):
                    numeric[key] += Decimal(str(quantity))
                else:
                    textual[key].append(str(quantity).strip())
                sources[key].add(f"{meal['date']} {dish['name']}")
    items: list[dict[str, Any]] = []
    for key in sorted(set(numeric) | set(textual), key=lambda value: (value[2], value[0], value[1])):
        amount_parts: list[str] = []
        if key in numeric:
            value = numeric[key]
            amount_parts.append(format(value.normalize(), "f"))
        amount_parts.extend(textual.get(key, []))
        items.append(
            {
                "name": display_names[key],
                "quantity": " + ".join(amount_parts),
                "unit": key[1],
                "category": key[2],
                "sources": sorted(sources[key]),
            }
        )
    return items
