---
title: サーバーレス生成AIアプリの育てかた：OCI Generative AI + Functions + API Gateway + Gradio Lite 編
tags: oracle LLM AI serverless Python
author: yuji-arakawa
slide: false
---
## この記事は何？
__サーバーレスコンピューティング__ で実現する __生成AIアプリケーション__ の作り方を紹介します。
<table>
<tr>
<td>
<a href="https://youtu.be/K4IcTKegWj8">
    <img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/6361e77b-7b55-03cd-7cda-abc67361888c.jpeg" alt="サーバーレス生成AIアプリの育てかた：OCI Generative AI + Functions + API Gateway + Gradio Lite 編" height="256" width="256">
</a>
</td>
<td>
このブログの概要を80秒でご紹介する動画です<BR>（画像をクリックしてください）
</td>
</table>

大規模言語モデル（LLM）のAPIサービス、FaaS（Function-as-a-Service）、APIゲートウェイサービスとサーバーレスなUIフレームワークの __Gradio Lite__ を組み合わせて end-to-end でサーバーレスコンピューティングを活用したアプリケーションをステップバイステップで育てていきます
この記事では、生成AIアプリケーション自体は、入力された文章をLLMを使って日英、もしくは、日本語以外から日本語へ翻訳するシンプルなアプリケーションを例にしています

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/af181d29-7fad-02e9-cf07-fa265e8107cf.png)

:::note
この記事で使用しているコードはすべて記事内に記載していますが GitHub でも公開していますのでご活用ください

https://github.com/kutsushitaneko/serverless_generative_ai_gradio_lite


```bash:サンプルコードリポジトリのクローン
git clone https://github.com/kutsushitaneko/serverless_generative_ai_gradio_lite
cd serverless_generative_ai_gradio_lite
```
:::

## アーキテクチャ
この記事で作成するサーバーレス生成AIアプリのアーキテクチャは、下図のとおりです

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/8559b8c2-6a5a-ac9f-02cf-3d3ee9b5a629.png)


## 活用するサービス
このアーキテクチャを実装するために以下のようなサービスやフレームワークを活用します

### 大規模言語モデル（LLM） の API サービス
LLM の推論機能を クラウドベースの API で利用できるサービスとして、OCI Generative AI サービスを利用します。OCI Generative AI サービスは、Cohere 社や Meta 社の LLM や 埋め込みモデル（Emedding Model）を API で利用できるサービスです。課金体系は、コンサンプションベースの課金で利用できるオンデマンドに加えて、専用クラスタ構成でのサービスもありテナント（アカウント）に閉じたセキュアで安定した性能を確保できる環境を利用することもできます。今回は、LLM として、Cohere の Command R+ をオンデマンドで使用します。オンデマンドサービスは、LLMをホストする仮想マシンやクラスタをプロビジョニングする必要なく、APIを呼び出すことですぐに利用することができます。

