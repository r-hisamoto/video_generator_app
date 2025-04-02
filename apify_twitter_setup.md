# Apify Twitter抽出機能の設定方法

## 概要
このドキュメントでは、5ch/X コメント抽出・動画生成アプリにおいて、Apifyの「twitter-replies-scraper」アクターを使用したTwitter（X）コメント抽出機能の設定方法について説明します。

## 必要なもの
1. Apify APIキー
2. TwitterのCookies情報

## Apify APIキーの取得方法
1. [Apify](https://apify.com/)にアクセスし、アカウントを作成またはログインします。
2. ダッシュボードから「Account」→「Integrations」を選択します。
3. 「API」セクションからAPIキーを取得します。

## TwitterのCookies情報の取得方法
1. Google Chromeに[Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)拡張機能をインストールします。
2. Twitterにログインします。
3. Cookie-Editor拡張機能をクリックし、「Export」ボタンをクリックします。
4. JSONフォーマットのCookies情報がクリップボードにコピーされます。

## 設定方法
1. プロジェクトのルートディレクトリに`.env`ファイルを作成または編集します。
2. 以下の設定を追加します：

```
# Apify設定
APIFY_API_KEY=あなたのApifyAPIキー
TWITTER_COOKIES={"取得したCookies情報をここに貼り付け"}
USE_APIFY_FOR_TWITTER=true
```

3. `TWITTER_COOKIES`の値は、Cookie-Editorから取得したJSON文字列をそのまま貼り付けます。
4. `USE_APIFY_FOR_TWITTER`を`true`に設定すると、TwitterのコメントはApifyを使用して抽出されます。`false`に設定すると、従来のTwitter APIを使用します。

## 注意事項
- TwitterのCookiesは定期的に更新される可能性があります。抽出が失敗する場合は、Cookiesを再取得してください。
- Apifyの無料プランには使用制限があります。大量のデータを抽出する場合は、有料プランへのアップグレードを検討してください。
- Cookiesには個人情報が含まれるため、安全に管理してください。`.env`ファイルをGitリポジトリにコミットしないよう注意してください。

## テスト方法
設定が正しく行われているかを確認するには、以下のコマンドを実行します：

```bash
python tests/test_twitter_apify_extractor.py
```

正常に動作すれば、指定したツイートとそのリプライが表示されます。
