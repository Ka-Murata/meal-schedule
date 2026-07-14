# 献立HTMLをGitHub Pagesで公開する

状態: accepted

日付: 2026-07-14

決定者: プロジェクトオーナー

見直し: 公開範囲、リポジトリの可視性、認証要件、HTMLの生成元、またはGitHub Pagesの配備方式を変更する時

関連: [プロダクト仕様](../product-specs/meal-planning-assistant.md)、[既存の利用入口と保存方式](2026-07-14-meal-planning-interface.md)、[アーキテクチャ](../../ARCHITECTURE.md)、[公開ワークフロー](../../.github/workflows/pages.yml)、[公開HTML](../../meal-history.html)

## 背景

自己完結HTMLはローカルブラウザで閲覧できるが、利用者は作成済みHTMLをGitHub PagesのURLから開けるようにしたい。献立履歴の正本や利用者設定を公開せず、追加のWebアプリ、サーバー、実行時依存を導入しない配備境界が必要である。

## 決定

`main`の`meal-history.html`をGitHub ActionsからGitHub Pagesへ静的配備する。配備時にこのファイルだけを`index.html`へコピーし、Pages artifactへ格納する。公開元の正本は[ワークフロー](../../.github/workflows/pages.yml)とし、`main`上のHTML変更時および手動実行時に配備する。

`config/preferences.json`、`data/plans/`、Pythonソース、リポジトリ内のその他のファイルはPages artifactへ含めない。公開HTMLはインターネット上の公開情報として扱い、機微情報を含めないことを公開前に確認する。履歴JSONは引き続き正本であり、公開HTMLは明示的に再生成・レビューする派生物とする。

## 検討した選択肢

| 選択肢 | 採用しない／採用する理由 |
| --- | --- |
| GitHub Actionsから単一HTMLだけをPages artifactとして配備（採用） | 公開対象を1ファイルへ限定でき、履歴JSONや利用者設定を誤って配信しにくい。既定ブランチへの変更をレビューしてから公開できる。 |
| リポジトリ全体またはルートディレクトリを配備 | 設定や将来追加されるファイルまで公開対象になりやすく、必要なHTML以外を配信する。 |
| `gh-pages`ブランチを手作業で更新 | 同じHTMLの複製と手順依存が増え、公開内容と変更履歴の対応を追いにくい。 |
| サーバー型Webアプリとして配備 | 動的更新は可能だが、認証、運用、追加依存、データ保護が必要になり、作成済みHTMLの表示という目的を超える。 |

## 影響

- `https://ka-murata.github.io/meal-schedule/`から作成済み献立HTMLを閲覧できる。
- 公開HTMLを更新するには、履歴から`meal-history.html`を再生成し、レビューを経て`main`へ反映する必要がある。
- HTMLに含まれる献立、材料、メモは公開情報になる。チェック状態は従来どおりブラウザ内の一時状態である。
- 初回のみ、リポジトリ設定でPagesの公開元を「GitHub Actions」にする必要がある。

## 守り方

- [公開ワークフロー](../../.github/workflows/pages.yml)は`meal-history.html`だけを`_site/index.html`としてartifactへ格納する。
- [品質条件](../QUALITY.md)にワークフロー構文、artifact内容、公開URLの確認を記録する。
- 公開前レビューでHTMLに機微情報や外部通信がないことを確認する。HTMLのエスケープと自己完結性は[自動テスト](../../tests/test_meal_schedule.py)で守る。