[OCI Generative AI（生成AI）の 公式ドキュメント](https://docs.oracle.com/ja-jp/iaas/Content/generative-ai/home.htm)

### FaaS（Function-as-a-Service）

<img width="100%" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/3065885c-c989-5c9f-680f-7c400d29110f.png">


ビジネスロジックを実行するサーバーレスコンピューティングプラットフォーム（Function-as-a-Service:FaaS）には、OCI Functions を利用します。OCI Functions は、オープンソースのサーバーレスコンピューティングフレームワークの Fn Project をOCI クラウドのマネージドサービスで利用できるものです。コンテナが稼働する仮想マシンなどのサーバー環境をあらかじめ準備する必要がなく、Java や Python などのプログラムを実行することができます。また、スケールアウトもサービス側で自動的に行われるためスケーラブルなアプリケーションを構築することができます。なお、OCIのドキュメントの中では、"Functions"、"ファンクション"、"関数"などと表現されています。この記事では原則的にサービス名は "Functions"、実行される個々のプログラムを"ファンクション"と表現しています。

[OCI Functions（ファンクション：関数）の 公式ドキュメント](https://docs.oracle.com/ja-jp/iaas/Content/Functions/home.htm)

### APIゲートウェイサービス
バックエンドのアプリケーションを REST API として公開し、ロードバランシングなどの機能を提供するAPIゲートウェイサービスとしては、OCI API Gateway を利用します。ロードバランサや API サーバーを自分で構築する必要なく OCI クラウドのマネージドサービスで APIゲートウェイ機能を利用できるサービスです。OCI API Gatewayを活用することでバックエンドの機能を直接インターネットにさらす必要がなくなる上、APIゲートウェイ自体のスケールアウトもサービス側で自動的に実行されるためセキュアでスケーラブルな API サービスを開発することができます。

[OCI API Gateway（API ゲートウェイ）の 公式ドキュメント](https://docs.oracle.com/ja-jp/iaas/Content/APIGateway/home.htm)

### サーバーレスなUIフレームワーク
機械学習／生成AI分野のデモアプリケーションや PoC のプロトタイプ開発において、Python ベースの UI 開発ツールとして Gradio が人気です。この Gradio のサーバーレス版である __Gradio Lite__ を使用します。Python コードを HTML ファイルに埋め込むことで、コードをブラウザ内で実行することができフロントエンドを稼働させるサーバーが不要です。UIを手軽に構築できるフレームワークとしてとても便利なものです。

[Gradio Lite の公式ドキュメント](https://www.gradio.app/guides/gradio-lite)

### オブジェクトストレージ
Gradio Lite の HTML ファイルを公開するための Webサーバーとして、 OCI Object Storage サービスを利用します。バケットに HTML ファイルをアップロードして公開することで Webサーバーとして機能させることができます。

[OCI Object Storage（オブジェクト・ストレージ） の公式ドキュメント](https://docs.oracle.com/ja-jp/iaas/Content/Object/home.htm)

## 事前準備：ユーザーに対する IAM のポリシー設定
:::note
ポリシーとは？
OCIでは、ユーザーがサービスへアクセスできるかどうか、サービスが他のサービスへアクセスできるかどうかを「ポリシー」を利用して制御します。ポリシーは、各リソースに誰（もしくはどのリソース）がアクセスできるかを指定することができます。 
:::
使用するユーザーがOCIの各サービスへのアクセス権を持っていない場合には、ポリシーを設定してアクセス権を付与する必要があります。

:::note warn
サービスへのアクセス権がない場合には、コンソールにアクセスした際、もしくは、何か操作した際に下記の2つの画像のような表示が出ます。
テナンシ管理者へ連絡して必要なポリシーを設定してもらいましょう。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/ea7fab8b-e7a9-12d9-fcf2-0d900701a668.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/c3839314-2481-2988-5d03-4fbfd7c598ce.png)

### OCI Functions（ファンクション、関数） へのアクセス権の設定

OCI公式チュートリアル【Oracle Functions ハンズオン】の[事前準備](https://oracle-japan.github.io/ocitutorials/cloud-native/functions-for-beginners/#%E4%BA%8B%E5%89%8D%E6%BA%96%E5%82%99) を参考にポリシーを設定します

OCI公式ドキュメントは [ネットワークおよびファンクション関連リソースへのアクセスを制御するポリシーの作成](https://docs.public.oneportal.content.oci.oraclecloud.com/ja-jp/iaas/Content/Functions/Tasks/functionscreatingpolicies.htm#userfunctionpolicy) です

### OCI Generative AI（生成AI） へのアクセス権の設定

OCI公式ドキュメントの[生成AIへのアクセス](https://docs.oracle.com/ja-jp/iaas/Content/generative-ai/iam-policies.htm) を参考にポリシーを設定します


### OCI API Gateway へのアクセス権の設定

OCI公式ドキュメントの[ネットワークおよびAPIゲートウェイ関連リソースへのアクセスを制御するポリシーの作成](https://docs.public.oneportal.content.oci.oraclecloud.com/ja-jp/iaas/Content/APIGateway/Tasks/apigatewaycreatingpolicies.htm) を参考にポリシーを設定します

### OCI Object Storage へのアクセス権の設定

OCI公式ドキュメントの[オブジェクト・ストレージ、アーカイブ・ストレージおよびデータ転送の詳細](https://docs.oracle.com/ja-jp/iaas/Content/Identity/policyreference/objectstoragepolicyreference.htm) を参考にポリシーを設定します
:::

## OCI Functions の開発環境のセットアップ
:::note
OCI Functions の開発環境のセットアップ手順は、OCI公式チュートリアル【Oracle Functions ハンズオン】の[1.Cloud Shellのセットアップ](https://oracle-japan.github.io/ocitutorials/cloud-native/functions-for-beginners/#1cloud-shell%E3%81%AE%E3%82%BB%E3%83%83%E3%83%88%E3%82%A2%E3%83%83%E3%83%97)を参考にしています
:::
### 必要な情報の収集
#### 認証トークンの作成
:::note
Oracle Cloud Infrastructure Registry(OCIR)にログインするための認証トークンを作成します。OCIRは、OCI 提供のプライベートDockerイメージレジストリで、今回は、Oracle Functionsのファンクションのイメージを保存するために使用します
:::

##### 手順
OCIダッシュボードの画面右上の人型のマークをクリックします。テナンシの認証管理システムにより下図のどちらかの形式でプロファイルメニューが表示されます。「アイデンティティ・ドメイン：XXXX」という項目の有無で見分けます

<table>
<tr>
<td>

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/6f2869fb-c948-cd76-e706-ccd2d25f35bb.png)
</td>
<td>

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/487cb47b-d9c9-f846-0f6d-d3181312e00b.png)
</td>
</tr>
<tr>
<td>
アイデンティティ・ドメイン
</td>
<td>
IDCS/フェデレーション
</td>
</tr>
</table>

###### アイデンティティ・ドメインの場合の手順
- "アイデンティティ・ドメイン：xxxx"の下の __"自分のプロファイル"__ をクリックします
- "自分のプロファイル" 画面の左下のメニューから __"認証トークン"__ をクリックします
- __”トークンの生成”__ をクリックします

###### IDCS/フェデレーションの場合の手順
- "プロファイル"の"直下の __ユーザー名__ をクリックします
- "ユーザーの詳細"画面の左側のメニューで、 __”認証トークン”__ をクリックします
- __”トークンの生成”__ をクリックします

###### 共通の手順
次のような画面が表示されているはずです

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/245552be-930a-db77-5f61-5dea251059a8.png)

“説明”に"GenAI Translate ファンクション用"等の説明文を入力し、”トークンの生成”をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/1f643e4e-e938-b7bb-ea87-076cbf944a55.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/a9e4299e-e500-37c7-c098-80f52ebfa78a.png)
"コピー"をクリックしてトークンをクリップボード経由でメモ帳などに転記します

#### コンパートメントOCIDの確認
- OCIダッシュボードの画面左上のナビゲーション・メニュー（ハンバーガー・メニュー）から"アイデンティティとセキュリティ"⇒"コンパートメント"の順に選択します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/b37a2ebf-a7c4-1996-b3e9-b419efe973d7.png)
- 使用するコンパート名をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/403f2a37-df11-2780-5158-a0b81701521a.png)
- __"コピー"__ をクリックしてOCIDをクリップボード経由でメモ帳などに転記します


#### オブジェクト・ストレージ・ネームスペースの確認

- OCIダッシュボードの画面右上の人型のマークをクリックし、テナンシをクリックして、"テナンシ詳細"を表示します
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/18110a72-c20e-596e-01b5-4acf15c2cb66.png)
- 右側の __"オブジェクト・ストレージ設定"のオブジェクト・ストレージ・ネームスペース:__ に表示されている文字列をメモ帳などに転記します

### Cloud Shell の起動
ここでは、Cloud Shell を開発環境しとして使用します
- OCIダッシュボードの右上の"開発者ツール"アイコンをクリックして"Cloud Shell"を選択します
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/b8305256-4d53-33a5-b652-6b55880e44d0.png)
- ダッシュボードの下部にCloud Shell が表示されます

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/792bae88-5d55-2654-c7a8-e91dd26ec37d.png)

### OCI Functions CLI context の設定
:::note
OCI Functions CLI contextは、OCI Functionsを使用するための設定情報をまとめたものです。以下のような情報を設定します
- 使用するOCIリージョン
- ファンクションをデプロイするコンパートメントID
- OCIRのアドレス
- 認証情報
:::
:::note
Cloud Shell には事前に CLI context が設定されています
:::

#### 現在の CLI context を確認
Cloud Shell で以下のコマンドを実行します
```bash:CLI context の確認
fn list context
```
```bash:出力例
$ fn list context
CURRENT NAME            PROVIDER        API URL                                                 REGISTRY
*       ap-tokyo-1      oracle-cs       https://functions.ap-tokyo-1.oci.oraclecloud.com
        default         oracle-cs
        us-chicago-1    oracle-cs       https://functions.us-chicago-1.oci.oraclecloud.com
```

__"\*"__  が付いている context が現在の CLI context です。これからご利用されるリージョンと異なる context に "*" が付いている場合は、次のコマンドで適切な context を選択します

```bash:CLI context の選択
fn use context <region-context>
```

```bash:実行例
$ fn use context us-chicago-1
Now using context: us-chicago-1

$ fn list context
CURRENT NAME            PROVIDER        API URL                                                 REGISTRY
        ap-tokyo-1      oracle-cs       https://functions.ap-tokyo-1.oci.oraclecloud.com
        default         oracle-cs
*       us-chicago-1    oracle-cs       https://functions.us-chicago-1.oci.oraclecloud.com
```

#### CLI context にコンパートメントIDを設定
```bash:コンパートメントIDの設定
fn update context oracle.compartment-id [compartment-ocid]
```
[compartment-ocid]は、先程確認してメモしたコンパートメントIDです。[]は不要です

```bash:実行例
$ fn update context oracle.compartment-id ocid1.compartment.oc1..xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Current context updated oracle.compartment-id with ocid1.compartment.oc1..xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### CLI context に OCIR を設定
```bash:OCIRの設定
fn update context registry [region-key].ocir.io/[tenancy-namespace]/[repo-name-prefix]
```
- [region-key] : 利用するリージョンのコード。[]は不要です
:::note
region-keyは、[こちら](https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm) で確認できます
:::
:::note alert
region-key は英小文字で入力します。大文字で入力するとファンクションの OCIRへのデプロイに失敗します
:::
- [tenancy-namespace] : 先程確認してメモしたオブジェクト・ストレージ・ネームスペース。__テナンシの名前ではありません__
- [repo-name-prefix] : （オプション）ファンクションのイメージを格納するOCIR(Oracle Cloud Infrastructure Registry)リポジトリの任意のプレフィックス。リポジトリ名とプレフィックス（接頭辞）についてはドキュメントの[リポジトリ名およびリポジトリ名の接頭辞に関するノート](https://docs.public.oneportal.content.oci.oraclecloud.com/ja-jp/iaas/Content/Functions/Tasks/functionscreatefncontext.htm#Create_an_Fn_Project_CLI_Context_to_Connect_to_Oracle_Cloud_Infrastructure__section_repository_name_notes)を参照

```bash:実行例（シカゴリージョンの例）
$ fn update context registry ord.ocir.io/xxxxxxxxxx/ya_genai
Current context updated registry with ord.ocir.io/xxxxxxxxxx/ya_genai
```

```bash:CLI context の OCIR レジストリの確認
fn list context
```

```bash:実行例
$ fn list context
CURRENT NAME            PROVIDER        API URL                                                 REGISTRY
        ap-tokyo-1      oracle-cs       https://functions.ap-tokyo-1.oci.oraclecloud.com
        default         oracle-cs
*       us-chicago-1    oracle-cs       https://functions.us-chicago-1.oci.oraclecloud.com      ord.ocir.io/orasejapan/ya_genai
```

#### CLI context に OCI CLI プロファイルを設定
このCLI context で使用する OCI CLI プロファイルを設定します

```bash:CLI context の OCI CLI Profileの設定
fn update context oracle.profile "プロファイル名"
```
Cloud Shell が自動的にセットアップした OCI CLI Profile は、/etc/oci/config に定義されています
以下は、DEFAULTプロファイルを使用する例です
```bash:実行例
fn update context oracle.profile "DEFAULT"
```

#### CLI context 設定内容の確認
```bash:CLI context の確認
more ~/.fn/contexts/[CLI context].yaml
```
[CLI context] : `fn list context` で確認した現在（CURRENT）の CLI context の名前（NAME）

```bash:実行例
$ more ~/.fn/contexts/us-chicago-1.yaml
api-url: https://functions.us-chicago-1.oci.oraclecloud.com
oracle.compartment-id: ocid1.compartment.oc1..aaaaaaaaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
provider: oracle-cs
registry: ord.ocir.io/xxxxxxxxxx/ya_genai
```

#### OCIR へのログインの確認
```bash:OCIRへのログイン
docker login [region-key].ocir.io
```
このコマンドを実行すると __Username:__ と __Password:__ を聞かれますので以下のように応答します。
- __Username:__ は、OCIのIdentity and Access Management(IAM) サービスで直接作成および管理される IAM ユーザーの場合とOracle Identity Cloud Service (IDCS)と統合されたフェデレーテッド・ユーザーの場合で形式が異なります。__IAM ユーザーの場合は、[tenancy-namespace]/[username]__ の形式でユーザー名を応答します。__フェデレーテッド・ユーザーの場合は、oracleidentitycloudservice/[tenancy-namespace]/[username]__ の形式でユーザー名を応答します。
     - [tenancy-namespace] : オブジェクト・ストレージ・ネームスペース[tenancy-namespace]/
     - [username] : OCIコンソール画面右上の人型のアイコンをクリックし、展開されたメニューにある”プロファイル”直下に表示される文字列
-  __Password:__ には上で作成してメモした認証トークンを応答します
```bash:実行例（フェデレーテッド・ユーザーがシカゴリージョンを使う例）
$ docker login ord.ocir.io
Username: xxxxxxxxxx/oracleidentitycloudservice/XXXXXXXXXXXXXXXXXXXXXXXX
Password: 
WARNING! Your password will be stored unencrypted in /home/xxxxxxxx/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded
```
__"Login Succeeded"__ と表示されればログイン成功です
### VCN（仮想クラウドネットワーク） の作成
OCI Functionsのアプリケーションを動作させる仮想クラウドネットワークを作成します
- OCIのダッシュボードの画面左上のナビゲーション・メニュ（ハンバーガー・メニュー）から"ネットワーキング"⇒"仮想クラウド・ネットワーク"の順に選択します

![スクリーンショット 2024-08-19 140641.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/ff7cd822-0155-672f-8432-67bd31986ea2.png)
- 画面左側のメニューの下の方にあるプルダウンでコンパートメントを選択します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/4c27e894-6494-623b-ebec-17d619f0d280.png)

- "VCNウィザードの起動"をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/66ec7c2b-59e1-01a5-77d1-cf4f8fd3cd9b.png)

- “インターネット接続性を持つVCN”を選択し、”ワークフローの起動”をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/4912e688-487c-bcc9-2138-d58f240a9918.png)

- 以下の情報を入力します（CIDRなどは適宜変更してください）
    - VCN名：任意の名前(例：”OCI Generative AI Hands-on”)
    - コンパートメント：上で選択したコンパートメント名が表示されています
    - VCN CIDRブロック：10.0.0.0/16（デフォルト）
    - パブリック・サブネットCIDRブロック：10.0.0.0/24（デフォルト）
    - プライベート・サブネットCIDRブロック：10.0.1.0/24（デフォルト）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/043ba680-deaf-4813-e3af-8814fcd30f30.png)

- "次"をクリックします

- "確認および作成"画面で設定内容を確認したら“作成”をクリックします



![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/fa1d61b5-d6b7-0271-9380-0e1791c82a65.png)
- "VCNが作成されました"と表示されたら画面左下の"VCNの表示"をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/97fcb760-45ca-6315-7017-a6ecc987645d.png)
- VCNが"使用可能"となっていること、プライベートとパブリックの2つのサブネットがコンパートメント内に作成されていることを確認します

以上で、VCN（仮想クラウドネットワーク）が作成されました

## OCI Functions ファンクションの作成
### アプリケーションの作成
:::note
アプリケーションとは、複数のファンクションの論理グループで VCN や サブネットといった属性を共有するファンクションをまとめて管理するものです。ファンクションを作成する前に必ずアプリケーションを作成する必要があります
:::

- OCIのダッシュボードの画面左上のナビゲーション・メニュ（ハンバーガー・メニュー）から”開発者サービス”⇒”ファンクション”の順に選択します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/fb196d40-d8a2-349f-ca76-1bc0e64c9b74.png)
- ファンクション画面が表示されます

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/c4ab4bb9-2e3b-ef33-c95b-1fc021fc8a36.png)
- ”アプリケーションの作成”をクリックします
- 以下の情報を入力、選択します
    - 名前：OCI Functions アプリケーションの任意の名前を入力します（例："fn_genai_translate_app"）
    - XXXXXXXのVCN：（XXXXXXX）にはコンパートメント名がセットされています。プルダウンで先程作成した VCN を選択します
    - XXXXXXXのサブネット：（XXXXXXX）にはコンパートメント名がセットされています。プルダウンで先程作成した VCN のパブリックサブネットを選択します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/7579bfe7-d45b-c600-bfed-2bf91c509fb4.png)

- "作成"をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/fd677e0e-87d9-85b1-a9dc-f664d25caaa7.png)

以上で、OCI Functionsアプリケーションの作成は完了です。アプリケーションの中身は空です。次にこのアプリケーションに入れるファンクションを作成します

### ファンクションの作成
:::note
ファンクションとは？
Fn Project や OCI Functions におけるファンクションとは、Dockerイメージとしてレジストリに格納されて、HTTPリクエストやCLIによって呼び出されて実行されるコード・ブロックです
:::
このブログでは、Python でファンクションを開発します

- ファンクションの初期化

```bash:Pythonを使ったファンクションの初期化
fn init --runtime [programming language runtime] [function-subdirectory]
```
- fn init のパラメータ
    - [programming language runtime] : ファンクションのランタイム
    - [function-subdirectory] : サンプルコードや設定ファイル等を配置するディレクトリ

```bash:実行例（ランタイムに Python を使う場合）
$ fn init --runtime python genai_translate_func
Creating function at: ./genai_translate_func
Function boilerplate generated.
func.yaml created.

$ ls genai_translate_func
func.py  func.yaml  requirements.txt

```
`fn init` のリファレンスは[こちら](https://github.com/fnproject/docs/blob/master/cli/ref/fn-init.md)

Python のファンクションを初期化するとサンプル Python スクリプト（func.py）、設定ファイル（func.yaml）、requirements.txt が生成されます
```bash:サンプルコードの確認
$ cat genai_translate_func/func.py 
import io
import json
import logging

from fdk import response


def handler(ctx, data: io.BytesIO = None):
    name = "World"
    try:
        body = json.loads(data.getvalue())
        name = body.get("name")
    except (Exception, ValueError) as ex:
        logging.getLogger().info('error parsing json payload: ' + str(ex))

    logging.getLogger().info("Inside Python Hello World function")
    return response.Response(
        ctx, response_data=json.dumps(
            {"message": "Hello {0}".format(name)}),
        headers={"Content-Type": "application/json"}
    )
```

### ファンクションのデプロイ
ここでは一旦サンプル Python スクリプトのファンクションをデプロイして、OCIRへプッシュされることを確認します
```bash:デプロイ
fn deploy --app [app-name] [function-subdirectory]
```
- [app-name] : 先程作成したアプリケーション名
- [function-subdirectory] : デプロイで指定したプロジェクトの サンプルコードやyaml ファイル等を配置するディレクトリ

```bash:実行例
$ fn deploy --app fn_genai_translate_app genai_translate_func
Deploying function at: ./genai_translate_func
Deploying genai_translate_func to app: fn_genai_translate_app
Bumped to version 0.0.4
Using Container engine docker
Building image ord.ocir.io/xxxxxxxxxx/ya_genai/genai_translate_func:0.0.4 TargetedPlatform:  amd64HostPlatform:  arm
........................................................................
Updating function genai_translate_func using image ord.ocir.io/xxxxxxxxxx/ya_genai/genai_translate_func:0.0.4...
Successfully created function: genai_translate_func with ord.ocir.io/xxxxxxxxxx/ya_genai/genai_translate_func:0.0.4
```

`fn deploy` のリファレンスは[こちら](https://github.com/fnproject/docs/blob/master/cli/ref/fn-deploy.md)


### デプロイの確認
#### OCIR にファンクションがアップロードされていることを確認
- OCIダッシュボードの左上ナビゲーションメニューから”開発者サービス”⇒”コンテナ・レジストリ”を選択します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/fe8c1d50-4c7b-cf57-05c1-7acd20d8baa0.png)

- OCIRのレジストリに先ほどデプロイしたファンクションがアップロードされていることを確認します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/20d881cc-1c54-6202-3877-03bd8331b09f.png)

- 左側の"Compartment" でルート・コンパートメントが選ばれていることを確認します。"リポジトリおよびイメージ"にリポジトリが表示されない場合は、"リポジトリおよびイメージ"直下のプルダウン（白い部分）をクリックします

#### OCI Functions アプリケーションにファンクションがデプロイされていることを確認
- OCIダッシュボードの左上ナビゲーションメニューから”開発者サービス”⇒”ファンクション”を選択します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/58148233-b2ba-4c45-7541-4980d39b2192.png)

- 左側の"コンパートメント"で __アプリケーションを作成したコンパートメント__ を選択します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/6d1886c4-25fe-85b5-964e-c7d5ebb91c0a.png)

- 右側のアプリケーションの一覧エリアに作成したアプリケーション名（例では fn_genai_translate_app）が表示されているはずです。このアプリケーション名をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/4a0e3c6a-3d6c-1221-0db0-96979714e0d8.png)


画面下部の"ファンクション"の下に先程作成したファンクション（例では、genai_translate_func）が表示されていればデプロイに成功しています

### ファンクションの実行
以下のコマンドを実行し、ファンクションが正常に実行されることを確認します
```bash:ファンクションの実行
fn invoke [app-name] [function-name] 
```
-[app-name] : アプリケーション名
-[function-name]  : ファンクション名

`fn invoke` のリファレンスは[こちら](https://github.com/fnproject/docs/blob/master/cli/ref/fn-invoke.md)

```bash:実行例
$ fn invoke fn_genai_translate_app genai_translate_func
{"message": "Hello World"}

$ echo -n '{"name": "Tokyo"}' | fn invoke fn_genai_translate_app genai_translate_func
{"message": "Hello Tokyo"}
```
### ファンクションの修正
サンプルの func.py をOCI Generative AI サービスの Cohere Command-R+ を呼び出すように修正して再度デプロイします

```python:新しい func.py - OCI Generative AI を呼び出すコード
import io
import json
import logging
import oci.auth.signers
import oci.generative_ai_inference
import os

from fdk import response

try:
    endpoint = os.getenv("OCI_GENAI_ENDPOINT")
    compartment_id = os.getenv("COMPARTMENT_OCID")
    model_id = os.getenv("OCI_GENAI_MODEL_ID")

    if not endpoint:
        raise ValueError("ERROR: Missing configuration key OCI_GENAI_ENDPOINT")
    if not compartment_id:
        raise ValueError("ERROR: Missing configuration key COMPARTMENT_OCID")
    if not model_id:
        raise ValueError("ERROR: Missing configuration key OCI_GENAI_MODEL_ID")

    signer = oci.auth.signers.get_resource_principals_signer()
    generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config={}, service_endpoint=endpoint, signer=signer,retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10,240))
