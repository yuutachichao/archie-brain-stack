# Zeabur 第二大腦部署踩坑與除錯實錄（Playbook）

> 目的：下次重建新資料庫時，直接照這份排查，不再重踩同樣的坑。

---

## 0. 最終成功配置（先看）

- API：FastAPI + uvicorn（不是 Caddy）
- Embedding：Ollama `bge-m3`
- Vector DB：Qdrant（API key 驗證）
- SQL：Postgres（`POSTGRES_URL` 必須是完整 DSN）
- 驗收：`health -> ingest -> search` 全通

---

## 1. 常見坑位與對應解法

## 坑 1：服務跑成 Caddy（`/usr/share/caddy`）
**症狀**
- Terminal 在 `/usr/share/caddy`
- `python3` / `bash` 不存在

**原因**
- Zeabur 將服務誤判成靜態站

**解法**
1. 強制 Docker 部署（使用 repo 根 `Dockerfile`）
2. Redeploy
3. 確認 Runtime logs 有：`Uvicorn running on 0.0.0.0:8080`

---

## 坑 2：Dockerfile parse error (`unknown instruction: brain-api/Dockerfile`)
**症狀**
- Build fail: `unknown instruction`

**原因**
- 把 Dockerfile 路徑填在「Dockerfile 內容欄位」

**解法**
- 欄位貼完整 Dockerfile 內容，或改用根目錄 Dockerfile

---

## 坑 3：`unknown url type: ollama_url=http`
**症狀**
- urllib 報 `unknown url type`

**原因**
- env 值誤填成 `OLLAMA_URL=http://...`（值內又包含變數名）

**解法**
- env 值只能是純網址：`http://...`

---

## 坑 4：`Name or service not known`
**症狀**
- `OLLAMA_URL` / `QDRANT_URL` 連線失敗，DNS 無法解析

**原因**
- `.zeabur.internal` 別名在該環境不可解析

**解法**
- 改用 Zeabur 實際可解析的 service host（`service-xxxxx`）

---

## 坑 5：Qdrant 401 Unauthorized
**症狀**
- `/collections` 回 401

**原因**
- `QDRANT_API_KEY`（API 端）與 `QDRANT__SERVICE__API_KEY`（Qdrant 端）不一致

**解法**
1. 兩邊 key 設成完全一致
2. Redeploy API（headers 於啟動時載入）

---

## 坑 6：`missing "=" after ... in connection info string`
**症狀**
- psycopg 解析 DSN 失敗

**原因**
- `POSTGRES_URL` 只填 host/IP，不是完整 DSN

**解法**
- 必須使用：`postgresql://user:pass@host:5432/db`

---

## 坑 7：Postgres 密碼驗證失敗
**症狀**
- `FATAL: password authentication failed for user "root"`

**原因**
- DB 真實密碼與 API 內 `POSTGRES_URL` 不一致
- 只改 env 不一定改到既有 Postgres 使用者密碼

**解法（最穩）**
1. 在 Postgres 容器執行：
   ```bash
   psql -U root -d zeabur -c "ALTER USER root WITH PASSWORD 'NEW_PASSWORD';"
   ```
2. API 的 `POSTGRES_URL` 同步改成新密碼
3. Redeploy API
4. 驗證 `select 1`

---

## 坑 8：`ingest` 500 但 `search` 空陣列
**症狀**
- `search` 可回應但沒資料
- `ingest` 500

**常見原因**
- DB schema 未初始化
- DB 連線失敗

**解法**
- 初始化資料表（articles/article_chunks/ingestion_logs）
- 驗證 `select count(*) from articles`

---

## 2. 標準化快速診斷順序（5 分鐘）

1. 看 Runtime logs 是否 uvicorn
2. `echo` 核心 env：
   - `POSTGRES_URL`
   - `OLLAMA_URL`
   - `QDRANT_URL`
3. 連通性測試：
   - `OLLAMA_URL/api/tags` -> 200
   - `QDRANT_URL/collections` + api-key -> 200
4. DB 測試：
   - `select 1` -> `(1,)`
5. E2E：
   - `health` -> `ingest` -> `search`

---

## 3. 一鍵驗證指令集合（容器內）

```bash
python3 -c "import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:8080/health').read().decode())"
python3 -c "import os,psycopg;conn=psycopg.connect(os.environ['POSTGRES_URL']);cur=conn.cursor();cur.execute('select 1');print(cur.fetchone());cur.close();conn.close()"
python3 -c "import urllib.request,os;print(urllib.request.urlopen(os.environ['OLLAMA_URL']+'/api/tags').status)"
python3 -c "import urllib.request,os;req=urllib.request.Request(os.environ['QDRANT_URL']+'/collections',headers={'api-key':os.environ['QDRANT_API_KEY']});print(urllib.request.urlopen(req).status)"
```

---

## 4. 收尾與安全

- 任何曾貼在聊天室的密碼/key 視同外洩，必須旋轉
- 文檔更新後立即 commit + push
- 每次重建都跑一遍本 Playbook
