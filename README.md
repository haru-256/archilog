# 💎 DevGist
[![Python CI](https://github.com/haru-256/devgist/actions/workflows/python-ci.yml/badge.svg)](https://github.com/haru-256/devgist/actions/workflows/python-ci.yml)
[![Terraform CI](https://github.com/haru-256/devgist/actions/workflows/terraform-ci.yml/badge.svg)](https://github.com/haru-256/devgist/actions/workflows/terraform-ci.yml)

<div align="center">
  <img src="docs/images/logo.png" width="500" alt="DevGist logo">
</div>

**「理論・実装・キャリアの分断を埋める、MLE/FDEのためのインテリジェンス・プラットフォーム」**

DevGistは、論文（Science）、技術ブログ（Engineering）、キャリア情報（Career）を収集・構造化し、エンジニアが「情報の海」で溺れる時間を減らし、「本質的な思考と意思決定」に集中できる世界を作るためのプラットフォームです。

## 🚀 Vision

**エンジニアが「情報の海」で溺れる時間を減らし、「本質的な思考と意思決定」に集中できる世界を作る。**

## ✨ Core Solutions

DevGistは、以下の3つの機能で「エンジニアの第2の脳」として機能します。

### ① 3層情報の集約と構造化 (Aggregation & Structuring)
世界中の情報を「Science」「Engineering」「Career」の3つのレイヤーで収集し、LLMが「読む前に」中身を構造化してデータベース化します。

### ② 能動的な「知見」検索 (Active RAG Search)
「リスト（検索結果）」ではなく「答え（知見）」を返す検索エンジン。論文とテックブログを横断して要約し、具体的な技術選定の理由や実装のヒントを即座に提示します。

### ③ 受動的な「未知」の発見 (Passive Discovery)
検索しなくても、「今の自分に必要な情報」が届くパーソナライズフィード。興味ベクトルを分析し、未知の論文や新しい技術トレンドをプッシュ通知します。

## 🛠 Architecture

DevGistは主に以下の4つのレイヤーで構成されています。

1. **データインジェクション & インテリジェンス・レイヤー**: arXivやテックブログからのデータ収集・構造化
2. **セマンティック・リトリーバル・レイヤー**: RAGを用いた能動的検索バックエンド
3. **パーソナライズ・フィードバック・レイヤー**: 行動ログに基づく推薦システム
4. **プロダクト・インターフェース**: 検索とフィードを統合したUI

## 🗺 Roadmap

- **Phase 1: Deep Search** - 検索機能の確立 (Science RAG, Engineering Bridge)
- **Phase 2: Discovery Feed** - 受動的発見の構築 (Personalized Feed)
- **Phase 3: Holistic Platform** - 全方位統合 (Career & Life)

## 📚 Documentation

詳細な設計思想や仕様については、以下のドキュメントを参照してください。

- [Design Doc](docs/design_doc.md)