except Exception as e:
   logging.getLogger().error(e)
   raise

def inference(message):
    logging.getLogger().info(f"messages:{message}")
    chat_request = oci.generative_ai_inference.models.CohereChatRequest()
    chat_request.message = f'''
    ##あなたは翻訳の専門家です。与えられた原文が日本語かどうかを判断して以下の指示のとおりに翻訳することが仕事です。
    ##以下の文章は翻訳対象の原文です。
    ##原文：{message}
    ##指示：以下のSTEPに従って原文を翻訳してください。
    ###STEP-1：原文が主に日本語であるかどうかを判断します。
    ###STEP-2：原文が主に日本語の場合は英語に翻訳します。
    ###STEP-3：原文が主に日本語以外の場合は日本語に翻訳します。
    ###STEP-4：以下の出力フォーマットに従って出力します。途中のSTEPの結果は出力しません。
    ##出力フォーマット：{{"input": "原文","output": "翻訳文"}}
    ##以下は原文とそれに対するあなたの出力の例です。
    ###Example-1：原文：こんにちは！
    出力：{{"input": "こんにちは！","output": "Hello!"}}
    ###Example-2：原文：Good morning.
    出力：{{"input": "Good morning.","output": "おはようございます。"}}
    '''
    chat_request.max_tokens = 2000
    chat_request.is_stream = False
    chat_request.temperature = 0.0
    chat_request.top_p = 0.7
    chat_request.top_k = 0 # Only support topK within [0, 500]
    chat_request.frequency_penalty = 1.0
    chat_request.is_echo = False

    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=model_id)
    chat_detail.compartment_id = compartment_id
    chat_detail.chat_request = chat_request

    try:
        chat_response = generative_ai_inference_client.chat(chat_detail)
        logging.getLogger().info(f"chat_response.text:{chat_response.data.chat_response.text}")
        return chat_response.data.chat_response.text
    except Exception as e:
        logging.getLogger().error(e)
        raise

