# 5ch/X コメント抽出・動画生成アプリケーション 要件分析

## 1. プロジェクト概要

本プロジェクトは、5chのスレッドやX(Twitter)の投稿・スレッドURLからコメントを抽出し、音声合成と画像を組み合わせて動画を生成するWEBアプリケーションを開発するものです。ユーザーはURLを入力するだけで、コメントの抽出から音声合成、画像検索、動画生成までの一連の流れを自動化できます。

## 2. 主要機能と技術要件

### 2.1 コメント抽出機能
- **対応プラットフォーム**: 5ch、X(Twitter)
- **抽出方法**: 
  - 5ch: HTMLパース（APIなし）
  - X(Twitter): API利用（ユーザー提供のAPIキー）
- **特記事項**: 
  - 5chの1コメ（スレッド本文）をイントロとして使用
  - イントロが長い場合（25秒超）は自動短縮

### 2.2 音声合成機能
- **主要エンジン**: 
  - OpenAI gpt-4o-mini-tts（デフォルト）
  - fish.audio（オプション）
- **機能要件**:
  - コメント単位での話者指定
  - 連続同一話者回避ロジック
  - 音声パラメータ調整（速度・ピッチ等）

### 2.3 画像検索・ダウンロード機能
- **検索エンジン**: Google画像検索（Apify等の外部APIを利用）
- **機能要件**:
  - キーワードベースの画像検索
  - 画像一覧のプレビュー・選択
  - 画像フィルタ処理（モノクロ/セピア等）

### 2.4 動画生成機能
- **ベースライブラリ**: diffusionstudio/core
- **機能要件**:
  - 画像スライドショー生成
  - 音声とBGMの合成
  - 字幕表示（太めのゴシックフォント）
  - MP4形式での出力

## 3. システムアーキテクチャ

### 3.1 フロントエンド
- **フレームワーク候補**: React/Vue.js
- **主要コンポーネント**:
  - URL入力フォーム
  - コメント編集・話者選択UI
  - 画像検索・プレビューUI
  - 動画生成設定・プレビューUI

### 3.2 バックエンド
- **言語候補**: Python（diffusionstudio/coreとの互換性を考慮）
- **フレームワーク候補**: FastAPI/Flask
- **主要モジュール**:
  - コメント抽出モジュール
  - 音声合成モジュール
  - 画像検索モジュール
  - 動画生成モジュール

### 3.3 データフロー
1. ユーザーがURLを入力
2. バックエンドがコメントを抽出
3. 音声合成エンジンがコメントを音声化
4. 画像検索エンジンが関連画像を取得
5. 動画生成エンジンが音声・画像・字幕を合成
6. 生成された動画をユーザーに提供

## 4. 技術的課題と対応策

### 4.1 5chからのコメント抽出
- **課題**: 公式APIがない
- **対応策**: HTMLスクレイピングライブラリ（BeautifulSoup等）を使用

### 4.2 X(Twitter)からのコメント抽出
- **課題**: API制限、認証要件
- **対応策**: ユーザー提供のAPIキーを使用、レート制限を考慮した設計

### 4.3 音声合成の品質と多様性
- **課題**: 自然な音声生成、話者の多様性
- **対応策**: 複数のTTSエンジン対応、パラメータ調整機能

### 4.4 画像検索の関連性
- **課題**: コンテンツに関連する適切な画像の取得
- **対応策**: キーワード最適化、ユーザーによる選択機能

### 4.5 動画生成の処理負荷
- **課題**: 処理時間、サーバーリソース
- **対応策**: 非同期処理、ジョブキュー、進捗表示

## 5. 開発アプローチ

### 5.1 ベースリポジトリ
- **GitHub**: [agentic_video_generator](https://github.com/dylanler/agentic_video_generator)
- **拡張点**:
  - 日本語音声生成機能の追加
  - 画像収集機能の強化
  - 5ch/X対応のコメント抽出機能

### 5.2 開発フェーズ
1. **要件分析と設計**: システム設計、API設計、UI/UX設計
2. **モジュール開発**: 各機能モジュールの個別開発
3. **統合テスト**: モジュール間の連携テスト
4. **UI実装**: フロントエンド開発
5. **デプロイ準備**: インフラ構築、デプロイスクリプト作成

### 5.3 テスト戦略
- **単体テスト**: 各モジュールの機能テスト
- **統合テスト**: モジュール間連携テスト
- **エンドツーエンドテスト**: 実際のURLからの動画生成フロー

## 6. 非機能要件への対応

### 6.1 パフォーマンス
- 非同期処理によるレスポンス向上
- ジョブキューによる処理の分散

### 6.2 セキュリティ
- APIキーの安全な管理
- 入力検証によるインジェクション対策

### 6.3 拡張性
- モジュール化された設計
- プラグイン方式によるコメントソース追加

### 6.4 運用・保守性
- ログ管理
- エラーハンドリング
- データ保持期間の管理

## 7. 今後の検討事項

- YouTubeコメント等の追加ソース対応
- 生成コンテンツのSNSシェア機能
- テロップのカスタマイズ拡張
- 音声合成の感情パラメータ対応
