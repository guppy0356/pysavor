# pysavor

`pysavor`は、クリーンアーキテクチャの原則に基づき、テスト可能性、保守性、拡張性を最大化することを目的としたFastAPIプロジェクトのテンプレートです。

## 中核となる設計思想

本プロジェクトは、以下の3つの原則を厳格に遵守します。

1. **関心の分離 (Separation of Concerns)**: 各レイヤーは、単一の明確な責務のみを持ちます。

2. **依存性の逆転 (Dependency Inversion Principle)**: ビジネスロジック（高レベルのモジュール）は、インフラストラクチャ（低レベルのモジュール）に依存しません。両者は、抽象（`Protocol`）に依存します。

3. **思想の表明 (Expressive Architecture)**: ディレクトリ構造、ファイル名、コードの一行一行が、設計思想を明確に表現します。

## アーキテクチャ概要

### ディレクトリ構造

プロジェクトのすべてのソースコードは`src/`ディレクトリ内に配置され、各サブディレクトリは明確に分離された責務を持ちます。

```
src/
├── api/                  # API層
│   ├── deps.py           #   - 依存性注入(DI)の定義
│   └── routers/          #   - APIルーターの定義
├── use_cases/            # ビジネスロジック層
├── policies/             # 認可ルール層
├── repositories/         # データアクセス層
├── protocols/            # 抽象インターフェース層
├── models/               # データベースモデル層 (SQLModel)
├── schemas/              # APIデータモデル層 (Pydantic)
├── migrations/           # ★★★ [修正] データベースマイグレーション (古文書館) ★★★
├── security.py           # セキュリティ関連ユーティリティ
├── db.py                 # データベース接続管理
└── settings.py           # アプリケーション設定

```

### 各層の責務

* **`api/routers/`**: HTTPリクエストを受け付け、レスポンスを返却する唯一の層。ビジネスロジックは含まず、`use_cases`層の呼び出しと、`deps.py`を通じた依存性の解決に専念します。

* **`api/deps.py`**: API層で必要とされるすべてのDI関数（認証、認可、セッション管理など）を集約します。

* **`use_cases/`**: アプリケーション固有のビジネスロジックを実装します。フレームワークやデータベースの実装詳細からは完全に独立しています。

* **`policies/`**: 「誰が何を行えるか」という認可ルールを、フレームワーク非依存の純粋なPythonクラスとして定義します。

* **`repositories/`**: データベースとのデータ永続化処理をカプセル化します。ビジネスロジックは含みません。

* **`protocols/`**: リポジトリなどの抽象インターフェースを`typing.Protocol`を用いて定義します。`use_cases`層は、具象クラスではなくこの`Protocol`に依存します。

* **`models/`**: `SQLModel`を用いて、データベースのテーブルスキーマとエンティティを定義します。

* **`schemas/`**: `Pydantic`を用いて、APIの入出力（リクエスト/レスポンスボディ）のデータ構造とバリデーションルールを定義します。`SQLModel`を継承せず、APIの契約に特化します。

* **`migrations/`**: `Alembic`によって生成・管理されるデータベースのマイグレーションスクリプトを格納します。

* **`security.py`**: パスワードハッシュやJWTの生成・検証など、セキュリティ関連のユーティリティ関数を提供します。

* **`db.py`**: SQLAlchemyの`engine`を生成し、DI用の`Session`ジェネレータを提供します。

* **`settings.py`**: `pydantic-settings`を用い、`.env`ファイルや環境変数からアプリケーションの設定を読み込み、一元管理します。

## 主要な実装パターン

### 依存性の注入 (DI) と認可

認可には、**アクションに対するガード**と、**コレクションへのスコープ適用**の2つの側面があります。

#### アクションに対するガード

個別のリソースへのアクション（作成、更新、削除など）に対する認可ロジックは、`policies`層で純粋なルールとして定義されます。これらのルールは、`api/deps.py`内でDI関数（ガード）として実装され、`@router`の`Depends`を通じて宣言的に適用されます。これにより、`use_cases`層は認可ロジックから解放され、ビジネスロジックに集中できます。

```
# src/api/routers/issue.py (例)
@router.post("/", dependencies=[Depends(deps.can_create_issue)])
def create_issue(
    current_user: User = Depends(deps.get_current_user),
    # ...
):
    # ...

```

#### コレクションへのスコープ適用 (`resolve_scope`)

一覧取得のように、ユーザーの権限に応じて返すべきリソースの**範囲（スコープ）**を決定する必要がある場合、`policies`層に`resolve_scope`メソッドを定義します。このメソッドは、`SQLAlchemy`のフィルター条件のような、リポジトリ層が解釈できる「法律」そのものを返します。`use_cases`層は、この法律を`repositories`層に渡して、認可済みのリソースリストを取得します。

```
# src/use_cases/issue.py (例)
def get_my_issues(
    session: Session,
    current_user: User,
    issue_repo: IssueRepositoryProtocol,
) -> List[Issue]:
    policy = IssuePolicy(user=current_user)
    scope = policy.resolve_scope()
    return issue_repo.find_by_scope(session=session, scope=scope)

```

### 抽象への依存

`use_cases`層は、`repositories`の具象クラスに直接依存しません。代わりに、`protocols`に定義されたインターフェースに依存します。これにより、テスト時にリポジトリをモックに差し替えることが容易になり、データソースの変更（例: DBから外部APIへ）にも柔軟に対応できます。この契約は、主に`mypy`のような**静的型チェッカー**によって、コードの実行前に検証されます。`typing.Protocol`は、クラスが特定のメソッドや属性を持っているかという「構造」をチェックするものであり（構造的型付け）、明示的な継承を必要としません。

```
# src/use_cases/issue.py (例)
from src.protocols.issue import IssueRepositoryProtocol

def create_issue(
    issue_repo: IssueRepositoryProtocol,
    # ...
):
    # ...

```

## セットアップと実行

1. **環境構築**:

   ```
   uv venv
   source .venv/bin/activate
   
   ```

2. **依存関係のインストール**:

   ```
   # uv.lockファイルに基づいて、すべての依存関係を正確に再現します
   uv sync --dev
   
   # プロジェクト自体を編集可能モードでインストールし、'src'をインポート可能にします
   uv pip install -e .
   
   ```

3. **環境変数の設定**:
   `.env`ファイルを作成し、`DATABASE_URL`や`SECRET_KEY`を設定します。

4. **データベースマイグレーション**:

   ```
   uv run alembic upgrade head
   
   ```

5. **開発サーバーの起動**:

   ```
   uv run dev
   
   ```