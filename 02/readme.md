ローカルネットワーク内でのキャプティブポータル構築について、各ステップを具体的に説明します。以下では、Linuxサーバー（Ubuntu）を使用した例を挙げますが、他のOSでも同様の手順で実行可能です。

### 1. **サーバーの準備（Webサーバーの設定）**

キャプティブポータルのHTMLページをホストするために、NginxまたはApacheをインストールします。

**Nginxのインストールと設定:**

```bash
sudo apt update
sudo apt install nginx
```

Nginxがインストールされたら、デフォルトのポート80で動作します。次に、キャプティブポータル用のシンプルなHTMLページを作成します。

```bash
sudo nano /var/www/html/index.html
```

**index.htmlの内容（例）:**

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>キャプティブポータル</title>
</head>
<body>
    <h1>ネットワーク利用のためにこのページをご確認ください</h1>
    <p>ここに利用規約や認証方法を表示します。</p>
</body>
</html>
```

### 2. **DHCPサーバーの設定**

次に、ローカルネットワーク内のクライアントにIPアドレスを割り当てるためのDHCPサーバーを設定します。`dnsmasq`は、軽量で設定が簡単なDNS/DHCPサーバーとして便利です。

**dnsmasqのインストール:**

```bash
sudo apt install dnsmasq
```

**dnsmasq設定ファイルの編集:**

```bash
sudo nano /etc/dnsmasq.conf
```

**設定内容の例:**

```bash
# DHCP範囲の設定（192.168.1.50〜192.168.1.150に割り当てる）
dhcp-range=192.168.1.50,192.168.1.150,12h

# キャプティブポータルサーバーのIPアドレス
dhcp-option=3,192.168.1.1
dhcp-option=6,192.168.1.1
```

### 3. **DNSリダイレクト**

キャプティブポータルにすべてのリクエストをリダイレクトするため、DNSを設定します。dnsmasqを使って、すべてのドメイン名をキャプティブポータルサーバーに解決させます。

**dnsmasqの設定に追加:**

```bash
# すべてのドメイン名をキャプティブポータルサーバーのIPにリダイレクト
address=/#/192.168.1.1
```

これにより、ユーザーがどのURLにアクセスしても、キャプティブポータルのサーバー（192.168.1.1）にリダイレクトされるようになります。

### 4. **ファイアウォールの設定**

次に、iptablesを使ってファイアウォールを設定し、クライアントがキャプティブポータルページを経由しない限り、インターネットや他のネットワークへのアクセスを制限します。

**iptablesルールの設定:**

```bash
# 既存のルールをクリア
sudo iptables -F

# HTTPトラフィックを許可
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# ローカルネットワーク内でのアクセスを許可
sudo iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT

# 他のすべてのアクセスをブロック
sudo iptables -A INPUT -j REJECT
```

これにより、キャプティブポータルページにはアクセスできますが、他のリソースへのアクセスは制限されます。

### 5. **ポータルページのデザイン**

最後に、ポータルページをカスタマイズします。認証システムや利用規約ページをHTMLやJavaScriptで設計します。

#### シンプルな例（ログインフォーム）:

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ログイン</title>
</head>
<body>
    <h1>ネットワークアクセスのためにログインしてください</h1>
    <form action="/login" method="post">
        <label for="username">ユーザー名:</label>
        <input type="text" id="username" name="username">
        <label for="password">パスワード:</label>
        <input type="password" id="password" name="password">
        <button type="submit">ログイン</button>
    </form>
</body>
</html>
```

フォームを作成する場合、バックエンドのサーバー側で認証処理を実装する必要があります。

### 6. **動作確認**

すべての設定が完了したら、ローカルネットワークにデバイスを接続し、Webブラウザを開いて、任意のURLにアクセスしてみます。アクセスがすべてキャプティブポータルページにリダイレクトされることを確認してください。

---

以上の手順で、ローカルネットワーク内にキャプティブポータルを構築できます。