def handler(ctx, data: io.BytesIO = None):
    logging.getLogger().info("handler is called")
    logging.getLogger().info(f"OCI_GENAI_MODEL_ID: {model_id}")
    try:
        body = json.loads(data.getvalue())
        message = body["message"]
    except (Exception, ValueError) as ex:
        logging.getLogger().info('error parsing json payload: ' + str(ex))     


    if not message.strip():
        return response.Response(
            ctx, response_data=json.dumps(
                {"message": "There is no text to translate."},
                ensure_ascii=False
            ),
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

    inference_response = inference(message)
    return response.Response(
        ctx, response_data=json.dumps(
            {"message": f"{inference_response}"},
            ensure_ascii=False
        ),
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
```

```python:新しい requirements.txt
fdk>=0.1.75
oci
```

OCI Generative AI サービスを使った Python アプリケーションの書き方については以下の記事を参考にしてみてください

https://qiita.com/yuji-arakawa/items/597c4bd9f3d5b4212b51

- この新しい func.py と requirements.txt をローカルに保存します
- 保存した func.py と requirements.txt を Cloud Shell にアップロードします。Cloud Shell の右上の歯車マークから"アップロード"を選択します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/1166996d-c4ff-e5f0-70d2-cf85d32ac475.png)

- ファイルは、ホームディレクトリはアップロードされます
- mv コマンドでプロジェクトディレクトリ（例では、genai_translate_func）へ移動します

```
mv func.py genai_translate_func/
mv requirements.txt genai_translate_func/
```

- 修正したファンクションをデプロイします

```bash:再デプロイコマンド
fn deploy --app fn_genai_translate_app genai_translate_func
```

再デプロイの実行例
```bash:再デプロイ実行例
$ fn deploy --app fn_genai_translate_app genai_translate_func
Deploying function at: ./genai_translate_func
Deploying genai_translate_func to app: fn_genai_translate_app
Bumped to version 0.0.7
Using Container engine docker
Building image ord.ocir.io/xxxxxxxxxx/ya_genai/genai_translate_func:0.0.7 TargetedPlatform:  amd64HostPlatform:  arm
...........................................................................................................................................................................................................................................................................................................................................
Updating function genai_translate_func using image ord.ocir.io/xxxxxxxxxx/ya_genai/genai_translate_func:0.0.7...
```

### 環境変数をアプリケーションの構成に設定
修正した func.py は、2つの環境変数 OCI_GENAI_ENDPOINT と COMPARTMENT_OCID を参照しています。ファンクションに環境変数を渡すためにアプリケーションの構成にキーと値と設定します

- 左上のナビゲーションメニューから"開発者サービス"⇒"アプリケーション"を選択します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/92c79449-67a5-6459-2a27-f257efc3a285.png)

- "アプリケーションの作成"の下の一覧エリアに表示されているアプリケーションの名前（例では、fn_genai_translate_app）をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/e366c581-e3df-9efb-879d-effe08f19b35.png)

- 画面左側の"リソース"の下の"構成"をクリックします
- キーと値の組み合わせに以下の3つを定義します
    - OCI_GENAI_ENDPOINT : https://inference.generativeai.us-chicago-1.oci.oraclecloud.com
    - COMPARTMENT_OCID : コンパートメントのOCID
    - OCI_GENAI_MODEL_ID ： 翻訳を実行する LLM のモデルID => "cohere.command-r-plus-08-2024"

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/7657e98e-6ce3-4325-a37d-c490023af74d.png)


### リソース・プリンシパルによる認証・認可設定
:::note warn
今回作成している生成AIアプリは、OCI Functios サービスのファンクションから OCI Generative AI サービスの大規模言語モデル（Cohere Command-R+）を呼び出して翻訳を行います。そのため、作成したファンクションに対して、OCI Generative AI サービスの推論機能にアクセスする権限を与える必要があります。
:::
:::note
OCI では、ユーザーに対する認証認可に加えてファンクションのようなサービスのリソースに対して認証認可を行うためのリソース・プリンシパルという機能があります。APIキーをプログラムコードや Docker イメージに埋め込む必要がなくセキュアにサービスを利用できます
:::
リソース・プリンシパルを使うためには、動的グループと、動的グループに権限を付与するIAMポリシーを作成する必要があります。OCI Functions におけるリソース・プリンシパルについては、OCIドキュメントの[ファンクションの実行による他のOracle Cloud Infrastructureリソースへのアクセス](https://docs.oracle.com/ja-jp/iaas/Content/Functions/Tasks/functionsaccessingociresources.htm) に詳しい説明があります
#### ファンクション用動的グループの作成
:::note
動的グループとは指定したルールに合致するリソースのグループです。動的とあるようにグループ作成後に作られたリソースであってもルールに合致すれば動的グループの一員となります。この動的グループに対して権限を与えるポリシーを付与することで柔軟かつ確実な権限管理を実現できます
:::
##### アイデンティティ・ドメインの場合の手順
- OCIダッシュボード左上のナビゲーションメニューから"アイデンティティとセキュリティ"⇒"ドメイン"⇒ドメイン名（"Defaultドメイン"等）⇒"動的グループ"を選択します
- "動的グループの作成"をクリックします

##### IDCS/フェデレーションの場合の手順
- OCIダッシュボード左上のナビゲーションメニューから"アイデンティティとセキュリティ"⇒"動的グループ"を選択します
- "動的グループの作成"をクリックします

##### 共通の手順
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/efe22397-f92e-6fd8-09f9-1e6652929264.png)

- 任意の名前を入力します（例：Functions-dg）
- 任意の説明を入力します（例：ファンクション動的グループ）
- 以下の一致ルールを入力します（この一致ルールは、リソースのタイプが OCI Functions（`resource.type='fnfunc'`） のファンクションで、リソースのコンパートメントが指定したコンパートメントIDを持つものをグループ化しています。`ocid1.compartment.oc1..aaaaaaaa...`の部分はファンクションを作成した際のコンパートメントのIDを指定します）
```text:Functions-dg
All {resource.type='fnfunc', resource.compartment.id = 'コンパートメントID'}
```
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/e93c74db-4a7a-75fd-ed2f-8954609dd95d.png)

- "作成"をクリックします

#### ファンクション用 IAM ポリシーの作成
ポリシーを作成して上で作成した動的グループ（例では、Functions-dg）に OCI Generative AI の推論エンドポイントを呼び出す権限を付与します

- OCIダッシュボード左上のナビゲーションメニューから"アイデンティティとセキュリティ"⇒"ポリシー"を選択します
- ポリシーの作成をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/54ff8f51-bc5a-c021-7338-755bcccc6c4c.png)

- 任意の名前を入力します（例：genai4functions-policy）
- 任意の説明を入力します（例：ファンクションに OCI GenAI の使用権限を与えるポリシー）
- ポリシー・ビルダーの右横の"手動エディタの表示"のスライダーを右にスライドして手動エディタを表示します
- 以下のポリシーを入力します
    - 動的グループ名は、上で作成したファンクション用動的グループの名前を指定します（例では、Functions-dg）
    - コンパートメント名は、ファンクションを作成したコンパートメントの名前を指定します
```text:genai4functions
allow dynamic-group 動的グループ名 to use generative-ai-family in compartment コンパートメント名
```
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/ce40b7a3-1556-9c36-0b7c-ba6bf2a5400c.png)

- "作成"をクリックします
### Generative AI 対応版ファンクションをテスト
動的グループの作成とポリシーの作成が完了すると先程デプロイしたファンクションから OCI Generative AI サービスを呼び出すことができるようになっています

:::note warn
ただし、お使いのリージョンがホーム・リージョンでない場合には、IAM の情報が伝播するまでに数分から15分程度かかります。下記のテストを実施して "Error invoking function. status: 502 message: function failed" となる場合にはしばらく待ってから再実行してみてください。15分以上待っても変わらない場合は、動的グループとポリシーの設定に間違いがあると考えられますので見直してみてください
:::
```bash:ファンクションのテスト
echo -n '{"message": "こんばんは！"}' | fn invoke fn_genai_translate_app genai_translate_func
```
```bash:ファンクションのテスト実行例
$ echo -n '{"message": "こんばんは！"}' | fn invoke fn_genai_translate_app genai_translate_func
{"message": "{\"input\": \"こんばんは！\",\"output\": \"Good evening.\"}"}
```

## OCI API Gateway の設定
OCI API Gateway を使ってファンクションを RESTful API として公開します。
公式ドキュメントはこちら↓です。

https://docs.public.oneportal.content.oci.oraclecloud.com/ja-jp/iaas/Content/APIGateway/Tasks/apigatewayusingfunctionsbackend.htm



### ネットワーク・セキュリティ・グループの設定
API Gateway 自体の設定の前にインターネットから API Gateway にアクセスできるようにネットワーク・セキュリティ・グループを設定します

- 左上のナビゲーションメニューから "ネットワーキング"⇒"仮想クラウド・ネットワーク"と選択します
- 左側のメニューの Compartment が正しく選択されていることを確認します
- "VCNの作成"の下に表示されている本アプリケーション用に作成した仮想クラウド・ネットワークの名前（例では、OCI Generative AI Hands-on）をクリックします
- 左側のメニューで"ネットワーク・セキュリティ・グループ"をクリックします
- "ネットワーク・セキュリティ・グループの作成"をクリックします
- 任意の名前を設定します（例：OCI Generative AI Hands-on Security Group）
- コンパートメントは、[コンパートメントOCIDの確認](https://qiita.com/drafts#%E3%82%B3%E3%83%B3%E3%83%91%E3%83%BC%E3%83%88%E3%83%A1%E3%83%B3%E3%83%88ocid%E3%81%AE%E7%A2%BA%E8%AA%8D)を で確認したコンパートメントを選択します
- "Next"をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/f22b736c-8ca6-ee1f-7bfb-e37b2ce7253e.png)

- ソース・タイプは、"CIDR" を選択
- ソースCIDRは、アクセスを許可する CIDR を設定します。インターネット上の任意のアドレスからのアクセスを許可する場合は `0.0.0.0/0` と入力します
- IPプロトコルは、"TCP"
- 宛先ポート範囲は、"443" を指定します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/89863418-403b-f38b-704a-304b46e9efc3.png)

- "作成" をクリックします

### リソース・プリンシパルによる認証・認可設定
#### API Gateway 用動的グループの作成
:::note
動的グループの作成手順は、[ファンクション用動的グループの作成](https://qiita.com/drafts#%E3%83%95%E3%82%A1%E3%83%B3%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3%E7%94%A8%E5%8B%95%E7%9A%84%E3%82%B0%E3%83%AB%E3%83%BC%E3%83%97%E3%81%AE%E4%BD%9C%E6%88%90) と同じです
:::

API Gateway 用動的グループの場合の"動的グループの作成"画面での設定項目は次のようになります。

- 任意の名前を入力します（例：API-GW-dg）
- 任意の説明を入力します（例：API Gateway動的グループ）
- 以下の一致ルールを入力します（この一致ルールは、リソースのタイプが OCI API Gateway（`resource.type = 'ApiGateway'`） で、リソースのコンパートメントが指定したコンパートメントIDを持つ API Gateway インスタンスをグループ化しています。`ocid1.compartment.oc1..aaaaaaaa...`の部分はファンクションを作成した際のコンパートメントのIDを指定します）

```text:API-GW-dg
ALL {resource.type = 'ApiGateway', resource.compartment.id = 'コンパートメントID'}
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/43ad4d29-3570-5522-38fd-b7f70ab07715.png)

#### API Gateway 用 IAM ポリシーの作成
:::note
API Gateway 用 IAM ポリシーの作成手順は、[ファンクション用 IAM ポリシーの作成](https://qiita.com/drafts#%E3%83%95%E3%82%A1%E3%83%B3%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3%E7%94%A8-iam-%E3%83%9D%E3%83%AA%E3%82%B7%E3%83%BC%E3%81%AE%E4%BD%9C%E6%88%90) と同じです
:::

API Gateway 用動的グループの場合の"動的グループの作成"画面での設定項目は次のようになります。
- 任意の名前を入力します（例：function4api-gateway-policy）
- 任意の説明を入力します（例：API Gateway に ファンクションの使用権限を与えるポリシー）
- ポリシー・ビルダーの右横の"手動エディタの表示"のスライダーを右にスライドして手動エディタを表示します
- 以下のポリシーを入力します
    - 動的グループ名は、先程作成した動的グループの名前を指定します（例では、API-GW-dg）
    - コンパートメントは、[コンパートメントOCIDの確認](https://qiita.com/drafts#%E3%82%B3%E3%83%B3%E3%83%91%E3%83%BC%E3%83%88%E3%83%A1%E3%83%B3%E3%83%88ocid%E3%81%AE%E7%A2%BA%E8%AA%8D)で確認したコンパートメントを選択します
 
```text:genai4functions
Allow dynamic-group 動的グループ名 to use functions-family in compartment コンパートメント名
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/33b2489d-c74b-6f7d-9751-61c27d2c4756.png)

#### API Gateway の作成
- OCIダッシュボード左上のナビゲーションメニューから"開発者サービス"⇒"API管理"⇒"ゲートウェイ"の順に選択します
- "ゲートウェイの作成" をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/ce47397c-39ec-5ee7-d077-98442acf5603.png)

- 任意の名前を入力します（例：ServerlessGenAI-apigw）
- タイプは、"パブリック"を選択します
- コンパートメントは、[コンパートメントOCIDの確認](https://qiita.com/drafts#%E3%82%B3%E3%83%B3%E3%83%91%E3%83%BC%E3%83%88%E3%83%A1%E3%83%B3%E3%83%88ocid%E3%81%AE%E7%A2%BA%E8%AA%8D)を で確認したコンパートメントを選択します
- 仮想クラウド・ネットワークは[VCN（仮想クラウドネットワーク） の作成](https://qiita.com/drafts#vcn%E4%BB%AE%E6%83%B3%E3%82%AF%E3%83%A9%E3%82%A6%E3%83%89%E3%83%8D%E3%83%83%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF-%E3%81%AE%E4%BD%9C%E6%88%90) で作成した仮想クラウド・ネットワーク（VCN）を選択します（例では、"OCI Generative AI Hands-on"）
- サブネットは、パブリックサブネットを選択します（例では、パブリック・サブネット-OCI Generative AI Hands-on）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/51f23fa4-be58-b770-e4d1-e2dfec990d50.png)

- "ネットワーク・セキュリティ・グループの有効化"にチェックを入れます。
- "（コンパートメント名）のネットワークセキュリティグループ"のプルダウンで[ネットワーク・セキュリティ・グループの設定](https://qiita.com/drafts#%E3%83%8D%E3%83%83%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3%E3%82%B0%E3%83%AB%E3%83%BC%E3%83%97%E3%81%AE%E8%A8%AD%E5%AE%9A)で作成したネットワーク・セキュリティ・グループを選択します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/a4928f0a-4a9b-135d-dd2f-55d961b3eb5e.png)

- "ゲートウェイの作成"をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/6fd1caf6-227e-b028-c26f-3c7f00d35b4d.png)
左上の円が緑色となりその下に"アクティブ"と表示されることを確認します

#### デプロイメントの作成
- 画面左側の"リソース"の下のメニューにある"デプロイメント"をクリックします
- "デプロイメントの作成"をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/35e2ac12-2703-1407-46c5-c446c9135353.png)
- "最初から"が選択されたままにします
- 任意の名前を入力します（例：ServerlessGenAI-apigw-deployment）
- 任意のパス接頭辞を入力します（例：/v1）
    - パス接頭辞は"/" で始まる必要があります
- コンパートメントは、[コンパートメントOCIDの確認](https://qiita.com/drafts#%E3%82%B3%E3%83%B3%E3%83%91%E3%83%BC%E3%83%88%E3%83%A1%E3%83%B3%E3%83%88ocid%E3%81%AE%E7%A2%BA%E8%AA%8D)を で確認したコンパートメントを選択します
- "CORS" の追加をクリックして以下のように設定します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/189383be-5d96-eb77-0668-a70e76b2b851.png)

- 許可されるオリジン： https://objectstorage.us-chicago-1.oraclecloud.com
- メソッド： POST
- 許可されるヘッダー：Content-Type
- その他はデフォルトのまま
- 変更の適用ボタンをクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/e0a4d6d5-0879-bcbb-f7ae-80f6c7855f88.png)

- "次" をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/9fab0117-ce69-f6a4-ab51-9db37f7655ec.png)

- 認証画面では、"認証なし"が選択された状態のまま "次"をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/bd812584-1d81-7e01-d3a7-7019f7c6d439.png)
- パスに任意のパス名を入力します（例：/translate）
- メソッドは、`POST`を選択します
- "単一のバックエンド"が選択された状態のままとします
- バックエンドタイプは、"Oracle ファンクション" を選択します
- アプリケーションは、[OCI Functions アプリケーションの作成](https://qiita.com/drafts#oci-functions-%E3%82%A2%E3%83%97%E3%83%AA%E3%82%B1%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%AE%E4%BD%9C%E6%88%90) で作成したアプリケーションの名前を指定します（例では、fn_genai_translate_app）
- 関数名は、[ファンクションの作成](https://qiita.com/drafts#%E3%83%95%E3%82%A1%E3%83%B3%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%AE%E4%BD%9C%E6%88%90) で作成したファンクションの名前を指定します（例では、genai_translate_func）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/8fa14972-cbca-5edb-b412-64ad771110e5.png)

- "次"をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/5a0d0399-aaf0-a7a9-09e3-53682a9ca28b.png)

- "作成"をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/f6d71078-8a2a-475e-8e27-f46a2b21598b.png)


- "ゲートウェイの詳細"画面に遷移し、状態がデプロイメントの"作成中"となります

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/0cd361e8-cc44-9360-c618-4f95ecad1b06.png)

- 状態が "アクティブ"となるまで待ちます

#### API Gateway を経由したファンクション呼び出しのテスト

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/4d960b7d-bea2-d971-b84d-b91a7f7fa586.png)

- ゲートウェイの詳細"画面の下部"デプロイメント"で作成したデプロイメントの名前（例では、ServerlessGenAI-apigw-deployment）の列にあるエンドポイントをコピーします（"コピー"リンクをクリックします

##### curl コマンドを使ったテスト
HTTPリクエストの body に翻訳したいテキストを設定して、翻訳機能を確認します

```bash:curlによる翻訳機能のテスト
curl -X POST -H "Content-Type: application/json" --data '{"key":"value"}' エンドポイント/パス名
```
- "key" に "message" を入力します
- "value" に翻訳したい文字列を入力します

環境によりエスケープシーケンスに癖があるため以下の実行例を参考にしてください（Macが手元にないため Mac の例がありません...）
```bash:実行例（Cloud Shell 等の Linux環境、Window Git-bash環境）
$ $ echo '{"message":"A long time ago in a galaxy far, far away…"}' | curl -X POST -H "Content-Type: application/json" --data @- https://xxx...xxx.apigateway.us-chicago-1.oci.customer-oci.com/v1/translate
{"message": "{\"input\": \"A long time ago in a galaxy far, far away...\",\"output\": \"遠い昔、はるか彼方の銀河系で...\"}"}
{"message": "遠い昔、はるか彼方の銀河系で..."}

$ echo '{"message":"こんばんは！あなたのお名前は？"}' | curl -X POST -H "Content-Type: application/json" --data @- https://xxx...xxx.apigateway.us-chicago-1.oci.customer-oci.com/v1/translate
{"message": "{\"input\": \"こんばんは！あなたのお名前は？\",\"output\": \"Good evening! What's your name?\"}"}
```

```powershell:実行例（Windows Powershell）
> curl.exe -X POST -H "Content-Type: application/json" https://hpahxbuqsuhbnbibunoesy55ju.apigateway.us-chicago-1.oci.customer-oci.com/v1/translate --data '{\"message\": \"A long time ago in a galaxy far, far away..\"}'
{"message": "{\"input\": \"A long time ago in a galaxy far, far away..\",\"output\": \"遠い昔、はるか彼方の銀河系で...\"}"}

> curl.exe -X POST -H "Content-Type: application/json" https://xxx...xxx.apigateway.us-chicago-1.oci.customer-oci.com/v1/translate --data '{\"message\": \"こんばんは！あなたのお名前は？\"}'
{"message": "{\"input\": \"こんばんは！あなたのお名前は？\",\"output\": \"Good evening! What's your name?\"}"}
```

"A long time ago in a galaxy far, far away…\" という英文が「遠い昔、はるか彼方の銀河系で」という和文に翻訳されたことが確認できました。

:::note warn
{"message": "Hello!"}`と表示される場合は、HTTP Body の JSON を受け渡せていません。恐らくダブルクォーテーションのエスケープに失敗しています。ターミナルの環境によってエスケープに癖があるためうまくいかない場合は、次の Podman を使うことをおススメします
:::

##### Postman によるテスト
- Postman を起動したら "+" をクリックして新しいリクエストを作成
- メソッドはデフォルトの "GET"のままにする
- URL にエンドポイントをペーストして、URLの末尾に先程設定したパス名（例：/translate）を追加します（パス接頭辞（例では、/v1）はコピーしたエンドポイントに記載されています）
- "送信"をクリックします
- レスポンスのボディに以下のように表示されれば API Gateway を経由したファンクションの呼び出しは成功です
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/4a3f23cb-ffb1-9745-baf2-11269d4182ec.png)

続いて、`message` パラメータに翻訳したいテキストを設定して、翻訳機能を確認します

- メソッドは"POST"を選択する（GETでも動作します）
- "パラメータ"とある行の"ボディ"を選択します
- ラジオボタンの "Raw" 選択します
- 入力欄に `{"message":"サーバーレス生成AIアプリの作成を楽しんでいますか？"}`と入力します
- 送信をクリックします
- レスポンスのボディに以下のように表示されれば API Gateway を経由したファンクションの呼び出しと翻訳機能のテストは成功です

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/2cd8deef-7add-d18a-b07f-447684550ed2.png)

:::note warn
いずれの方法においても、API Gateway からレスポンスが返らずタイムアウトする場合には、インターネットから API Gateway へアクセスするためのセキュリティ・グループのインバウンド設定に不備があると思われます。また、`{"message":"Internal Server Error","code":500}` というエラーが返ってきた場合には、API Gateway 用動的グループか API Gateway に ファンクションへのアクセス権を与えるIAM のポリシーの設定に不備がある可能性が高いのでこれらを再確認しましょう
:::

## Gradio Lite による UI 
### Gradio Python コード

```python:serverless_generative_ai_gradio_lite_translate.py (Gradio による UI)
import gradio as gr
import requests
import json
import re

def translate(text):
    url = "エンドポイント名/v1/translate"
    headers = {"Content-Type": "application/json"}
    data = {"message": text}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        message = result["message"]
        
        # JSONデータを抽出し、改行をエスケープ
        json_match = re.search(r'\{.*\}', message, re.DOTALL)
        if json_match:
            try:
                json_string = json_match.group().replace('\n', '\\n')
                json_data = json.loads(json_string)
                return json_data.get("output", message)
            except json.JSONDecodeError:
                return message
        else:
            return message
    except requests.exceptions.RequestException as e:
        return f"エラーが発生しました: {str(e)}"

with gr.Blocks() as demo:
    gr.Markdown("# とにかく翻訳する青山アイさん")
    
    with gr.Row():
        input_text = gr.Textbox(label="翻訳したい文章", lines=5, scale=1, show_copy_button=True)
        translate_button = gr.Button("翻訳", scale=0, min_width=100)
        output_text = gr.Textbox(label="翻訳結果", lines=5, scale=1, show_copy_button=True)
    with gr.Row():
        clear_button = gr.ClearButton(components=[input_text], value="クリア")

    translate_button.click(fn=translate, inputs=input_text, outputs=output_text)

demo.launch(share=True, favicon_path="img/ai_aoyama_favicon.png")
```

- この Python コード をコピーしてローカルに serverless_generative_ai_gradio_lite_translate.py という名前（例）で保存します
- "エンドポイント名" をAPI Gatewayのデプロイメントで確認して書き換えます
    - OCIダッシュボード左上のナビゲーション・メニューから"開発者サービス"⇒"ゲートウェイ"と選択し、左側の"リソース"の下のメニューから"デプロイメント"をクリックします
    - "デプロイメント"に表示されたリストの中の先程作成したデプロイメントの名前の行の"エンドポイント"欄の"コピー"をクリックします
- コード の "エンドポイント名" の部分へペーストします
- url = "https://xxxx......xxxxxx.apigateway.us-chicago-1.oci.customer-oci.com/v1/translate" のような記述になります

- ローカル環境や Cloud Shell で動作確認します

```bash: Gradio Python コード の実行例
python serverless_generative_ai_gradio_lite_translate.py 
Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://2e467eacb8694dfce1.gradio.live

This share link expires in 72 hours. For free permanent hosting and GPU upgrades, run `gradio deploy` from Terminal to deploy to Spaces (https://huggingface.co/spaces)
```
- ここで、操作している PC 上で Serverless_generative_ai_gradio_lite_translate.py を実行している場合は、local URL: の __http://127.0.0.1:7860__ を ブラウザで開きます（ターミナルによっては Ctrlキーを押しながらマウスクリックで開くことができます。）。Serverless_generative_ai_gradio_lite_translate.py を Cloud Shell などのリモートで実行している場合は、__public URL:__ の後に表示されている URL をブラウザで開きます
- 以下のような画面がブラウザに表示されます

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/4661edfd-f374-fda3-95f4-24c614d6484c.png)

