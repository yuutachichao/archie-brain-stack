# Archie Brain Stack（國二學習版）

這份模板提供完整獨立部署：
- Postgres（結構化資料）
- Qdrant（向量庫）
- Ollama（embedding）
- brain-api（ingest/search）

## 1. 快速啟動

```bash
cp .env.example .env
# 編輯 .env，至少改掉 API_KEY / QDRANT_API_KEY / POSTGRES_PASSWORD

docker compose up -d --build
```

健康檢查：
```bash
curl http://localhost:8080/health
```

## 2. 下載 embedding 模型

```bash
docker exec -it archie-ollama ollama pull bge-m3
```

## 3. API 測試

### 寫入
```bash
curl -X POST http://localhost:8080/ingest/article \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"測試文章",
    "raw_content":"這是 Archie 第二大腦測試內容",
    "summary":"測試",
    "tags":["subject:自然-理化","grade:國二"]
  }'
```

### 搜尋
```bash
curl -X POST http://localhost:8080/search \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"query":"理化重點","top_k":3,"tags":[]}'
```

## 4. 使用本地工具

```bash
cd brain-tools
cp archie_config.json.example archie_config.json
# 填入 api_url / api_key

python3 archie_search.py "能源危機" --top-k 3
python3 archie_push.py --title "測試" --raw-content "內容" --tags subject:社會-地理 grade:國二
```

## 5. 建議的科目 tags

- subject:國文
- subject:英語
- subject:數學
- subject:自然-生物
- subject:自然-理化
- subject:自然-地球科學
- subject:社會-地理
- subject:社會-歷史
- subject:社會-公民
- grade:國二
- type:課堂筆記 / type:考前複習 / type:錯題

## 6. GitHub 部署建議（已附 workflow）

1. 建立新 repo：`archie-brain-stack`
2. 把這個目錄整包 push 上去
3. 在新伺服器預先安裝：`git`、`docker`、`docker compose`
4. 在伺服器建立：`/opt/archie-brain-stack/.env`（由 `.env.example` 複製）
5. 到 GitHub repo secrets 設定：
   - `SSH_PRIVATE_KEY`
   - `SERVER_HOST`
   - `SERVER_USER`
   - `APP_DIR`（例：`/opt/archie-brain-stack`）
   - `REPO_URL`（例：`git@github.com:you/archie-brain-stack.git`）
   - `BRANCH`（例：`main`）
6. push 到 `main` 後會自動 SSH 部署（見 `.github/workflows/deploy.yml`）

> 機密值（API_KEY 等）只放伺服器 `.env`，不要進 Git。

## 7. 備份（重要）

- Postgres：`pg_dump`
- Qdrant：備份 `qdrant_data` volume

建議每週至少備份一次。
