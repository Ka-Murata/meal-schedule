"""外部依存なしで献立JSONを検証する。"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


class ValidationError(ValueError):
    """利用者が修正できる入力エラー。"""


def _require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{path} はオブジェクトである必要があります")
    return value


def _require_list(value: Any, path: str, *, non_empty: bool = False) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{path} は配列である必要があります")
    if non_empty and not value:
        raise ValidationError(f"{path} は1件以上必要です")
    return value


def _require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{path} は空でない文字列である必要があります")
    return value.strip()


def _require_positive_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValidationError(f"{path} は正の整数である必要があります")
    return value


def _parse_date(value: Any, path: str) -> date:
    text = _require_string(value, path)
    try:
        return date.fromisoformat(text)
    except ValueError as error:
        raise ValidationError(f"{path} は YYYY-MM-DD 形式である必要があります") from error


def validate_preferences(raw: Any) -> dict[str, Any]:
    preferences = _require_mapping(raw, "設定")
    if preferences.get("schema_version") != 1:
        raise ValidationError("設定.schema_version は 1 である必要があります")
    _require_positive_int(preferences.get("household_size"), "設定.household_size")
    meals = _require_list(preferences.get("meals"), "設定.meals", non_empty=True)
    for index, meal in enumerate(meals):
        _require_string(meal, f"設定.meals[{index}]")
    for field in ("allergies", "dislikes"):
        values = _require_list(preferences.get(field, []), f"設定.{field}")
        for index, value in enumerate(values):
            _require_string(value, f"設定.{field}[{index}]")
    for field in ("max_cooking_minutes", "weekly_budget_yen"):
        if preferences.get(field) is not None:
            _require_positive_int(preferences[field], f"設定.{field}")
    if preferences.get("week_starts_on", "monday") not in {"monday", "sunday"}:
        raise ValidationError("設定.week_starts_on は monday または sunday である必要があります")
    return preferences


def _forbidden_terms(preferences: dict[str, Any] | None) -> list[str]:
    if preferences is None:
        return []
    validate_preferences(preferences)
    values = preferences.get("allergies", []) + preferences.get("dislikes", [])
    return [str(value).casefold().strip() for value in values if str(value).strip()]


def _check_forbidden(text: str, path: str, forbidden: list[str]) -> None:
    normalized = text.casefold()
    matches = sorted({term for term in forbidden if term in normalized})
    if matches:
        raise ValidationError(f"{path} に禁止食材が含まれています: {', '.join(matches)}")


def _validate_ingredient(raw: Any, path: str, forbidden: list[str]) -> None:
    ingredient = _require_mapping(raw, path)
    name = _require_string(ingredient.get("name"), f"{path}.name")
    _check_forbidden(name, f"{path}.name", forbidden)
    quantity = ingredient.get("quantity")
    if isinstance(quantity, bool) or not isinstance(quantity, (int, float, str)):
        raise ValidationError(f"{path}.quantity は正の数または説明文字列である必要があります")
    if isinstance(quantity, (int, float)) and quantity <= 0:
        raise ValidationError(f"{path}.quantity は正の数である必要があります")
    if isinstance(quantity, str) and not quantity.strip():
        raise ValidationError(f"{path}.quantity は空にできません")
    if not isinstance(ingredient.get("unit"), str):
        raise ValidationError(f"{path}.unit は文字列である必要があります")
    if ingredient.get("category") is not None:
        _require_string(ingredient["category"], f"{path}.category")


def validate_plan(raw: Any, preferences: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = _require_mapping(raw, "献立")
    if plan.get("schema_version") != 1:
        raise ValidationError("献立.schema_version は 1 である必要があります")
    _require_string(plan.get("title"), "献立.title")
    start = _parse_date(plan.get("start_date"), "献立.start_date")
    end = _parse_date(plan.get("end_date"), "献立.end_date")
    if end < start:
        raise ValidationError("献立.end_date は start_date 以降である必要があります")
    if (end - start).days > 31:
        raise ValidationError("1件の献立期間は32日未満にしてください")
    servings = _require_positive_int(plan.get("servings"), "献立.servings")
    if preferences is not None:
        validate_preferences(preferences)
        if servings != preferences["household_size"]:
            raise ValidationError("献立.servings が設定.household_size と一致しません")
    forbidden = _forbidden_terms(preferences)
    meals = _require_list(plan.get("meals"), "献立.meals", non_empty=True)
    covered_dates: set[date] = set()
    meal_keys: set[tuple[date, str]] = set()
    for meal_index, raw_meal in enumerate(meals):
        path = f"献立.meals[{meal_index}]"
        meal = _require_mapping(raw_meal, path)
        meal_date = _parse_date(meal.get("date"), f"{path}.date")
        if meal_date < start or meal_date > end:
            raise ValidationError(f"{path}.date が献立期間外です")
        meal_type = _require_string(meal.get("meal_type"), f"{path}.meal_type")
        key = (meal_date, meal_type.casefold())
        if key in meal_keys:
            raise ValidationError(f"{path} は同じ日付・食事区分で重複しています")
        meal_keys.add(key)
        covered_dates.add(meal_date)
        dishes = _require_list(meal.get("dishes"), f"{path}.dishes", non_empty=True)
        for dish_index, raw_dish in enumerate(dishes):
            dish_path = f"{path}.dishes[{dish_index}]"
            dish = _require_mapping(raw_dish, dish_path)
            dish_name = _require_string(dish.get("name"), f"{dish_path}.name")
            _check_forbidden(dish_name, f"{dish_path}.name", forbidden)
            dish_servings = _require_positive_int(dish.get("servings"), f"{dish_path}.servings")
            if dish_servings != servings:
                raise ValidationError(f"{dish_path}.servings が献立.servings と一致しません")
            ingredients = _require_list(
                dish.get("ingredients"), f"{dish_path}.ingredients", non_empty=True
            )
            for ingredient_index, ingredient in enumerate(ingredients):
                _validate_ingredient(
                    ingredient,
                    f"{dish_path}.ingredients[{ingredient_index}]",
                    forbidden,
                )
            steps = _require_list(dish.get("steps"), f"{dish_path}.steps", non_empty=True)
            for step_index, step in enumerate(steps):
                _require_string(step, f"{dish_path}.steps[{step_index}]")
    expected_dates = {
        start + timedelta(days=offset) for offset in range((end - start).days + 1)
    }
    missing = sorted(expected_dates - covered_dates)
    if missing:
        missing_text = ", ".join(value.isoformat() for value in missing)
        raise ValidationError(f"献立がない日付があります: {missing_text}")
    if plan.get("notes") is not None:
        _require_string(plan["notes"], "献立.notes")
    return plan
