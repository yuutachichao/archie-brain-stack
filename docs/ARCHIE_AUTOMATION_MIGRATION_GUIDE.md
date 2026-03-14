# 全自動化安裝與移植技術文件（Archie 第二大腦）

> 目的：當你重灌/換電腦/換伺服器時，最快重建完整 Archie 系統。
> 範圍：Zeabur + GitHub + Ollama(bge-m3) + Postgres + Qdrant + FastAPI。

---

## 1) 環境變數鎖定（Variable Identification）

## 1.1 硬體建議
- **CPU-only 可跑**（小規模資料）
- 若有 GPU：建議 NVIDIA 8GB+ VRAM（加速 embedding/推論）
- RAM：至少 8GB（建議 16GB）
- 磁碟：至少 30GB（含 Ollama 模型與資料庫）

## 1.2 作業系統 / 執行環境
- Zeabur（託管容器）
- Python 3.11+
- Git
- Docker（若在自管主機）

## 1.3 必備環境變數（API 服務）
```env
API_KEY=<ARCHIE_API_KEY>
POSTGRES_URL=postgresql://<user>:<pass>@<host>:5432/<db>
QDRANT_URL=http://<qdrant-internal-host>:6333
QDRANT_API_KEY=<ARCHIE_QDRANT_API_KEY>
OLLAMA_URL=http://<ollama-internal-host>:11434
EMBEDDING_MODEL=bge-m3
EMBEDDING_PROVIDER=ollama
EMBEDDING_VERSION=v1
QDRANT_COLLECTION=archie_knowledge_bge_m3_v1
TOP_K_DEFAULT=8
CHUNK_SIZE=1200
CHUNK_OVERLAP=150
```

---

## 2) 標準化安裝流程（可複製）

## 2.1 GitHub 端
```bash
# 本地/工作區
cd /home/node/.openclaw/workspace/archie-brain-stack
git add .
git commit -m "deploy: update archie stack"
git push origin main
```

### 驗證（介入測試）
- GitHub repo 可看到最新 commit

## 2.2 Zeabur 建立服務
1. 建立 Project：`archie-brain`
2. 建立 4 服務：
   - `archie-brain-api`（From GitHub）
   - `archie-brain-postgres`
   - `archie-brain-qdrant`
   - `archie-brain-ollama`

### 驗證（介入測試）
- 4 服務都顯示 Running

## 2.3 API 服務部署模式固定
- 若誤判成 Caddy/靜態站，使用 repo 根目錄 `Dockerfile` 強制 Python API

### 驗證（介入測試）
- Runtime log 出現：`Uvicorn running on 0.0.0.0:8080`

## 2.4 內網 URL 與變數設定
- 從 Zeabur 取得可解析的 internal host
- 填入 `POSTGRES_URL/QDRANT_URL/OLLAMA_URL`（注意 POSTGRES_URL 必須是 DSN）

### 驗證（介入測試）
```bash
python3 -c "import urllib.request,os;print(urllib.request.urlopen(os.environ['OLLAMA_URL']+'/api/tags').status)"
python3 -c "import urllib.request,os;req=urllib.request.Request(os.environ['QDRANT_URL']+'/collections',headers={'api-key':os.environ['QDRANT_API_KEY']});print(urllib.request.urlopen(req).status)"
```
預期：兩個都 `200`

## 2.5 初始化模型與資料表
```bash
# 在 archie-brain-ollama terminal
ollama pull bge-m3
```

```bash
# 在 archie-brain-api terminal
python3 -c "import os,psycopg;sql=\"\"\"create table if not exists articles (id uuid primary key,title text,source_url text,source_type text,author text,language text,raw_content text,clean_content text,summary text,key_points jsonb default '[]'::jsonb,tags jsonb default '[]'::jsonb,assistant_notes text,status text default 'processed',created_at timestamptz default now()); create table if not exists article_chunks (id uuid primary key,article_id uuid references articles(id) on delete cascade,chunk_index int,chunk_text text,token_count int,embedding_provider text,embedding_model text,embedding_dim int,embedding_version text,qdrant_collection text,qdrant_point_id uuid,created_at timestamptz default now()); create table if not exists ingestion_logs (id bigserial primary key,source_url text,article_id uuid,status text,message text,created_at timestamptz default now()); create index if not exists idx_articles_created_at on articles(created_at desc); create index if not exists idx_chunks_article_id on article_chunks(article_id);\"\"\";conn=psycopg.connect(os.environ['POSTGRES_URL']);cur=conn.cursor();cur.execute(sql);conn.commit();cur.close();conn.close();print('DB schema initialized.')"
```

