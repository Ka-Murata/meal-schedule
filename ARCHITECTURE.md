# アーキテクチャ

状態: active

所有者: プロジェクトオーナー

見直し: 技術スタック、実行入口、保存形式、主要な依存関係、または文書構成を変更する時

関連: [README](README.md)、[作業ルール](AGENTS.md)、[プロダクト仕様](docs/product-specs/meal-planning-assistant.md)、[設計判断](docs/design-docs/2026-07-14-meal-planning-interface.md)、[品質](docs/QUALITY.md)

## 目的と適用範囲

この文書は、Codexから使う献立計画アシスタントの実行入口、実装領域、永続データ、依存方向を定めます。MVPはローカル実行に限定し、外部API、Web UI、データベース、認証基盤を持ちません。

## 実行入口

| 入口 | 用途 | 正本 |
| --- | --- | --- |
| Codexスキル | 自然文での条件確認、履歴を踏まえた献立・レシピ生成、確定確認 | [.agents/skills/plan-meals/SKILL.md](.agents/skills/plan-meals/SKILL.md) |
| Python CLI | JSON検証、確定後保存、期間検索、Markdown・静的HTML表示、買い物集約、最近の料理取得 | [`python3 -m meal_schedule`](meal_schedule/__main__.py) |
| 利用者設定 | 人数、対象食事、禁止食材、任意制約 | [設定例](config/preferences.example.json) |
| 献立履歴 | 検証済みの確定献立 | 実行時に作成する `data/plans/*.json` |

## 構成と責務

| 領域 | 責務 |
| --- | --- |
| `.agents/skills/plan-meals/` | Codex会話のワークフローと保存前確認を規定する |
| `meal_schedule/models.py` | 設定・献立の構造、期間、人数、禁止食材の機械的検証 |
| `meal_schedule/store.py` | JSON履歴の原子的保存、破損検出、期間検索 |
| `meal_schedule/shopping.py` | 材料の数量集約と利用元追跡 |
| `meal_schedule/render.py` | レシピ、手順、買い物リストのMarkdown表示と自己完結HTML表示 |
| `meal_schedule/cli.py` | コマンド引数、入出力、利用者向けエラー |
| `config/` | 利用者設定の例。実設定はGit管理外 |
| `examples/` | 入力形式の実行可能な例 |
| `tests/` | 仕様の受け入れ条件と失敗条件の自動検証 |
| `docs/` | 仕様、設計判断、計画、品質証拠の正本 |
| `.devcontainer/` | Codex IDE拡張機能などを含む再現可能な開発環境 |

## 依存方向

```text
利用者 ──> Codex ──> plan-meals skill ──> meal_schedule CLI
                                             ├─> models
                                             ├─> store ──> models ──> data/plans
                                             └─> render ──> shopping

config/preferences.json ─────────────────────> models
```

- `models` と `shopping` はファイルシステムやCodexに依存しない。
- `store` は検証済みモデルだけを保存し、既存ファイルを既定で上書きしない。
- `render` は保存データから買い物リストを再計算し、重複する派生データを保存しない。
- HTML表示は外部資産やネットワーク通信を必要としない単一ファイルとして生成し、Webサーバーや認証を追加しない。
- スキルは生成内容を保存前にCLIで検証し、利用者の明示確認後だけ `save` を実行する。
- アプリ本体はPython標準ライブラリだけを使用し、ネットワーク通信を行わない。

## データ境界

- 確定献立はスキーマバージョン付きJSONとして開始日単位で保存する。
- 実設定 `config/preferences.json` はGit管理外とし、アレルギー等の個人情報をリポジトリ履歴へ含めない。
- 禁止食材検査は文字列一致の補助であり、派生原料や交差接触まで保証しない。曖昧な場合はスキルが利用者へ確認する。
- 破損または不完全なJSONは黙って無視せず、修正可能なエラーとして停止する。

## 文書領域

| 領域 | 正本または入口 |
| --- | --- |
| 作業ルール | [AGENTS.md](AGENTS.md) |
| プロダクト仕様 | [docs/product-specs/](docs/product-specs/index.md) |
| 設計判断 | [docs/design-docs/](docs/design-docs/index.md) |
| 実行計画 | [docs/exec-plans/](docs/exec-plans/index.md) |
| 品質 | [docs/QUALITY.md](docs/QUALITY.md) |
| Pull Request | [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md) |

## 検証

最短コマンドは [AGENTS.md](AGENTS.md)、品質条件と証拠の対応は [docs/QUALITY.md](docs/QUALITY.md) を正とします。CLIの単体・結合テスト、Python構文検査、スキル構造検証、文書リンク検査、`git diff --check` を変更範囲に応じて実行します。
