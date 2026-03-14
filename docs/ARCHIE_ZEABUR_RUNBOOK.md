# Archie 第二大腦（Zeabur）最終部署手冊

> 最後驗證狀態：`health` ✅ / `ingest` ✅ / `search` ✅

## A. 最終架構
- `archie-brain-api`（FastAPI）
- `archie-brain-postgres`（結構化資料）
- `archie-brain-qdrant`（向量庫）
- `archie-brain-ollama`（embedding）

## B. 實際部署重點（已踩坑修正版）

1. GitHub repo：`yuutachichao/archie-brain-stack`（private）
2. API 服務若被 Zeabur 誤判成 Caddy，使用 repo 根目錄 `Dockerfile` 強制走 Python API
3. `POSTGRES_URL` 必須是完整 DSN：
   - `postgresql://user:pass@host:5432/db`
   - **不能只填 host/IP**
4. `OLLAMA_URL` / `QDRANT_URL` 要用 Zeabur 內網可解析 host（service id host），不要硬寫可能失效的別名

## C. archie-brain-api 必備環境變數
- `API_KEY=<ARCHIE_API_KEY>`
- `POSTGRES_URL=<完整 postgresql://... 連線字串>`
- `QDRANT_URL=http://<QDRANT_INTERNAL_HOST>:6333`
- `QDRANT_API_KEY=<ARCHIE_QDRANT_API_KEY>`
- `OLLAMA_URL=http://<OLLAMA_INTERNAL_HOST>:11434`
- `EMBEDDING_MODEL=bge-m3`
- `EMBEDDING_PROVIDER=ollama`
- `EMBEDDING_VERSION=v1`
- `QDRANT_COLLECTION=archie_knowledge_bge_m3_v1`
- `TOP_K_DEFAULT=8`
- `CHUNK_SIZE=1200`
- `CHUNK_OVERLAP=150`

## D. 初始化（必要）

### 1) Ollama 拉模型
```bash
ollama pull bge-m3
```

### 2) 初始化 PostgreSQL schema（首次）
```bash
python3 -c "import os,psycopg;sql=\"\"\"create table if not exists articles (id uuid primary key,title text,source_url text,source_type text,author text,language text,raw_content text,clean_content text,summary text,key_points jsonb default '[]'::jsonb,tags jsonb default '[]'::jsonb,assistant_notes text,status text default 'processed',created_at timestamptz default now()); create table if not exists article_chunks (id uuid primary key,article_id uuid references articles(id) on delete cascade,chunk_index int,chunk_text text,token_count int,embedding_provider text,embedding_model text,embedding_dim int,embedding_version text,qdrant_collection text,qdrant_point_id uuid,created_at timestamptz default now()); create table if not exists ingestion_logs (id bigserial primary key,source_url text,article_id uuid,status text,message text,created_at timestamptz default now()); create index if not exists idx_articles_created_at on articles(created_at desc); create index if not exists idx_chunks_article_id on article_chunks(article_id);\"\"\";conn=psycopg.connect(os.environ['POSTGRES_URL']);cur=conn.cursor();cur.execute(sql);conn.commit();cur.close();conn.close();print('DB schema initialized.')"
```

## E. 驗收指令（容器內本機）

### health
```bash
python3 -c "import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:8080/health').read().decode())"
```

### ingest
```bash
python3 -c "import json,urllib.request,os;d={'title':'Archie 上線驗收','raw_content':'這是 Archie 第二大腦正式上線測試，主題是國二自然理化。','summary':'上線驗收測試','tags':['subject:自然-理化','type:課堂筆記','grade:國二']};req=urllib.request.Request('http://127.0.0.1:8080/ingest/article',data=json.dumps(d).encode(),headers={'Authorization':'Bearer '+os.environ['API_KEY'],'Content-Type':'application/json'},method='POST');print(urllib.request.urlopen(req).read().decode())"
```

### search
```bash
python3 -c "import json,urllib.request,os;d={'query':'國二自然理化重點','top_k':3,'tags':[]};req=urllib.request.Request('http://127.0.0.1:8080/search',data=json.dumps(d).encode(),headers={'Authorization':'Bearer '+os.environ['API_KEY'],'Content-Type':'application/json'},method='POST');print(urllib.request.urlopen(req).read().decode())"
```

## F. 安全收尾
- 已外露過的密鑰全部旋轉（API/Qdrant/Postgres）
- 新密鑰只保留在 Zeabur env / 本機安全檔，不貼聊天室
- 建議每次重建後先做一次 `health -> ingest -> search` 三步驗收