- "翻訳したい文章" の下のテキストボックスに "ある春の日に、俺は運命と出会った......" などと日本語の文章を入力して、"翻訳"ボタンをクリックします
- "翻訳結果"のテキストボックスに "On a spring day, I met my destiny..." などと英語が表示されれるはずです（初回は少し時間がかかります。また、翻訳文は厳密に同一とは限りません）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/12ce15d3-0127-49c8-19de-ea38725db5f7.png)

- 次に、クリアボタンをクリックして "翻訳したい文章" の下のテキストボックスをクリアした後、 "A long time ago in a galaxy far, far away…" などと入力して、"翻訳"ボタンをクリックします
- - "翻訳結果"のテキストボックスに "遠い昔、遥か彼方の銀河系で。" などと英語が表示されれるはずです（翻訳文は厳密に同一とは限りません）
- 以上で、Gradio Python コードの作成と動作確認は完了です

### Gradio Lite 化
:::note
Gradio Lite の公式ドキュメントはこちら↓です

https://www.gradio.app/guides/gradio-lite

:::

作成した Gradio のPython コードをブラウザで動作するように Gradio Lite 対応の HTML へ埋め込みインターネットに公開します

Gradio の Python コードを Gradio Lite に対応させる手順は以下のとおりです。
- Gradio Lite の書式に従った HTML に Python コードと Python の requirements.txt を埋め込む
- HTML を Webサーバーやオブジェクトストレージを使って HTTP(S) でアクセスできるように公開する

