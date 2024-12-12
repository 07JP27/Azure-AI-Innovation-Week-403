# DEMO3 : Promptyを使ったプロンプトの読み込み

## ローカル実行方法
1. PythonおよびGitの環境を用意します。（オプションとしてpyenvを使うこともできます。）

1. リポジトリをクローンします。
1. Azure OpenAIのリソースを作成し、GPT-4oのデプロイを作成します。[参考](https://learn.microsoft.com/ja-jp/azure/ai-services/openai/how-to/create-resource?pivots=web-portal)
1. Entra ID認証を使用するために、実行ユーザーのEntra IDアカウントにAzure OpenAIのリソースのAzure OpenAI UserのRBACを付与します。（app.pyのコードを改変してAPIキー認証にすることもできます。[参考](https://learn.microsoft.com/ja-jp/azure/ai-services/openai/how-to/chatgpt?tabs=python-new#work-with-chat-completion-models)）
1. 端末にAzure CLIをインストールし、`az login`でログインします。
1. このディレクトリの.env-sampleを.envにリネームします。
1. .envにAzure OpenAIのエンドポイント、デプロイ名を設定します。
1. `pip install -r requirements.txt`で必要なライブラリをインストールします。
1. `stremlit run app.py`でアプリを起動します。
