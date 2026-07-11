# アーキテクチャ

状態: template

所有者: <担当者またはチーム>

見直し: 技術スタック、実行入口、主要な依存関係、または文書構成を変更する時

関連: [README](README.md)、[作業ルール](AGENTS.md)、[ドキュメント入口](docs/README.md)、[品質](docs/QUALITY.md)

## 目的と適用範囲

この文書は、このリポジトリの構成、各領域の責務、依存方向を案内するための入口です。対象プロダクトの実装アーキテクチャは、技術スタックと実装領域が決まった後にここへ追記します。

現時点では、プロダクトコード、実行可能なエントリーポイント、テスト、CIは未導入です。存在しない構成やコマンドは推測で記載しません。

## 現在の構成と責務

| 領域 | 責務 | 正本または入口 |
| --- | --- | --- |
| リポジトリ入口 | テンプレートの目的と利用方法を案内する | [README.md](README.md) |
| 作業ルール | 変更時の必須ルールと正本を示す | [AGENTS.md](AGENTS.md) |
| プロダクト仕様 | 利用者の振る舞い、スコープ、受け入れ条件を管理する | [docs/product-specs/](docs/product-specs/index.md) |
| 設計判断 | 継続して参照する技術判断と影響を管理する | [docs/design-docs/](docs/design-docs/index.md) |
| 実行計画 | 複雑な変更の進捗、判断、検証を管理する | [docs/exec-plans/](docs/exec-plans/index.md) |
| 品質 | 品質条件、検証の証拠、既知の課題を管理する | [docs/QUALITY.md](docs/QUALITY.md) |
| Pull Request | 変更理由・影響・検証結果を揃える | [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md) |

## 情報と依存の方向

```text
README ──> AGENTS ──> docs/README
                         ├─> product-specs ──> design-docs
                         ├─> exec-plans ─────> （将来の実装・設定・テスト）
                         └─> QUALITY <────────── 検証の証拠
```

- 仕様は実装方法を固定せず、設計判断は仕様と矛盾しないようにします。
- 実行計画は、関連する仕様・設計判断・検証結果へリンクします。
- 実装と設定を導入した後は、それらを動作と設定値の正本とし、文書には意図・判断・リンクを残します。

## 導入時に追加する領域

次の領域は、必要性と技術選定が確定した変更で追加します。空のディレクトリは作成しません。

| 領域 | 追加する契機 | 更新する文書 |
| --- | --- | --- |
| `src/` または `apps/` | 実装の所有境界と技術スタックを決めた時 | この文書、`AGENTS.md`、関連する設計判断 |
| `tests/` | 検証対象とテスト方式を決めた時 | `AGENTS.md`、[品質](docs/QUALITY.md) |
| `scripts/` | 繰り返す開発・検証作業を自動化する時 | `README.md`、`AGENTS.md` |
| `config/` | 複数の設定を役割ごとに管理する必要が出た時 | この文書、関連する設計判断 |
| `.github/workflows/` | 実行すべき検証コマンドが確定した時 | [品質](docs/QUALITY.md) |
| `docs/references/` | 安定した外部仕様・ベンダー資料を保存する必要が出た時 | `docs/README.md` と索引 |
| `docs/generated/` | 再生成可能な成果物を保存する必要が出た時 | 生成元・生成コマンド・更新契機を記載した索引 |

運用・セキュリティの要件が具体化した時は、必要に応じて `docs/RELIABILITY.md` または `docs/SECURITY.md` を追加します。どちらも、所有者、見直し契機、検証方法が明確になってから作成します。

## 検証

現時点で自動テスト、リンター、CIはありません。文書変更では、リンクの存在確認と `git diff --check` を実施します。自動検証を導入した後は、最短コマンドを `AGENTS.md` に、品質条件と証拠を [docs/QUALITY.md](docs/QUALITY.md) に記録します。
