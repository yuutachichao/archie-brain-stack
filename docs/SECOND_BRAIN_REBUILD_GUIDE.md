# 第二大腦重建教學

> 本文件記錄如何從零開始建立第二大腦系統（PostgreSQL + Qdrant + Ollama + brain-api）

---

## 系統架構

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  brain-api  │────▶│  PostgreSQL  │     │   Qdrant   │
│  (FastAPI)  │     │  (結構化資料) │     │  (向量資料庫)│
└─────────────┘     └─────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │   articles  │     │  vectors    │
                    │ article_    │     │  (bge-m3)   │
                    │   chunks    │     └─────────────┘
                    └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Ollama    │
                    │ (embedding) │
                    └─────────────┘
```

---

## 方法一：本地 Docker 部署（推薦开发/测试用）

### 1. 準備環境

```bash
#  clone repo
git clone https://github.com/yuutachichao/archie-brain-stack.git
cd archie-brain-stack

# 複製環境變數範例
cp .env.example .env
```

### 2. 編輯 .env

```env
# PostgreSQL
POSTGRES_DB=archie
POSTGRES_USER=archie
POSTGRES_PASSWORD=your_secure_password

# Qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=your_qdrant_key

# Ollama
OLLAMA_URL=http://ollama:11434

# brain-api
API_KEY=your_api_key
EMBEDDING_MODEL=bge-m3
EMBEDDING_PROVIDER=ollama
QDRANT_COLLECTION=knowledge_bge_m3_v1
```

### 3. 啟動服務

```bash
docker compose up -d --build
```

### 4. 下載 Embedding 模型

```bash
docker exec -it archie-ollama ollama pull bge-m3
```

### 5. 驗證

```bash
curl http://localhost:8080/health
```

---

## 方法二：Zeabur 雲端部署（推薦正式使用）

### 1. 準備 Zeabur 專案

1. 註冊 [Zeabur](https://zeabur.com)
2. 建立新專案

### 2. 建立服務

#### 2.1 PostgreSQL
- Add Service → Marketplace → PostgreSQL
- 設定資料庫名稱、用戶名、密碼

#### 2.2 Qdrant
- Add Service → Marketplace → Qdrant
- 設定 API Key

#### 2.3 Ollama
- 使用 Docker 模板
- Image: `ollama/ollama:latest`
- 環境變數: 無需特殊設定
- Port: 11434

#### 2.4 brain-api（從 GitHub 部署）
- Add Service → GitHub
- 選擇 `yuutachichao/archie-brain-stack`
- 路徑：`/brain-api`
- 環境變數：
  ```
  POSTGRES_URL=postgresql://user:password@host:port/db
  QDRANT_URL=https://xxx.zeabur.app
  QDRANT_API_KEY=your_key
  OLLAMA_URL=https://xxx.zeabur.app
  API_KEY=your_api_key
  EMBEDDING_MODEL=bge-m3
  QDRANT_COLLECTION=knowledge_bge_m3_v1
  ```

### 3. 初始化資料庫

#### 3.1 建立資料表

連線到 PostgreSQL（可用 Zeabur 的 Data Editor 或外部工具），執行：

```sql
CREATE TABLE IF NOT EXISTS articles (
  id uuid PRIMARY KEY,
  title text,
  source_url text,
  source_type text,
  author text,
  language text,
  raw_content text,
  clean_content text,
  summary text,
  key_points jsonb DEFAULT '[]'::jsonb,
  tags jsonb DEFAULT '[]'::jsonb,
  assistant_notes text,
  status text DEFAULT 'processed',
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS article_chunks (
  id uuid PRIMARY KEY,
  article_id uuid REFERENCES articles(id) ON DELETE CASCADE,
  chunk_index int,
  chunk_text text,
  token_count int,
  embedding_provider text,
  embedding_model text,
  embedding_dim int,
  embedding_version text,
  qdrant_collection text,
  qdrant_point_id uuid,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ingestion_logs (
  id bigserial PRIMARY KEY,
  source_url text,
  article_id uuid,
  status text,
  message text,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chunks_article_id ON article_chunks(article_id);
```

> 注意：`db/init.sql` 會自動執行，但建議手動確認資料表已建立

### 4. 部署 Ollama 模型

在 Ollama 服務的 Console 或透過 API：

```bash
curl -X POST https://your-ollama.zeabur.app/api/pull -d '{"name":"bge-m3"}'
```

### 5. 驗證

```bash
curl https://your-brain-api.zeabur.app/health
```

---

## API 使用方式

### 寫入文章

```bash
curl -X POST "https://your-brain-api.zeabur.app/ingest/article" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "文章標題",
    "source_url": "https://example.com",
    "raw_content": "文章內容...",
    "summary": "摘要",
    "tags": ["tag1", "tag2"]
  }'
```

### 搜尋文章

```bash
curl -X POST "https://your-brain-api.zeabur.app/search" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "搜尋關鍵字",
    "top_k": 5
  }'
```

### 刪除文章

```bash
curl -X DELETE "https://your-brain-api.zeabur.app/article/ARTICLE_ID" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 常見問題

### Q1: 如何備份資料？

**PostgreSQL**:
```bash
pg_dump -h host -U user -d db > backup.sql
```

**Qdrant**:
- Zeabur 會自動備份
- 或使用 Qdrant Cloud 的備份功能

### Q2: API 一直返回 500 錯誤？

1. 檢查環境變數是否正確
2. 確認 PostgreSQL 和 Qdrant 服務正常運作
3. 查看 Zeabur logs：`Zeabur Dashboard → brain-api → Logs`

### Q3: 向量搜尋沒有結果？

1. 確認 Ollama 模型已下載：`curl https://your-ollama.zeabur.app/api/tags`
2. 確認 Qdrant collection 存在
3. 檢查文章是否已成功寫入

### Q4: 如何更新 brain-api？

1. 在 GitHub 更新 `brain-api/app/main.py`
2. Zeabur 會自動偵測並重新部署

---

## 相關檔案

- `db/init.sql` - 資料庫結構
- `brain-api/app/main.py` - API 原始碼
- `docker-compose.yml` - 本地開發用
- `docs/troubleshooting.md` - 除錯指南

---

**更新時間**: 2026-03-16
