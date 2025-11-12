# promptfoo コードレビュー評価

## 使い方

```bash
# インストール
npm install

# 認証（API従量課金）
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# 実行
npx promptfoo eval
npx promptfoo view
```

## 重要な注意

**Claude Codeのサブスクリプション認証は使えません。**

詳細は [AUTHENTICATION_INVESTIGATION.md](./AUTHENTICATION_INVESTIGATION.md) を参照。
