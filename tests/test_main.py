import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from api.db import get_db, Base
from api.main import app
import starlette.status

ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """
    - 非同期のオンメモリSQLiteエンジンとセッションを作成
    - テーブルを初期化
    - DB依存関係 (get_db) をテスト用に差し替え
    - LifespanManager を使ってアプリの起動/終了イベントを制御しながら、
      ASGITransport 経由で直接アプリにリクエストを送る AsyncClient を作成
    """

    # 1. 非同期エンジンとセッションの用意
    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
    async_session = sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
    )

    # 2. テスト用にテーブルを初期化
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # 3. DB依存関係を上書き
    async def get_test_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    # 4. LifespanManager を使ってアプリの lifespan を管理しつつ、
    #    ASGITransport を利用してネットワーク経由ではなく直接アプリへリクエストを送る
    async with LifespanManager(app):
        transport = ASGITransport(app=app)  # lifespan 引数は削除
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client


@pytest.mark.asyncio
async def test_create_and_read(async_client: AsyncClient):
    # 1. タスクを新規作成
    response = await async_client.post("/tasks", json={"title": "テストタスク"})
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "テストタスク"

    # 2. タスク一覧を取得し、件数・内容を検証
    response = await async_client.get("/tasks")
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()

    assert len(response_obj) == 1
    assert response_obj[0]["title"] == "テストタスク"
    assert response_obj[0]["is_done"] is False
