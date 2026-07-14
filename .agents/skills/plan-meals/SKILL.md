---
name: plan-meals
description: Set up meal preferences and plan, validate, save, or retrieve daily or weekly meal schedules with per-dish ingredients, cooking steps, aggregated shopping lists, and history-aware variety. Use when the user asks Codex for first-time setup, preference changes, meal planning, recipes, a shopping list, saving an agreed plan, reviewing past meals, or avoiding recently repeated dishes in this repository.
---

# Plan meals

Use the repository CLI as the source of truth for validation, history, shopping-list aggregation, and persistence. Generate recipe content in the conversation, but never claim it was saved until the CLI succeeds.

## Choose the workflow

- For first-time setup or preference changes, follow **Set up preferences**.
- For a new plan, follow **Plan a period**.
- For “save this” or equivalent, follow **Confirm and save**. Reuse the proposal from the current conversation; do not silently regenerate it.
- For past plans, follow **Review history**.

## Set up preferences

1. Work from the repository root and inspect `config/preferences.json` if it exists. For changes, preserve values the user did not ask to change.
2. Ask for the required values that are not already known: household size, included meal types, and whether anyone has food allergies. Never assume there are no allergies. Clearly separate allergies from dislikes.
3. Offer the example defaults for optional values instead of requiring them: maximum cooking time 45 minutes, weekly budget 8,000 yen, and Monday as the first day of the week. Let the user omit either numeric limit. Ask follow-up questions only when an answer is ambiguous or unsafe to encode.
4. Summarize the proposed settings in plain language, including an explicit allergy statement, and ask the user to confirm before writing personal information to `config/preferences.json`.
5. After confirmation, create `config/preferences.json` with schema version 1 and these fields: `household_size`, `meals`, `allergies`, `dislikes`, optional `max_cooking_minutes`, optional `weekly_budget_yen`, and `week_starts_on`. Use empty arrays for confirmed “none”; do not encode an unanswered allergy question as an empty array.
6. Validate the saved settings:

   ```bash
   python3 -m meal_schedule --preferences config/preferences.json validate-preferences
   ```

7. Report validation success and the saved path. If validation fails, correct the draft and validate again; do not proceed to meal planning with invalid settings.

## Plan a period

1. Work from the repository root.
2. Read `config/preferences.json` when it exists and validate it:

   ```bash
   python3 -m meal_schedule --preferences config/preferences.json validate <proposal.json>
   ```

   The command validates both files together after a proposal exists. Before generation, inspect the preferences JSON directly.
3. If preferences are absent, follow **Set up preferences** before planning. If the user does not want to save settings, collect the same required values for this proposal only and state that they will not persist.
4. Resolve relative dates using the current date and show exact `YYYY-MM-DD` dates. Honor `week_starts_on` when available.
5. Inspect recent dishes before proposing replacements:

   ```bash
   python3 -m meal_schedule --preferences config/preferences.json recent-dishes --days 28 --as-of YYYY-MM-DD
   ```

   Omit `--preferences` when no preferences file exists. Avoid exact recent repeats unless the user requests one; explain any deliberate repeat.
6. Create a proposal JSON outside `data/plans/`, normally under `/tmp`. Use this structure:

   ```json
   {
     "schema_version": 1,
     "title": "期間を表す題名",
     "start_date": "YYYY-MM-DD",
     "end_date": "YYYY-MM-DD",
     "servings": 2,
     "meals": [
       {
         "date": "YYYY-MM-DD",
         "meal_type": "夕食",
         "dishes": [
           {
             "name": "料理名",
             "servings": 2,
             "ingredients": [
               {"name": "食材", "quantity": 200, "unit": "g", "category": "野菜"}
             ],
             "steps": ["具体的な手順1", "具体的な手順2"]
           }
         ]
       }
     ],
     "notes": "任意の補足"
   }
   ```

   Cover every date from `start_date` through `end_date`. Give every dish useful quantities and ordered, actionable steps. Use a descriptive string such as `"少々"` with an empty unit only when a numeric amount is inappropriate.
7. Check exact forbidden-food terms yourself, including likely aliases or derivatives that simple text matching may miss. Treat uncertainty as a reason to ask, not as evidence of safety. This tool is not a medical safety guarantee.
8. Validate the proposal:

   ```bash
   python3 -m meal_schedule --preferences config/preferences.json validate /tmp/proposal.json
   ```

9. Render the proposal with recipes, steps, and the computed shopping list. Before saving, the CLI can render only stored plans, so present the validated proposal clearly in the response. Include:

   - dated meals and dish names;
   - ingredients and ordered steps for every dish;
   - the aggregated shopping list, grouped by category;
   - important assumptions and deliberate repeats.
10. Ask whether the user wants to confirm and save this exact plan. Do not save on the initial proposal turn.

## Confirm and save

1. Ensure the user explicitly confirmed the exact proposal or clearly requested saving it.
2. Revalidate the unchanged proposal.
3. Save it:

   ```bash
   python3 -m meal_schedule --preferences config/preferences.json save /tmp/proposal.json
   ```

4. Report the returned path. Never use `--overwrite` without explicit confirmation that the existing record should be replaced.
5. Render the stored result to prove it can be retrieved:

   ```bash
   python3 -m meal_schedule --preferences config/preferences.json show --from YYYY-MM-DD --to YYYY-MM-DD
   ```

## Review history

Resolve the requested period to exact dates, then run:

```bash
python3 -m meal_schedule --preferences config/preferences.json show --from YYYY-MM-DD --to YYYY-MM-DD
```

Return the stored output without inventing missing plans. If the CLI says no plan exists, say so and offer to create one.

## Handle failures

- Surface CLI validation errors and correct the proposal; never bypass validation.
- If a stored JSON file is corrupt, identify its path and stop using that record until it is fixed.
- If a plan already exists, show the conflict and ask before overwriting.
- Keep all permanent plans under `data/plans/`; do not hand-edit a stored plan when the CLI workflow can validate a replacement.
