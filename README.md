# Harness Engineering Template

人間とコーディングエージェントが、仕様・設計判断・実行計画をコードとともに管理するためのリポジトリ運用ひな形です。

## このテンプレートが提供するもの

- 人間とAIの作業ルール・正本への入口
- 仕様、設計判断、実行計画の記入用テンプレート
- 変更理由・影響・検証結果を残すPull Request形式

## 想定する利用者

- コーディングエージェントを使った開発を、再現可能な形で進めたいチーム
- プロダクトや設計の判断をチャット履歴だけに残したくないチーム
- 新しく参加した人やエージェントが、短時間で作業文脈を把握できるようにしたいチーム

## 使い方

1. このリポジトリを複製し、対象プロダクトの目的・利用者・起動方法をここへ記載します。
2. `AGENTS.md`に不変条件と検証コマンドを、[ARCHITECTURE.md](ARCHITECTURE.md)に実装領域と依存方向を追加します。
3. [ドキュメントの作業手順](docs/README.md)に従い、必要な仕様・設計・計画を作成します。

## 情報の置き場所

| 情報 | 正本 | 役割 |
| --- | --- | --- |
| リポジトリの概要・導入方法 | `README.md` | 人とエージェントの最初の入口 |
| 作業時の必須ルール | `AGENTS.md` | 簡潔な運用ルールと詳細情報への案内 |
| 全体構成・依存方向 | [ARCHITECTURE.md](ARCHITECTURE.md) | 領域の責務、実行入口、依存ルールの案内 |
| Pull Requestの記載項目 | `.github/PULL_REQUEST_TEMPLATE.md` | 変更理由・影響・検証を揃える |
| プロダクト仕様 | [`docs/product-specs/`](docs/product-specs/index.md) | 利用者の振る舞い、スコープ、受け入れ条件 |
| 設計判断 | [`docs/design-docs/`](docs/design-docs/index.md) | 背景、選択肢、決定、影響 |
| 実行計画 | [`docs/exec-plans/`](docs/exec-plans/index.md) | 作業の範囲、進捗、決定ログ、検証 |
| 品質 | [docs/QUALITY.md](docs/QUALITY.md) | 品質条件、検証の証拠、既知課題 |
| 文書テンプレート | [docs/templates/](docs/templates/README.md) | 新しい仕様・判断・計画のコピー元 |

重要な判断はMarkdownに残し、繰り返すルールはテスト・リンター・テンプレートなどで機械的に守ります。変更完了には、必要な文書更新と検証結果を含めます。

## 変更への参加

変更前に関連する仕様・実装・設定を確認します。Pull Requestは日本語で作成し、[PRテンプレート](.github/PULL_REQUEST_TEMPLATE.md)に従います。必須ルールは[AGENTS.md](AGENTS.md)を参照してください。
