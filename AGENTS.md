# AGENTS.md - pysavor アーキテクチャ・コンポーネント仕様書

## 📖 目次

1. [プロジェクト概要](#プロジェクト概要)
2. [アーキテクチャ設計](#アーキテクチャ設計)
3. [ディレクトリ構造](#ディレクトリ構造)
4. [コンポーネント詳細仕様](#コンポーネント詳細仕様)
5. [データフロー](#データフロー)
6. [セキュリティ機構](#セキュリティ機構)
7. [技術スタック](#技術スタック)
8. [設計パターンと規約](#設計パターンと規約)

---

## プロジェクト概要

**pysavor** は、Clean Architecture の原則に基づいて設計された FastAPI ベースの REST API アプリケーションです。ユーザー管理、認証、Issue 管理機能を提供し、保守性・テスト容易性・拡張性を重視した設計となっています。

### 設計哲学

- **関心の分離**: 各レイヤーは単一の明確な責務を持つ
- **依存性逆転**: ビジネスロジックは抽象（Protocol）に依存し、具象実装には依存しない
- **表現的アーキテクチャ**: ディレクトリ構造とコードが設計意図を伝える

---

## アーキテクチャ設計

### レイヤー構造

```
HTTP リクエスト
     ↓
┌─────────────────────────────────────────────┐
│  API レイヤー (api/routers/)                │
│  - HTTPリクエスト/レスポンスの処理           │
│  - ルート定義                               │
│  - HTTP例外への変換                         │
└─────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│  依存性注入レイヤー (api/deps.py)            │
│  - 認可ガード (can_create_issue等)          │
│  - リソースローディング (get_issue_by_id等) │
│  - 依存関係の解決                           │
└─────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│  ユースケースレイヤー (use_cases/)           │
│  - 純粋なビジネスロジック                    │
│  - フレームワーク非依存                      │
│  - Protocolに依存（具象実装には依存しない）   │
│  - ドメイン例外をスロー                      │
└─────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│  ポリシーレイヤー (policies/)                │
│  - 認可ルール                               │
│  - 純粋なPythonクラス                       │
│  - resolve_scope() がSQLAlchemyフィルタを返す│
│  - フレームワーク非依存                      │
└─────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│  リポジトリレイヤー (repositories/)          │
│  - SQLModel ORM操作                         │
│  - Protocolの実装                           │
│  - データベースクエリと永続化                │
└─────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│  モデルレイヤー (models/)                    │
│  - SQLModel エンティティ定義                 │
│  - テーブル定義とリレーションシップ          │
└─────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│  データベース (db.py)                        │
│  - SQLAlchemy エンジン                      │
│  - セッション管理                           │
└─────────────────────────────────────────────┘
```

### 依存関係の方向性

- **外側から内側へ**: API → ユースケース → リポジトリ → モデル
- **抽象への依存**: ユースケースは `Protocol` に依存し、具象リポジトリには依存しない
- **依存性注入**: FastAPI の `Depends` を使用してリポジトリを注入

---

## ディレクトリ構造

```
/Users/akira/Project/private/pysavor/
├── .env                          # 環境設定（SQLite DB、SECRET_KEY）
├── .gitignore                    # Git除外設定
├── .python-version               # Python バージョン指定
├── README.md                     # プロジェクトドキュメント（日本語）
├── AGENTS.md                     # 本ドキュメント
├── alembic.ini                   # Alembic マイグレーション設定
├── pyproject.toml                # プロジェクトメタデータと依存関係
├── uv.lock                       # UV パッケージマネージャーロックファイル
│
├── data/
│   └── development.db            # SQLite データベースファイル
│
└── src/                          # メインソースコード
    ├── __init__.py               # パッケージ初期化
    ├── main.py                   # FastAPI アプリケーションエントリーポイント
    ├── settings.py               # アプリケーション設定（pydantic-settings）
    ├── security.py               # JWT とパスワードハッシング（横断ユーティリティ）
    │
    ├── api/                      # APIレイヤー（HTTPハンドラ）
    │   ├── deps.py               # 依存性注入と認可ガード
    │   ├── routers/              # APIエンドポイントルーター
    │   │   ├── auth.py           # 認証エンドポイント（login）
    │   │   └── issue.py          # Issue 管理エンドポイント
    │   └── schemas/              # HTTP契約（Pydanticモデル）★ 新規配置
    │       ├── user.py           # UserCreate, UserRead, UserUpdate
    │       ├── issue.py          # IssueCreate, IssueRead, IssueUpdate
    │       ├── token.py          # Token, TokenPayload
    │       └── auth.py           # LoginRequest
    │
    ├── app/                      # アプリケーション層（ビジネスロジック）★ use_casesから移動
    │   ├── exceptions.py         # ドメイン固有例外
    │   ├── user.py               # ユーザーユースケース（create_user）
    │   ├── auth.py               # 認証ユースケース（login）
    │   └── issue.py              # Issue ユースケース（create, read, collaborate）
    │
    ├── domain/                    # ドメイン層（ルールと抽象）★ 新規配置
    │   ├── policies/              # 認可ルール（純粋Python）★ policiesから移動
    │   │   └── issue.py          # Issue 認可ポリシー
    │   └── ports/                 # 抽象インターフェース（typing.Protocol）★ protocolsから移動
    │       ├── user.py           # UserRepositoryProtocol
    │       └── issue.py          # IssueRepositoryProtocol
    │
    └── adapters/                  # アダプター層（技術詳細）★ 新規配置
        └── db/                    # データベースアダプター
            ├── session.py         # データベース接続管理 ★ db.pyから移動
            ├── models/            # SQLModel データベースモデル ★ modelsから移動
            │   ├── __init__.py    # 全テーブルモデルの自動ローダー
            │   ├── user.py        # User エンティティ
            │   ├── issue.py       # Issue エンティティ
            │   └── collaborator.py # Collaborator 結合テーブル
            ├── repositories/      # データアクセス実装 ★ repositoriesから移動
            │   ├── user.py        # User リポジトリ
            │   └── issue.py       # Issue リポジトリ
            └── migrations/        # Alembic データベースマイグレーション ★ migrationsから移動
                ├── env.py         # Alembic 環境設定
                ├── script.py.mako # マイグレーションテンプレート
                └── versions/      # マイグレーションスクリプト
                    ├── f63635279097_create_initial_user_table.py
                    ├── 6b277d0147af_create_initial_issues_table.py
                    └── 875428da6c8e_create_initial_collaborators_table.py
```

### ディレクトリ構造の設計方針（2025-01-26 リファクタリング）

**目的**: 「置き場所の意味が一発で分かる」「命名と境界がブレない」構造への整理

#### 配置ルール

1. **`src/api/schemas/`**: HTTP契約のみ（Pydanticモデル）
   - APIのリクエスト/レスポンスのデータ構造を定義
   - 外部との契約を明確化

2. **`src/adapters/`**: I/Oと技術詳細のみ
   - `adapters/db/`: SQLModel、Session、migrations、repository実装
   - データベース関連の技術詳細を集約

3. **`src/app/`**: HTTPを知らないビジネスロジック
   - 旧`use_cases/`から移動
   - FastAPI型に依存しない
   - UseCase入力はDTOを作らず引数で受ける（必要になったら後で導入）

4. **`src/domain/`**: ルールとportのみ
   - `domain/policies/`: 認可ルール（旧`policies/`から移動）
   - `domain/ports/`: repository protocol/interface（旧`protocols/`から移動）

5. **`src/security.py`**: 横断ユーティリティとして固定
   - JWT/Hashなどのセキュリティ機能
   - `adapters/security/`への移動も可能だが、横断的性質を考慮して現状維持

#### 移動マッピング（実施済み）

- `src/schemas/*` → `src/api/schemas/*`
- `src/models/*` → `src/adapters/db/models/*`
- `src/migrations/*` → `src/adapters/db/migrations/*`
- `src/db.py` → `src/adapters/db/session.py`
- `src/repositories/*` → `src/adapters/db/repositories/*`
- `src/protocols/*` → `src/domain/ports/*`
- `src/policies/*` → `src/domain/policies/*`
- `src/use_cases/*` → `src/app/*`

#### 重要な制約

- **最小差分で移行**: ロジック改修より「配置変更＋import修正」が中心
- **動作が壊れないこと**: 型/テスト/起動が通ることを重視
- **外部仕様を変えない**: APIレスポンスやリクエスト形を勝手に変更しない
- **CQRS分割はしない**: Read/Writeモデル分離は行わない
- **追加の設計大改造はしない**: domainエンティティ導入などは不要、現状維持でOK

---

## コンポーネント詳細仕様

### 1. アプリケーションエントリーポイント

#### `src/main.py`

FastAPI アプリケーションのメインモジュール。

```python
from fastapi import FastAPI
from src.api.routers import user, auth, issue

app = FastAPI(title="pysavor")

# ルーター登録
app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(issue.router, prefix="/api/v1/issues", tags=["issues"])

@app.get("/")
def root():
    return {"message": "Welcome to pysavor"}
```

**責務**:
- FastAPI アプリケーションの作成と設定
- ルーターの登録
- ルートエンドポイントの定義

---

### 2. 設定管理

#### `src/settings.py`

Pydantic Settings を使用した環境設定管理。

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str                    # 環境変数または .env から取得
    SECRET_KEY: str                      # JWT署名用秘密鍵
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    COOKIE_SECURE: bool = False
    ALGORITHM: str = "HS256"             # JWT アルゴリズム
```

**設定ファイル**: `.env`

```env
DATABASE_URL=sqlite:///./data/development.db
SECRET_KEY=your-secret-key-here
```

---

### 3. データベース接続

#### `src/db.py`

SQLAlchemy エンジンとセッション管理。

```python
from sqlmodel import Session, create_engine
from src.settings import Settings

settings = Settings()
engine = create_engine(settings.DATABASE_URL)

def current_session():
    """FastAPI Depends で使用するセッションジェネレータ"""
    with Session(engine) as session:
        yield session
```

**特徴**:
- リクエストごとに新しいセッションを生成
- コンテキストマネージャーで自動クローズ
- FastAPI の依存性注入システムと統合

---

### 4. セキュリティモジュール

#### `src/security.py`

JWT トークン生成とパスワードハッシング。

```python
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: str, expires_delta: timedelta) -> str:
    """JWT アクセストークンを生成"""
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": subject}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードを検証"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """パスワードをハッシュ化"""
    return pwd_context.hash(password)
```

**セキュリティ仕様**:
- **ハッシュアルゴリズム**: Bcrypt
- **JWT アルゴリズム**: HS256
- **トークン有効期限**: 30分（設定可能）
- **トークン保存先**: HTTP-only Secure Cookie

---

### 5. モデルレイヤー（データベーステーブル）

#### `src/models/user.py`

User エンティティの定義。

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: Optional[str] = Field(default=None, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

    # リレーションシップ
    issues: List["Issue"] = Relationship(back_populates="owner")
    collaborated_issues: List["Issue"] = Relationship(
        back_populates="collaborators",
        link_model=Collaborator
    )
```

**テーブル仕様**:
- **主キー**: `id` (INTEGER, AUTO_INCREMENT)
- **インデックス**: `email` (UNIQUE), `full_name`
- **リレーション**:
  - `issues`: 所有する Issue（1対多）
  - `collaborated_issues`: 共同作業する Issue（多対多）

---

#### `src/models/issue.py`

Issue エンティティの定義。

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Issue(SQLModel, table=True):
    __tablename__ = "issues"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    owner_id: int = Field(foreign_key="users.id")

    # リレーションシップ
    owner: User = Relationship(back_populates="issues")
    collaborators: List[User] = Relationship(
        back_populates="collaborated_issues",
        link_model=Collaborator
    )
```

**テーブル仕様**:
- **主キー**: `id` (INTEGER, AUTO_INCREMENT)
- **外部キー**: `owner_id` → `users.id`
- **インデックス**: `title`
- **リレーション**:
  - `owner`: Issue のオーナー（多対1）
  - `collaborators`: 共同作業者（多対多）

---

#### `src/models/collaborator.py`

User と Issue の多対多リレーションを管理する結合テーブル。

```python
from sqlmodel import SQLModel, Field
from typing import Optional

class Collaborator(SQLModel, table=True):
    __tablename__ = "collaborators"

    issue_id: Optional[int] = Field(
        default=None,
        foreign_key="issues.id",
        primary_key=True
    )
    user_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        primary_key=True
    )
```

**テーブル仕様**:
- **複合主キー**: `(issue_id, user_id)`
- **外部キー**:
  - `issue_id` → `issues.id`
  - `user_id` → `users.id`

---

### 6. スキーマレイヤー（API 契約）

#### `src/schemas/user.py`

ユーザー関連の Pydantic モデル。

```python
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserRead(UserBase):
    id: int

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = Field(default=None, min_length=8)
```

---

#### `src/schemas/issue.py`

Issue 関連の Pydantic モデル。

```python
from pydantic import BaseModel
from src.schemas.user import UserRead

class IssueBase(BaseModel):
    title: str
    description: str | None = None

class IssueCreate(IssueBase):
    pass

class IssueRead(IssueBase):
    id: int
    owner_id: int
    owner: UserRead

class IssueUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
```

---

#### `src/schemas/token.py` & `src/schemas/auth.py`

認証関連のスキーマ。

```python
# token.py
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: int | None = None  # JWT の subject（ユーザーID）

# auth.py
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

---

### 7. プロトコルレイヤー（抽象インターフェース）

#### `src/protocols/user.py`

User リポジトリの抽象インターフェース。

```python
from typing import Protocol
from sqlmodel import Session
from src.models.user import User
from src.schemas.user import UserCreate

class UserRepositoryProtocol(Protocol):
    def get_by_id(self, session: Session, *, id: int) -> User | None:
        """IDでユーザーを取得"""
        ...

    def get_by_email(self, session: Session, *, email: str) -> User | None:
        """メールアドレスでユーザーを取得"""
        ...

    def create(self, session: Session, *, user_create: UserCreate, hashed_password: str) -> User:
        """新しいユーザーを作成"""
        ...
```

**設計意図**:
- ユースケースは `Protocol` に依存し、具象実装には依存しない
- テスト時にモックを注入しやすい
- 依存性逆転の原則を実現

---

#### `src/protocols/issue.py`

Issue リポジトリの抽象インターフェース。

```python
from typing import Protocol, Any, Sequence
from sqlmodel import Session
from src.models.issue import Issue
from src.models.user import User
from src.schemas.issue import IssueCreate

class IssueRepositoryProtocol(Protocol):
    def get_by_id(self, session: Session, *, id: int) -> Issue | None:
        """IDでIssueを取得"""
        ...

    def find_by_scope(self, session: Session, *, scope: Any) -> Sequence[Issue]:
        """スコープ（SQLAlchemyフィルタ）でIssueを検索"""
        ...

    def create(self, session: Session, *, issue_create: IssueCreate, owner_id: int) -> Issue:
        """新しいIssueを作成"""
        ...

    def add_collaborator(self, session: Session, *, issue: Issue, user: User) -> None:
        """Issueに共同作業者を追加"""
        ...
```

---

### 8. リポジトリレイヤー（データアクセス実装）

#### `src/repositories/user.py`

User リポジトリの実装。

```python
from sqlmodel import Session
from src.models.user import User
from src.schemas.user import UserCreate

class UserRepository:
    def get_by_id(self, session: Session, *, id: int) -> User | None:
        return session.get(User, id)

    def get_by_email(self, session: Session, *, email: str) -> User | None:
        return session.query(User).filter(User.email == email).first()

    def create(self, session: Session, *, user_create: UserCreate, hashed_password: str) -> User:
        user_data = user_create.model_dump()
        user_data.pop("password", None)

        new_user = User(**user_data, hashed_password=hashed_password)

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return new_user
```

**実装パターン**:
- インスタンスメソッドを使用
- `self, session` を引数として受け取る
- 読み取り操作は `session.get()` または `session.query()` を使用
- 書き込み操作は `add()` → `commit()` → `refresh()`

---

#### `src/repositories/issue.py`

Issue リポジトリの実装。

```python
from typing import Any, Sequence
from sqlmodel import Session, select
from src.models.issue import Issue
from src.models.user import User
from src.schemas.issue import IssueCreate

class IssueRepository:
    def get_by_id(self, session: Session, *, id: int) -> Issue | None:
        return session.get(Issue, id)

    def find_by_scope(self, session: Session, *, scope: Any) -> Sequence[Issue]:
        """ポリシーから返されたSQLAlchemyフィルタを適用"""
        statement = select(Issue).where(scope)
        results = session.exec(statement)
        return results.all()

    def create(self, session: Session, *, issue_create: IssueCreate, owner_id: int) -> Issue:
        issue_data = issue_create.model_dump()

        new_issue = Issue(**issue_data, owner_id=owner_id)

        session.add(new_issue)
        session.commit()
        session.refresh(new_issue)

        return new_issue

    def add_collaborator(self, session: Session, *, issue: Issue, user: User) -> None:
        issue.collaborators.append(user)
        session.add(issue)
        session.commit()
        session.refresh(issue)
```

**特徴**:
- `find_by_scope()`: ポリシーから返された WHERE 句を適用
- `add_collaborator()`: SQLModel のリレーションシップを使用して多対多を管理

---

### 9. ユースケースレイヤー（ビジネスロジック）

#### `src/use_cases/exceptions.py`

ドメイン固有の例外定義。

```python
class UseCaseError(Exception):
    """ユースケースエラーの基底クラス"""
    pass

class UserAlreadyExistsError(UseCaseError):
    """メールアドレスが既に使用されている"""
    pass

class AuthenticationError(UseCaseError):
    """認証失敗"""
    pass
```

---

#### `src/use_cases/user.py`

ユーザー作成ユースケース。

```python
from sqlmodel import Session
from src.models.user import User
from src.schemas.user import UserCreate
from src.protocols.user import UserRepositoryProtocol
from src.security import get_password_hash
from src.use_cases.exceptions import UserAlreadyExistsError

def create_user(
    session: Session,
    *,
    user_repository: UserRepositoryProtocol,
    user_create: UserCreate
) -> User:
    """新しいユーザーを作成する"""

    # メールアドレスの重複チェック
    existing_user = user_repository.get_by_email(session, email=user_create.email)
    if existing_user:
        raise UserAlreadyExistsError(f"Email {user_create.email} already exists")

    # パスワードをハッシュ化
    hashed_password = get_password_hash(user_create.password)

    # リポジトリに委譲
    return user_repository.create(
        session,
        user_create=user_create,
        hashed_password=hashed_password
    )
```

**責務**:
- ビジネスルールの実行（メールアドレス重複チェック）
- パスワードのハッシュ化
- リポジトリへの委譲
- ドメイン例外のスロー

---

#### `src/use_cases/auth.py`

ログインユースケース。

```python
from datetime import timedelta
from sqlmodel import Session
from src.protocols.user import UserRepositoryProtocol
from src.security import verify_password, create_access_token
from src.settings import Settings
from src.use_cases.exceptions import AuthenticationError

settings = Settings()

def login(
    session: Session,
    *,
    user_repository: UserRepositoryProtocol,
    email: str,
    password: str
) -> str:
    """ユーザーをログインさせてJWTトークンを返す"""

    # ユーザーを取得
    user = user_repository.get_by_email(session, email=email)
    if not user:
        raise AuthenticationError("Invalid email or password")

    # パスワードを検証
    if not verify_password(password, user.hashed_password):
        raise AuthenticationError("Invalid email or password")

    # JWT トークンを生成
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=str(user.id), expires_delta=expires_delta)

    return access_token
```

---

#### `src/use_cases/issue.py`

Issue 関連のユースケース。

```python
from sqlmodel import Session
from src.models.user import User
from src.models.issue import Issue
from src.schemas.issue import IssueCreate
from src.protocols.issue import IssueRepositoryProtocol
from src.policies.issue import IssuePolicy

def create_issue(
    session: Session,
    *,
    current_user: User,
    issue_repository: IssueRepositoryProtocol,
    issue_create: IssueCreate
) -> Issue:
    """新しいIssueを作成する"""
    return issue_repository.create(
        session,
        issue_create=issue_create,
        owner_id=current_user.id
    )

def get_my_issues(
    session: Session,
    *,
    current_user: User,
    issue_repository: IssueRepositoryProtocol
) -> list[Issue]:
    """現在のユーザーが閲覧可能なIssueを取得"""
    policy = IssuePolicy(current_user)
    scope = policy.resolve_scope()
    return list(issue_repository.find_by_scope(session, scope=scope))

def add_collaborator(
    session: Session,
    *,
    issue_repository: IssueRepositoryProtocol,
    issue: Issue,
    user_to_add: User
) -> Issue:
    """Issueに共同作業者を追加する"""
    # 認可は deps.py の can_add_collaborator_to_issue で行われる
    issue_repository.add_collaborator(session, issue=issue, user=user_to_add)
    session.refresh(issue)
    return issue
```

**設計ポイント**:
- `get_my_issues()`: ポリシーからスコープを取得し、リポジトリに渡す
- 認可チェックは deps.py で実行（ユースケースは純粋なビジネスロジックのみ）

---

### 10. ポリシーレイヤー（認可ルール）

#### `src/policies/issue.py`

Issue に関する認可ポリシー。

```python
from sqlmodel import select, or_
from src.models.user import User
from src.models.issue import Issue
from src.models.collaborator import Collaborator

class IssuePolicy:
    def __init__(self, user: User):
        self.user = user

    def can_create(self) -> bool:
        """Issueを作成できるか"""
        return self.user is not None  # 認証済みユーザーなら可能

    def can_update(self, issue: Issue) -> bool:
        """Issueを更新できるか"""
        is_owner = self.user.id == issue.owner_id
        is_collaborator = self.user in issue.collaborators
        return is_owner or is_collaborator

    def can_delete(self, issue: Issue) -> bool:
        """Issueを削除できるか"""
        return self.user.id == issue.owner_id  # オーナーのみ可能

    def can_add_collaborator(self, issue: Issue, user_to_add: User) -> bool:
        """共同作業者を追加できるか"""
        # オーナーのみ可能
        if self.user.id != issue.owner_id:
            return False

        # オーナー自身は追加できない
        if user_to_add.id == issue.owner_id:
            return False

        # 既に共同作業者の場合は追加できない
        if user_to_add in issue.collaborators:
            return False

        return True

    def resolve_scope(self):
        """ユーザーが閲覧可能なIssueのスコープ（SQLAlchemyフィルタ）を返す"""
        return or_(
            Issue.owner_id == self.user.id,  # オーナーとして
            Issue.id.in_(  # または共同作業者として
                select(Collaborator.issue_id).where(
                    Collaborator.user_id == self.user.id
                )
            )
        )
```

**認可パターン**:
- **アクション系メソッド** (`can_create`, `can_update`, etc.): True/False を返す
- **スコープ解決** (`resolve_scope`): SQLAlchemy の WHERE 句を返す
- **用途**:
  - アクション系 → ルーターの依存性注入で使用
  - スコープ解決 → ユースケースでコレクションをフィルタリング

---

### 11. 依存性注入レイヤー

#### `src/api/deps.py`

FastAPI の依存性注入システムを使用した認証・認可・リソースローディング。

```python
from fastapi import Depends, HTTPException, status, Request, Path
from sqlmodel import Session
from jose import JWTError, jwt
from src.db import current_session
from src.models.user import User
from src.models.issue import Issue
from src.repositories.user import UserRepository
from src.repositories.issue import IssueRepository
from src.policies.issue import IssuePolicy
from src.settings import Settings

settings = Settings()

# =========================================
# 認証
# =========================================

def get_token_from_cookie(request: Request) -> str | None:
    """Cookieからトークンを取得"""
    return request.cookies.get("pysavor_access_token")

def get_current_user(
    session: Session = Depends(current_session),
    token: str | None = Depends(get_token_from_cookie),
) -> User:
    """現在のユーザーを取得（JWT検証）"""
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = UserRepository.get_by_id(session, id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user

# =========================================
# リソースローディング
# =========================================

def get_issue_by_id_from_path(
    issue_id: int = Path(..., gt=0),
    session: Session = Depends(current_session),
) -> Issue:
    """パスパラメータからIssueをロード"""
    issue = IssueRepository.get_by_id(session, id=issue_id)
    if issue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    return issue

def get_user_by_id_from_path(
    user_id: int = Path(..., gt=0, alias="user_id"),
    session: Session = Depends(current_session),
) -> User:
    """パスパラメータからUserをロード"""
    user = UserRepository.get_by_id(session, id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# =========================================
# 認可ガード
# =========================================

def can_create_issue(
    current_user: User = Depends(get_current_user)
) -> None:
    """Issue作成権限チェック"""
    policy = IssuePolicy(current_user)
    if not policy.can_create():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create issues"
        )

def can_update_issue(
    issue: Issue = Depends(get_issue_by_id_from_path),
    current_user: User = Depends(get_current_user),
) -> Issue:
    """Issue更新権限チェック"""
    policy = IssuePolicy(current_user)
    if not policy.can_update(issue):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this issue"
        )
    return issue

def can_delete_issue(
    issue: Issue = Depends(get_issue_by_id_from_path),
    current_user: User = Depends(get_current_user),
) -> Issue:
    """Issue削除権限チェック"""
    policy = IssuePolicy(current_user)
    if not policy.can_delete(issue):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this issue"
        )
    return issue

def can_add_collaborator_to_issue(
    issue: Issue = Depends(get_issue_by_id_from_path),
    user_to_add: User = Depends(get_user_by_id_from_path),
    current_user: User = Depends(get_current_user),
) -> Issue:
    """共同作業者追加権限チェック"""
    policy = IssuePolicy(current_user)
    if not policy.can_add_collaborator(issue, user_to_add):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add collaborators to this issue"
        )
    return issue
```

**依存性注入パターン**:
1. **認証**: `get_current_user()` - JWT を検証してユーザーを返す
2. **リソースローディング**: パスパラメータからリソースをロード、404 を返す
3. **認可ガード**: ポリシーを使用して権限チェック、403 を返す

---

### 12. API ルーターレイヤー

#### `src/api/routers/user.py`

ユーザー管理エンドポイント。

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.db import current_session
from src.schemas.user import UserCreate, UserRead
from src.use_cases.user import create_user
from src.use_cases.exceptions import UserAlreadyExistsError
from src.repositories.user import UserRepository

router = APIRouter()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(
    user_create: UserCreate,
    session: Session = Depends(current_session),
):
    """新しいユーザーを作成"""
    try:
        user = create_user(
            session,
            user_repository=UserRepository,
            user_create=user_create
        )
        return user
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
```

---

#### `src/api/routers/auth.py`

認証エンドポイント。

```python
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session
from src.db import current_session
from src.schemas.auth import LoginRequest
from src.use_cases.auth import login
from src.use_cases.exceptions import AuthenticationError
from src.repositories.user import UserRepository
from src.settings import Settings

router = APIRouter()
settings = Settings()

@router.post("/login")
def login_endpoint(
    login_request: LoginRequest,
    response: Response,
    session: Session = Depends(current_session),
):
    """ログインしてトークンをCookieに設定"""
    try:
        access_token = login(
            session,
            user_repository=UserRepository,
            email=login_request.email,
            password=login_request.password
        )

        # HTTP-only Secure Cookie にトークンを設定
        response.set_cookie(
            key="pysavor_access_token",
            value=access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax"
        )

        return {"message": "Login successful"}

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
```

---

#### `src/api/routers/issue.py`

Issue 管理エンドポイント。

```python
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from src.db import current_session
from src.models.user import User
from src.models.issue import Issue
from src.schemas.issue import IssueCreate, IssueRead
from src.use_cases.issue import create_issue, get_my_issues, add_collaborator
from src.api.deps import (
    get_current_user,
    can_create_issue,
    can_add_collaborator_to_issue
)
from src.repositories.issue import IssueRepository

router = APIRouter()

@router.post(
    "/",
    response_model=IssueRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(can_create_issue)]
)
def create_issue_endpoint(
    issue_create: IssueCreate,
    session: Session = Depends(current_session),
    current_user: User = Depends(get_current_user),
):
    """新しいIssueを作成"""
    issue = create_issue(
        session,
        current_user=current_user,
        issue_repository=IssueRepository,
        issue_create=issue_create
    )
    return issue

@router.get("/me", response_model=list[IssueRead])
def get_my_issues_endpoint(
    session: Session = Depends(current_session),
    current_user: User = Depends(get_current_user),
):
    """自分が閲覧可能なIssueを取得"""
    issues = get_my_issues(
        session,
        current_user=current_user,
        issue_repository=IssueRepository
    )
    return issues

@router.post(
    "/{issue_id}/collaborators/{user_id}",
    response_model=IssueRead
)
def add_collaborator_endpoint(
    issue: Issue = Depends(can_add_collaborator_to_issue),
    user_to_add: User = Depends(get_user_by_id_from_path),
    session: Session = Depends(current_session),
):
    """Issueに共同作業者を追加"""
    updated_issue = add_collaborator(
        session,
        issue_repository=IssueRepository,
        issue=issue,
        user_to_add=user_to_add
    )
    return updated_issue
```

**エンドポイント仕様**:

| メソッド | パス | 説明 | 認可 |
|---------|------|------|------|
| POST | `/api/v1/issues/` | Issue作成 | can_create_issue |
| GET | `/api/v1/issues/me` | 自分のIssue取得 | 認証のみ |
| POST | `/api/v1/issues/{issue_id}/collaborators/{user_id}` | 共同作業者追加 | can_add_collaborator_to_issue |

---

### 13. データベースマイグレーション

#### マイグレーション管理

Alembic を使用したスキーマバージョン管理。

**マイグレーション実行コマンド**:
```bash
# マイグレーション作成
alembic revision --autogenerate -m "description"

# マイグレーション適用
alembic upgrade head

# 現在のバージョン確認
alembic current

# マイグレーション履歴
alembic history
```

#### マイグレーション履歴

1. **f63635279097** - `users` テーブル作成
   - カラム: id, full_name, email, hashed_password
   - インデックス: email (UNIQUE), full_name

2. **6b277d0147af** - `issues` テーブル作成
   - カラム: id, title, description, owner_id
   - 外部キー: owner_id → users.id
   - インデックス: title

3. **875428da6c8e** - `collaborators` テーブル作成
   - カラム: issue_id, user_id
   - 複合主キー: (issue_id, user_id)
   - 外部キー: issue_id → issues.id, user_id → users.id

---

## データフロー

### 1. ユーザー登録フロー

```
1. クライアント
   POST /api/v1/users/
   Body: {"email": "user@example.com", "password": "password123", "full_name": "User Name"}
   ↓
2. user.py ルーター (create_user_endpoint)
   - リクエストボディを UserCreate に変換
   ↓
3. use_cases.user.create_user()
   - メールアドレス重複チェック
   - パスワードをハッシュ化（Bcrypt）
   ↓
4. repositories.user.create()
   - User オブジェクト作成
   - SQL: INSERT INTO users (email, full_name, hashed_password) VALUES (...)
   ↓
5. レスポンス
   201 Created
   Body: {"id": 1, "email": "user@example.com", "full_name": "User Name"}
```

---

### 2. ログインフロー

```
1. クライアント
   POST /api/v1/auth/login
   Body: {"email": "user@example.com", "password": "password123"}
   ↓
2. auth.py ルーター (login_endpoint)
   ↓
3. use_cases.auth.login()
   - メールアドレスでユーザー検索
   - パスワード検証（Bcrypt）
   - JWT トークン生成（HS256、30分有効）
   ↓
4. レスポンス
   200 OK
   Set-Cookie: pysavor_access_token=eyJ...; HttpOnly; Secure; SameSite=Lax
   Body: {"message": "Login successful"}
```

---

### 3. Issue 作成・共同作業フロー

```
1. Issue 作成
   POST /api/v1/issues/
   Cookie: pysavor_access_token=eyJ...
   Body: {"title": "New Feature", "description": "Description"}
   ↓
2. 認証・認可
   - get_current_user(): Cookie から JWT を取得・検証
   - can_create_issue(): ポリシーで権限チェック
   ↓
3. use_cases.issue.create_issue()
   - current_user.id を owner_id として設定
   ↓
4. repositories.issue.create()
   - SQL: INSERT INTO issues (title, description, owner_id) VALUES (...)
   ↓
5. レスポンス
   201 Created
   Body: {"id": 1, "title": "New Feature", "description": "Description", "owner_id": 1, "owner": {...}}

---

6. 共同作業者追加
   POST /api/v1/issues/1/collaborators/2
   Cookie: pysavor_access_token=eyJ...
   ↓
7. 認証・認可
   - get_current_user(): 現在のユーザー取得
   - get_issue_by_id_from_path(): Issue ID=1 をロード
   - get_user_by_id_from_path(): User ID=2 をロード
   - can_add_collaborator_to_issue():
     * オーナーのみ可能
     * オーナー自身は追加不可
     * 既存の共同作業者は追加不可
   ↓
8. use_cases.issue.add_collaborator()
   ↓
9. repositories.issue.add_collaborator()
   - issue.collaborators.append(user)
   - SQL: INSERT INTO collaborators (issue_id, user_id) VALUES (1, 2)
   ↓
10. レスポンス
    200 OK
    Body: {"id": 1, "title": "New Feature", ..., "collaborators": [...]}

---

11. 自分の Issue 取得
    GET /api/v1/issues/me
    Cookie: pysavor_access_token=eyJ...
    ↓
12. 認証
    - get_current_user(): 現在のユーザー取得
    ↓
13. use_cases.issue.get_my_issues()
    - IssuePolicy(current_user).resolve_scope() を呼び出し
    - SQLAlchemy フィルタを取得:
      WHERE (issues.owner_id = 1 OR issues.id IN (SELECT issue_id FROM collaborators WHERE user_id = 1))
    ↓
14. repositories.issue.find_by_scope()
    - SQL: SELECT * FROM issues WHERE (owner_id = 1 OR id IN (...))
    ↓
15. レスポンス
    200 OK
    Body: [{"id": 1, "title": "New Feature", ...}, ...]
```

---

## セキュリティ機構

### 1. パスワードセキュリティ

- **ハッシュアルゴリズム**: Bcrypt（`passlib[bcrypt]`）
- **ソルト**: 自動生成（Bcrypt デフォルト）
- **保存形式**: `$2b$12$...` (アルゴリズム + ソルト + ハッシュ)
- **検証**: `pwd_context.verify(plain_password, hashed_password)`

**実装**: `src/security.py:22-24`

---

### 2. JWT 認証

- **アルゴリズム**: HS256（HMAC SHA-256）
- **有効期限**: 30分（設定可能）
- **ペイロード**: `{"exp": timestamp, "sub": user_id}`
- **署名鍵**: `SECRET_KEY` 環境変数から取得

**トークン生成**: `src/security.py:10-18`
**トークン検証**: `src/api/deps.py:23-37`

---

### 3. Cookie ベース認証

- **Cookie 名**: `pysavor_access_token`
- **属性**:
  - `HttpOnly`: JavaScript からアクセス不可（XSS 対策）
  - `Secure`: HTTPS のみ送信（本番環境）
  - `SameSite=Lax`: CSRF 対策

**実装**: `src/api/routers/auth.py:28-34`

---

### 4. 認可システム

#### アクションベース認可（Ability-Based Authorization）

```python
# src/policies/issue.py
class IssuePolicy:
    def can_create(self) -> bool: ...
    def can_update(self, issue: Issue) -> bool: ...
    def can_delete(self, issue: Issue) -> bool: ...
    def can_add_collaborator(self, issue: Issue, user_to_add: User) -> bool: ...
```

#### スコープベース認可（Scope-Based Authorization）

```python
def resolve_scope(self):
    """ユーザーが閲覧可能な Issue の WHERE 句を返す"""
    return or_(
        Issue.owner_id == self.user.id,  # オーナーとして
        Issue.id.in_(...)  # 共同作業者として
    )
```

**適用箇所**:
- **アクション系**: ルーターの `dependencies=[Depends(can_create_issue)]`
- **スコープ系**: ユースケースの `find_by_scope(scope=policy.resolve_scope())`

---

### 5. セキュリティチェックリスト

| 項目 | 実装状況 | 実装箇所 |
|------|---------|---------|
| パスワードハッシュ化 | ✅ | `src/security.py:24` |
| JWT 署名検証 | ✅ | `src/api/deps.py:30-37` |
| トークン有効期限 | ✅ | `src/settings.py:7` |
| HttpOnly Cookie | ✅ | `src/api/routers/auth.py:31` |
| 認証チェック | ✅ | `src/api/deps.py:23-45` |
| 認可チェック | ✅ | `src/api/deps.py:74-135` |
| CSRF 対策 | ✅ | `src/api/routers/auth.py:33` (SameSite=Lax) |
| SQL インジェクション対策 | ✅ | SQLModel ORM 使用 |
| XSS 対策 | ✅ | FastAPI の自動エスケープ |

---

## 技術スタック

| カテゴリ | 技術 | バージョン | 用途 |
|---------|------|-----------|------|
| **言語** | Python | 3.12+ | プログラミング言語 |
| **Web フレームワーク** | FastAPI | 0.118+ | HTTP API サーバー |
| **ORM** | SQLModel | 0.0.25+ | データベースモデル + Pydantic スキーマ |
| **データベース** | SQLite | - | 開発用データベース |
| **マイグレーション** | Alembic | 1.16.5+ | スキーマバージョン管理 |
| **認証** | python-jose[cryptography] | 3.3+ | JWT トークンエンコード/デコード |
| **パスワード** | passlib[bcrypt] | 1.7.4+ | パスワードハッシング |
| **設定管理** | pydantic-settings | 2.11.0+ | 環境設定 |
| **パッケージマネージャー** | UV | - | 依存関係管理 |

---

## 設計パターンと規約

### 1. リポジトリパターン

```python
# 抽象インターフェース (Protocol)
class UserRepositoryProtocol(Protocol):
    def get_by_id(self, session: Session, *, id: int) -> User | None: ...

# 具象実装
class UserRepository:
    def get_by_id(self, session: Session, *, id: int) -> User | None:
        return session.get(User, id)
```

**利点**:
- ユースケースがデータアクセスの詳細から独立
- テスト時にモックを注入可能
- データベースを変更してもユースケースは不変

---

### 2. 依存性逆転の原則（Dependency Inversion Principle）

```
高レベルモジュール（use_cases）
         ↓ 依存
    抽象（protocols）
         ↑ 実装
低レベルモジュール（repositories）
```

**実装例**:
```python
def create_user(
    session: Session,
    *,
    user_repository: UserRepositoryProtocol,  # 抽象に依存
    user_create: UserCreate
) -> User:
    return user_repository.create(session, ...)
```

---

### 3. ポリシーオブジェクト（Policy Object）

認可ロジックを独立したクラスに分離。

```python
policy = IssuePolicy(current_user)
if not policy.can_update(issue):
    raise HTTPException(status_code=403)
```

**利点**:
- 認可ロジックの再利用性
- テストの容易性
- ビジネスルールの一元管理

---

### 4. FastAPI 依存性注入パターン

```python
@router.post("/", dependencies=[Depends(can_create_issue)])
def create_issue_endpoint(
    issue_create: IssueCreate,
    session: Session = Depends(current_session),
    current_user: User = Depends(get_current_user),
):
    ...
```

**パターン**:
- **認証**: `Depends(get_current_user)`
- **認可**: `dependencies=[Depends(can_create_issue)]`
- **リソースローディング**: `issue: Issue = Depends(get_issue_by_id_from_path)`

---

### 5. エラーハンドリングパターン

```
ドメイン例外（use_cases/exceptions.py）
         ↓ スロー
    ユースケース
         ↓ キャッチ
    ルーター
         ↓ 変換
  HTTP 例外（HTTPException）
```

**実装例**:
```python
try:
    user = create_user(...)
except UserAlreadyExistsError as e:
    raise HTTPException(status_code=409, detail=str(e))
```

---

### 6. トランザクション管理

```python
def current_session():
    with Session(engine) as session:
        yield session
        # 自動コミット・ロールバック
```

**特徴**:
- リクエストごとに新しいセッション
- コンテキストマネージャーで自動クリーンアップ
- 例外発生時は自動ロールバック

---

### 7. 命名規約

| 種類 | 規約 | 例 |
|------|------|-----|
| クラス | PascalCase | `User`, `IssueRepository` |
| 関数 | snake_case | `create_user`, `get_by_id` |
| 変数 | snake_case | `user_create`, `hashed_password` |
| 定数 | UPPER_SNAKE_CASE | `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES` |
| プライベート | `_` プレフィックス | `_hash_password` |
| Protocol | `Protocol` サフィックス | `UserRepositoryProtocol` |
| Schema | アクション + エンティティ | `UserCreate`, `IssueRead` |

---

### 8. SQLModel リレーションシップパターン

#### 1対多（User → Issues）

```python
# User モデル
issues: List["Issue"] = Relationship(back_populates="owner")

# Issue モデル
owner_id: int = Field(foreign_key="users.id")
owner: User = Relationship(back_populates="issues")
```

#### 多対多（User ↔ Issue via Collaborator）

```python
# User モデル
collaborated_issues: List["Issue"] = Relationship(
    back_populates="collaborators",
    link_model=Collaborator
)

# Issue モデル
collaborators: List[User] = Relationship(
    back_populates="collaborated_issues",
    link_model=Collaborator
)

# Collaborator モデル（結合テーブル）
issue_id: Optional[int] = Field(foreign_key="issues.id", primary_key=True)
user_id: Optional[int] = Field(foreign_key="users.id", primary_key=True)
```

---

## まとめ

**pysavor** は Clean Architecture の原則に基づき、以下の特徴を持つ設計となっています：

1. **明確なレイヤー分離**: API → ユースケース → リポジトリ → モデル
2. **依存性逆転**: 高レベルモジュールは抽象（Protocol）に依存
3. **テスト容易性**: モックを注入しやすい設計
4. **保守性**: 各コンポーネントが単一の責務を持つ
5. **拡張性**: 新機能追加が容易な構造
6. **セキュリティ**: JWT 認証、Bcrypt ハッシング、認可ガード

この設計により、ビジネスロジックがフレームワークから独立し、長期的な保守性と拡張性を確保しています。

---

**ドキュメントバージョン**: 1.0
**最終更新日**: 2025-10-21
**作成者**: Claude Code