#### HTML への埋め込み（）
```html:Gradio Lite HTML テンプレート
<html>
	<head>
		<script type="module" crossorigin src="https://cdn.jsdelivr.net/npm/@gradio/lite/dist/lite.js"></script>
		<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@gradio/lite/dist/lite.css" />
	</head>
	<body>
		<gradio-lite>
    		<gradio-requirements>
      			(gradio 以外の Python パッケージのリスト)
			</gradio-requirements>
   			(Gradio Python コード)
		</gradio-lite>
	</body>
</html>

```
- (gradio 以外の Python パッケージのリスト) の部分に、requirements.txt の gradio 以外のパッケージ名を改行で区切って列挙します。今回は、 requests だけです
- (Gradio Python コード) の部分に Gradio Python コードを丸ごと挿入します

以下が出来上がったHTMLコードです

```html:serverless_generative_ai_gradio_lite_translate.html (Gradio Lite 対応 HTML)
<html lang="ja">
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<script type="module" crossorigin src="https://cdn.jsdelivr.net/npm/@gradio/lite/dist/lite.js"></script>
		<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@gradio/lite/dist/lite.css" />
	</head>
	<body>
		<gradio-lite>
            <gradio-requirements>
                requests
            </gradio-requirements>
            import gradio as gr
            import requests
            import json
            import re

            def translate(text):
                url = "エンドポイント名/translate"
                headers = {"Content-Type": "application/json"}
                data = {"message": text}
                
                try:
                    response = requests.post(url, headers=headers, data=json.dumps(data))
                    response.raise_for_status()
                    result = response.json()
                    message = result["message"]
                    
                    # JSONデータを抽出し、改行をエスケープ
                    json_match = re.search(r'\{.*\}', message, re.DOTALL)
                    if json_match:
                        try:
                            json_string = json_match.group().replace('\n', '\\n')
                            json_data = json.loads(json_string)
                            return json_data.get("output", message)
                        except json.JSONDecodeError:
                            return message
                    else:
                        return message
                except requests.exceptions.RequestException as e:
                    return f"エラーが発生しました: {str(e)}"

            with gr.Blocks() as demo:
                gr.Markdown("# とにかく翻訳する青山アイさん")
                
                with gr.Row():
                    input_text = gr.Textbox(label="翻訳したい文章", lines=5, scale=1, show_copy_button=True)
                    translate_button = gr.Button("翻訳", scale=0, min_width=100)
                    output_text = gr.Textbox(label="翻訳結果", lines=5, scale=1, show_copy_button=True)
                with gr.Row():
                    clear_button = gr.ClearButton(components=[input_text], value="クリア")

                translate_button.click(fn=translate, inputs=input_text, outputs=output_text)

            demo.launch()

    	</gradio-lite>
    </body>

</html>
```
- この HTML をコピーしてローカルに serverless_generative_ai_gradio_lite_translate.html という名前（例）で保存します
- "エンドポイント名" をAPI Gatewayのデプロイメントで確認して書き換えます
    - OCIダッシュボード左上のナビゲーション・メニューから"開発者サービス"⇒"ゲートウェイ"と選択します
    - コンパートメント内のゲートウェイにリストされたゲートウェイの中から先程作成したゲートウェイの名前（例：ServerlessGenAI-apigw）をクリックします。
    - 左側の"リソース"の下のメニューから"デプロイメント"をクリックします
    - "デプロイメント"に表示されたリストの中の先程作成したデプロイメントの名前の行の"エンドポイント"欄の"コピー"をクリックします
