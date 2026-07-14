# Meal Schedule

Codexとの会話から、毎日または1週間の献立、人数分の材料、具体的な調理手順、集約した買い物リストを作り、確定した献立を後から確認できるローカルプロジェクトです。

献立の文章はCodexが作り、Python CLIが形式、日付、人数、禁止食材の単純一致を検証します。確定した履歴は `data/plans/` のJSONとして残るため、新しいCodexセッションからも参照できます。外部サービスへの送信は行いません。

## 必要環境

- Python 3.10以上（追加パッケージ不要）
- リポジトリ内スキルを読み込めるCodex環境

## 最初の設定

Codexに次のように依頼すると、人数、対象の食事、アレルギー、苦手な食材などを順に確認し、内容の確認後に設定ファイルを作成・検証します。

```text
最初の設定を手伝って。
```

手動で設定する場合は、利用者設定の例をコピーして編集します。

```bash
cp config/preferences.example.json config/preferences.json
```

`config/preferences.json` は個人設定のためGit管理対象外です。アレルギーの単純一致検査を補助しますが、医療上の安全は保証しません。曖昧な原材料や派生食材は必ず個別に確認してください。

```bash
python3 -m meal_schedule --preferences config/preferences.json validate-preferences
```

## Codexから使う

このリポジトリをCodexで開き、自然文で依頼します。`.agents/skills/plan-meals/` が献立作成、履歴参照、確認後保存の手順を提供します。

```text
今週の夕食の献立を考えて。レシピと買い物リストも詳しく教えて。
```

Codexは設定と直近28日の履歴を確認し、日付付き献立を提案します。初回提案は保存しません。内容を確認してから次のように依頼します。

```text
この献立で確定して保存して。
```

後から確認する場合:

```text
先週の献立を見せて。
```

ブラウザで見やすく確認したい場合は、その旨をCodexへ伝えてください。保存済み献立から、日付ナビゲーション、折りたたみ可能なレシピ、チェックできる買い物リストを含むHTMLを作成します。HTMLは外部通信やWebサーバーを使わない単一ファイルです。

```text
先週の献立をブラウザで見やすく確認できるようにして。
```

設定がない場合、Codexは初期設定を案内します。少なくとも人数、対象の食事、アレルギーの有無を確認し、利用者が内容を確認するまで設定ファイルを書き込みません。

## CLIを直接使う

提案JSONの形式は [examples/weekly-plan.json](examples/weekly-plan.json) を参照してください。

```bash
# 利用者設定だけを検証する
python3 -m meal_schedule --preferences config/preferences.json validate-preferences

# 提案を検証する
python3 -m meal_schedule --preferences config/preferences.json validate examples/weekly-plan.json

# 利用者が確定した提案を保存する
python3 -m meal_schedule --preferences config/preferences.json save examples/weekly-plan.json

# 指定期間の献立、レシピ、手順、買い物リストを表示する
python3 -m meal_schedule --preferences config/preferences.json show --from 2026-07-13 --to 2026-07-19

# 指定期間をブラウザ用の単一HTMLへ書き出す（出力ファイルをブラウザで開く）
python3 -m meal_schedule --preferences config/preferences.json show --from 2026-07-13 --to 2026-07-19 --format html --output meal-history.html

# 次の提案で重複を避けるため、最近の料理名を表示する
python3 -m meal_schedule --preferences config/preferences.json recent-dishes --days 28 --as-of 2026-07-19
```

共通オプション `--data-dir` で履歴ディレクトリを変更できます。既存期間を置き換える `--overwrite` は、上書きを明示的に確認した場合だけ使用してください。

## データ

| パス | 内容 |
| --- | --- |
| `config/preferences.example.json` | 利用者設定の記入例 |
| `config/preferences.json` | 実際の個人設定（Git管理外） |
| `data/plans/YYYY-MM-DD.json` | 開始日ごとの確定済み献立履歴 |
| `examples/weekly-plan.json` | 提案JSONの例 |

買い物リストは保存済み材料から表示時に再計算します。同じ食材名・単位・カテゴリの数量を集約し、利用元の料理を併記します。

HTML表示も保存済みJSONから都度生成する派生物です。CSSをファイル内に含み、外部の画像、フォント、スクリプト、サービスへ接続しないため、追加費用なしでローカル利用できます。画面幅とダークモードに追従し、印刷にも対応します。買い物リストのチェック状態はHTMLを開いている間だけの一時的な状態で、元の献立JSONは変更しません。

## 開発と検証

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q meal_schedule tests
python3 /home/vscode/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/plan-meals
```

領域の責務と依存方向は [ARCHITECTURE.md](ARCHITECTURE.md)、利用者要件は [献立計画アシスタント仕様](docs/product-specs/meal-planning-assistant.md)、品質条件は [docs/QUALITY.md](docs/QUALITY.md) を参照してください。
