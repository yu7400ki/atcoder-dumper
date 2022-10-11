# atcoder-dumper

## 概要

ユーザー名・結果・言語を指定して、AtCoderに提出したコードを保存し、コミットするCUIツールです。

GitとPythonが使用可能なことが前提です。

## インストール方法

```
pip install git+https://github.com/yu7400ki/atcoder-dumper.git
```

## 使い方

使用可能なコマンド

```
atcoder-dumper init
atcoder-dumper dump
```

1. 初期化

コードを保存したいディレクトリに移動して、`atcoder-dumper init`を実行してください。

```
> atcoder-dumper init
Please enter your atcoder.jp username:
Initialized successfully.
```

2. (設定ファイルの編集)

`atcoder-dumper init`を実行すると、以下のような設定ファイルが生成されます。

```json
{
    "atcoder.jp": {
        "username": "",
        "filter": {
            "result": [],
            "language": []
        }
    }
}
```

`username`には、初期化時に設定したusernameが入ります。

`result`には、保存したい提出結果を記入します。空欄の場合は全ての結果が対象となります。

`language`には、保存したい言語を記入します。空欄の場合は全ての言語が対象となります。

記入例

```json
{
    "atcoder.jp": {
        "username": "yu7400ki",
        "filter": {
            "result": ["AC"],
            "language": ["PyPy3 (7.3.0)", "Python (3.8.2)"]
        }
    }
}
```

3. コードの保存

`atcoder-dumper dump`を実行するとダウンロードが始まります。

おおよそ2秒に1回ダウンロードを行います。

## License

MIT