- HTML の "エンドポイント名" の部分へペーストします
- url = "https://xxxx......xxxxxx.apigateway.us-chicago-1.oci.customer-oci.com/v1/translate" のような記述になります

### オブジェクトストレージへのアップロード
#### バケットの作成
- OCIダッシュボードの左上のナビゲーション・メニューから"ストレージ"⇒"バケット"に順に選択します
- "バケットの作成"をクリックします
- バケット名にに任意の名前を入力します（例：serverless_generativeai_gradio_lite_bucket）
- その他はデフォルトのまま作成ボタンをクリックします
- 作成したバケットの名前をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/adaf76f1-8371-715c-0e20-9ff053d9bc9f.png)

#### バケットの公開
- バケット名の下にある"可視性の編集"をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/a6f925e6-a492-884d-16fc-1f27911d1364.png)

- "パブリック"をチェックします
- "ユーザーにこのバケットのオブジェクトのリスト表示を許可" のチェックを外します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/ce563fc3-edff-069e-ac74-6deb2670f54b.png)

- 変更の保存ボタンをクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/e0eb5d90-1b56-468b-3800-da5eaa1b3b33.png)

#### HTML のアップロード
- 上の画像の画面の下部のあるアップロードボタンをクリックします
- "ファイルを選択"をクリックして、serverless_generative_ai_gradio_lite_translate.html をアップロードします（その他はデフォルトのまま）
- 閉じるボタンをクリックします
- 画面下部の"オブジェクト"欄にアップロードした HTML ファイルの名前が表示されます
- HTML ファイルの名前の右側のメニュー（3つの点）をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/c9a32ffc-dffa-22c2-27c6-168c61359e66.png)

