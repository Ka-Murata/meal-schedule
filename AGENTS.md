# AGENTS.md

## 正本

- 概要・利用方法は `README.md`、Pull Requestの記載項目は `.github/PULL_REQUEST_TEMPLATE.md` を正とする。
- 領域の責務、実行入口、依存方向は [ARCHITECTURE.md](ARCHITECTURE.md) を正とする。
- 設計判断・仕様・運用手順はリポジトリ内のMarkdownで管理する。`AGENTS.md` には入口と必須ルールだけを置く。
- 文書を新規作成・更新するときは [`docs/README.md`](docs/README.md) と対象文書群の `index.md` に従う。作成・索引更新・リンク確認までを一つの変更として完了する。

## 変更とPull Request

- 着手前に関連する仕様・実装・設定を確認し、不明な仕様を推測で固定しない。
- 変更に応じた検証を実施し、結果または未実施の理由をPR本文に記載する。
- PRは日本語で、テンプレートに従い、簡潔なタイトルで作成する。Draft指定がなければReady for reviewとする。
- 無関係な変更は同じPRに含めない。
