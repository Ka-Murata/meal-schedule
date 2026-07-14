# 品質

状態: active

所有者: プロジェクトオーナー

見直し: テスト、CLI契約、保存形式、スキル、CI、品質条件の変更時

## 正本

最短の実行コマンドは [AGENTS.md](../AGENTS.md)、検証対象は `tests/`、CLIの実動作は `meal_schedule/`、スキル構造は `.agents/skills/plan-meals/` を正本とします。

## 変更完了の条件

| 品質条件 | 実施方法 | 証拠 |
| --- | --- | --- |
| 設定・献立の正常系と境界条件を検証する | `python3 -m unittest discover -s tests -v` | テスト結果 |
| 保存、期間検索、再表示、重複候補取得が一連で動く | CLI結合テスト | `StoreAndCliTests` |
| 材料を集約し、料理との対応を保つ | 買い物リスト単体テスト | `ShoppingAndRenderTests` |
| 静的HTMLが外部通信なしで安全に表示内容を整形する | HTMLレンダー・CLI書き出しテスト | `ShoppingAndRenderTests` と `StoreAndCliTests` |
| 禁止食材、欠落日、人数不一致、破損履歴を拒否する | 入力・失敗系テスト | `ValidationTests` と `StoreAndCliTests` |
| Pythonに構文エラーがない | `python3 -m compileall -q meal_schedule tests` | コマンド結果 |
| Codexスキルの構成が有効 | `quick_validate.py .agents/skills/plan-meals` | 公式バリデータ結果 |
| 文書内の相対リンクが存在する | `test_document_links` | テスト結果 |
| 差分に空白エラーがない | `git diff --check` | コマンド結果 |

## AIの手順

1. 変更範囲と設定・既存テストを確認し、必要な検証を実行する。
2. 結果をPRまたは実行計画に記録する。未実施・失敗は成功として扱わない。
3. 新しい不変条件は仕様または設計判断へ記録し、可能な範囲で自動テストへ追加する。
4. アレルギー検査は補助機能として扱い、文字列一致で検出できない安全性を保証しない。

## 現在の検証証拠

- 2026-07-14: `python3 -m unittest discover -s tests -v` — 13件成功（文書リンクテスト追加前）。
- 2026-07-14: `quick_validate.py .agents/skills/plan-meals` — `Skill is valid!`。
- 2026-07-14: `python3 -m unittest discover -s tests -v` — 20件成功。静的HTMLのエスケープ、主要閲覧要素、期間指定書き出し、出力先の必須化を含む。
- 2026-07-14: `python3 -m compileall -q meal_schedule tests`、`quick_validate.py .agents/skills/plan-meals`、`git diff --check` — 成功。
- 2026-07-14: 実際の保存履歴に対する `show --format html --output` — 成功。7日・14食、レシピ、集約買い物リストを含む単一HTMLを生成。
- 最終結果は [MVP実行計画](exec-plans/completed/2026-07-14-meal-planning-mvp.md) に記録する。

## 既知の課題

| 課題 | 影響 | 次の対応 | 関連 |
| --- | --- | --- | --- |
| CIは未導入 | 検証はローカル実行に依存する | 共有開発またはPR運用を始める時にCI導入を判断する | [技術的負債](exec-plans/tech-debt-tracker.md) |
| 禁止食材は単純な文字列一致 | 派生原料、別名、交差接触を完全には検出できない | スキルによる確認を継続し、医療用途には用いない | [プロダクト仕様](product-specs/meal-planning-assistant.md) |