- ”オブジェクト詳細の表示”を選びます
- "URLパス"に表示されているリンクをクリックします
- 以下のように Gradio Python コードのときと同じアプリケーションの UI が表示されるはずです

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/b78bcf59-b80b-3c8b-d91e-23592757c0c0.png)

:::note warn
ここで、翻訳結果欄に 「エラーが発生しました: ('Connection aborted.', HTTPException("Failed to execute 'send' on 'XMLHttpRequest': Failed to load 'https://hpahxbuqsuhbnbibunoesy55ju.apigateway.us-chicago-1.oci.customer-oci.com/v1/translate'."))」 のようなエラーメッセージが表示された場合は、API Gateway の CORSポリシー 設定に不備がある可能性が高いので API Gateway の設定を見直しましょう（OCIダッシュボード左上のナビゲーション・メニューから"開発者サービス"⇒"ゲートウェイ"と選択し、作成したゲートウェイ名をクリック、左側の"デプロイメント2を選択して、作成したデプロイメントの名前（例：ServerlessGenAI-apigw-deployment）うぃクリックして、"編集"をクリック、"APIリクエスト・ポリシー"の"CORS"の"編集"をクリック）
:::
- 先程と同じように"翻訳したい文章"に適当な文章を入力して"翻訳"ボタンをクリックしてテストします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/74534/d74ba370-2269-4465-8902-b16b503bd06c.png)

## お疲れさまでした！
この記事では、end-to-end でサーバーレスコンピューティングを活用する点を主題としているため生成AIアプリケーションは単純な翻訳アプリを題材としていますのでデータベースへのアクセスなどは実装していません。なお、この記事ではできるだけ簡単にアプリ全体の構築を体験していただけるようにセキュリティへの配慮は厳密にしていません。ログイン機能・画面の実装や API Gateway と ファンクションの統合や CORS、バケットの公開など工夫いただく余地があります。
みなさまのアイデアで育ててあげてください。

:::note
Functions のコールド・スタートによる遅延を回避するためには、「[プロビジョニングされた同時実行性（Provisioned Concurrency）](https://docs.oracle.com/ja-jp/iaas/Content/Functions/Tasks/functionsusingprovisionedconcurrency.htm)」を利用することができます。
:::

https://qiita.com/shukawam/items/ec128cc3dd1b169cc3e6

:::note
また、最小限のコストでコールド・スタートの影響を軽減したい場合には、「[リソース・スケジューラー](https://docs.oracle.com/ja-jp/iaas/Content/resource-scheduler/tasks/create-manage.htm#create-manage)」を使って Function を定期的に実行することもできます。
:::

## おまけ

他にもいろいろ記事を書いていますので良かったらお立ち寄りください。

https://qiita.com/yuji-arakawa/items/65ca3ec5fc5f73d44e7e

https://qiita.com/yuji-arakawa/items/c60251131c00f2ac02f1

https://qiita.com/yuji-arakawa/items/f27bfbdad9d763e8c8c4

https://qiita.com/yuji-arakawa/items/8607862c1e590b9ed146

https://qiita.com/yuji-arakawa/items/3f68a7136e42f743ae6b

https://qiita.com/yuji-arakawa/items/32dffa62c75e695019ef

https://qiita.com/yuji-arakawa/items/1f6ab3f68b98ff56de12

https://qiita.com/yuji-arakawa/items/70470b348c90adb82b7f

https://qiita.com/yuji-arakawa/items/122fa187309de013ec62

https://qiita.com/yuji-arakawa/items/1135f6d71acdec157db3

https://qiita.com/yuji-arakawa/items/9525beab101b8e1d6452

https://qiita.com/yuji-arakawa/items/8d065ae3df536f5cd559

https://qiita.com/yuji-arakawa/items/fd4fd0c026ecfa664d97

https://qiita.com/yuji-arakawa/items/654d936ca616334286b0

https://qiita.com/yuji-arakawa/items/1a8cfeff8f81ba808389

https://qiita.com/yuji-arakawa/items/9cd485debd5b0d18aca2

https://qiita.com/yuji-arakawa/items/042937eaf16fa00cf491

https://qiita.com/yuji-arakawa/items/6d0299c505315bc3cdb0

https://qiita.com/yuji-arakawa/items/05e3455572d3b09a53dc

https://qiita.com/yuji-arakawa/items/2d4f6eff17a5410dba2d

https://qiita.com/yuji-arakawa/items/597c4bd9f3d5b4212b51

https://aws.amazon.com/jp/blogs/news/leveraging-pinecone-on-aws-marketplace-as-a-knowledge-base-for-amazon-bedrock/