### 驗證（介入測試）
- 輸出 `DB schema initialized.`

## 2.6 端到端驗收
```bash
python3 -c "import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:8080/health').read().decode())"
python3 -c "import json,urllib.request,os;d={'title':'Archie 上線驗收','raw_content':'這是 Archie 第二大腦正式上線測試，主題是國二自然理化。','summary':'上線驗收測試','tags':['subject:自然-理化','type:課堂筆記','grade:國二']};req=urllib.request.Request('http://127.0.0.1:8080/ingest/article',data=json.dumps(d).encode(),headers={'Authorization':'Bearer '+os.environ['API_KEY'],'Content-Type':'application/json'},method='POST');print(urllib.request.urlopen(req).read().decode())"
python3 -c "import json,urllib.request,os;d={'query':'國二自然理化重點','top_k':3,'tags':[]};req=urllib.request.Request('http://127.0.0.1:8080/search',data=json.dumps(d).encode(),headers={'Authorization':'Bearer '+os.environ['API_KEY'],'Content-Type':'application/json'},method='POST');print(urllib.request.urlopen(req).read().decode())"
```

### 驗證（介入測試）
- health 回 `{"ok":true}`
- ingest 回 `{"ok":true,...}`
- search 回 `{"ok":true,"results":[...]}`

---

## 3) 環境移植關鍵（venv/路徑/備份）

## 3.1 你目前架構以容器為主
- 不依賴本機 venv/conda
- 核心是：`Git repo + Zeabur env + 資料卷`

## 3.2 要備份的關鍵資產
1. GitHub repo（程式與部署腳本）
2. Zeabur env 變數（遮罩後另存安全保管）
3. Postgres 資料（定期 dump）
4. Qdrant volume 快照

## 3.3 移植時路徑注意
- Zeabur 內部路徑由平台管理，不要硬編碼本機絕對路徑
- 服務間連線一律走 env

---

## 4) 坑點防禦（Reverse Interrogation）

## 錯誤 1：`dockerfile parse error unknown instruction: brain-api/Dockerfile`
- 原因：把 Dockerfile 路徑填到「Dockerfile 內容欄位」
- 解法：填完整 Dockerfile 內容，或改用根目錄 Dockerfile

## 錯誤 2：進 terminal 在 `/usr/share/caddy`，`python3` 不存在
- 原因：服務被誤判成靜態站（Caddy）
- 解法：強制 Docker 部署 Python API（確認 runtime log 有 uvicorn）

## 錯誤 3：`Name or service not known`
- 原因：OLLAMA/QDRANT host 不可解析
- 解法：改用 Zeabur 實際 internal host

## 錯誤 4：`missing "=" after ... in connection info string`
- 原因：`POSTGRES_URL` 只填 host，不是 DSN
- 解法：改為完整 `postgresql://...`

## 錯誤 5：`HTTP 500` 於 ingest
- 常見原因：
  1) bge-m3 未 pull
  2) DB schema 未初始化
  3) POSTGRES_URL 格式錯
- 解法：依序檢查模型、schema、DSN

## 錯誤 6：`curl: command not found`
- 原因：容器精簡
- 解法：改用 python3 + urllib 測試

---

## 5) 因果驗證（Intervention Test Checklist）

每一步完成後打勾：

- [ ] GitHub push 成功
- [ ] 4 服務 Running
- [ ] runtime log 出現 uvicorn
- [ ] Ollama tags 200
- [ ] Qdrant collections 200
- [ ] DB schema initialized
- [ ] health 成功
- [ ] ingest 成功
- [ ] search 命中剛寫入資料

全部打勾才算「可移植完成」。

---

## 6) 安全與收尾
- 任何貼過聊天室的 key 視同外洩，立即旋轉
- 正式環境一律 private repo
- API/Qdrant/Postgres 密碼分離，不共用
- 每次重建後執行第 5 節完整驗證
