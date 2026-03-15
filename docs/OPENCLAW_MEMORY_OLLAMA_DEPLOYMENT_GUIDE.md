# OpenClaw 記憶搜尋與第二大腦連線部署指南

> 本文件記錄 OpenClaw 記憶搜尋（使用本地 Ollama）與第二大腦資料庫的連線部署流程。
> 適用於全新環境重建或迁移。

---

## 1. 環境需求

### 硬體需求
- **建議 CPU**：4 核心以上
- **建議 RAM**：8GB 以上（ Ollama 模型加載需要資源）
- **磁碟**：至少 20GB（模型與資料）

### 軟體需求
- **Git**：用於 Clone 程式碼
- **Python**：3.11+（如有需要）
- **Docker / Docker Compose**：如有自架需求
- **Zeabur 帳號**：如使用 Zeabur 部署

### 網路需求
- OpenClaw Gateway 必須能訪問 Ollama 服務（建議同一 Zeabur 專案，或使用公開網址）

---

## 2. 標準化安裝流程

### 2.1 建立 Ollama 服務（Zeabur）

1. 登入 Zeabur，進入 OpenClaw 專案
2. 點擊 **Add Service**
3. 選擇 **Ollama**（或 Docker image: `ollama/ollama`）
4. 服務名稱設為：`openclaw-ollama`
5. 建議開啟 **Volume**（保留模型）
6. 部署完成後，進入 Terminal

### 2.2 拉取 Embedding 模型

在 Ollama 容器 Terminal 中執行：

```bash
ollama pull bge-m3
```

### 2.3 取得 Ollama 公開網址

1. 進入 `openclaw-ollama` 服務頁面
2. 找到 **Domain** 或 **Public URL**
3. 複製產生的網址，例如：
   ```
   https://openclaw-ollama-20260315.zeabur.app
   ```

### 2.4 設定密碼保護（可選但建議）

在 `openclaw-ollama` 服務的 **Environment Variables** 中新增：

```
OLLAMA_ADMIN_KEY=你的密碼
```

重啟服務使密碼生效。

### 2.5 設定 OpenClaw 連線至本地 Ollama

在 OpenClaw Gateway Terminal 中依序執行：

```bash
# 設定記憶搜尋使用 Ollama
openclaw config set agents.defaults.memorySearch.provider "ollama"
openclaw config set agents.defaults.memorySearch.model "bge-m3"
openclaw config set agents.defaults.memorySearch.fallback "none"

# 設定 Ollama 模型列表（避免驗證錯誤）
openclaw config set models.providers.ollama.models "[]"

# 設定 Ollama 網址（使用公開網址）
openclaw config set models.providers.ollama.baseUrl "https://你的-ollama-網址.zeabur.app"

# 設定密碼（如有設定）
openclaw config set models.providers.ollama.apiKey "你的密碼"
```

### 2.6 重啟 OpenClaw Gateway

```bash
openclaw restart
```

或在 Zeabur 中重啟 openclaw 服務。

---

## 3. 環境移植關鍵

### 3.1 必須備份的設定

- `openclaw.json`：OpenClaw 主設定檔
- `MEMORY.md`：長期記憶檔案
- `memory/` 目錄：日常記憶檔案

### 3.2 必須記錄的資訊

- Ollama 公開網址
- Ollama API 密碼（如有設定）
- Ollama 模型名稱（預設 `bge-m3`）

### 3.3 搬遷時的重點

1. 先在新環境建立 Ollama 服務
2. 確保模型已拉取（`ollama pull bge-m3`）
3. 設定公開網址
4. 修改 OpenClaw 設定中的 `baseUrl`
5. 重啟 OpenClaw Gateway

---

## 4. 坑點防禦：常見錯誤與解決對策

### 錯誤 1：`fetch failed`

**原因**：OpenClaw 無法連線至 Ollama（內網 DNS 不通）

**解決對策**：
- 確認 Ollama 服務是否正常運行
- 確認網址是否正確
- 改用 **公開網址** 而非內網網址

---

### 錯誤 2：`billing_not_active` / `quota exhausted`

**原因**：預設雲端 Embedding 服務額度用盡

**解決對策**：
- 參考本文件設定本地 Ollama
- 或充值雲端服務

---

### 錯誤 3：`Failed to discover Ollama models`

**原因**：Ollama 服務未正常運行或網址錯誤

**解決對策**：
- 確認 Ollama 容器是否 Running
- 確認 `baseUrl` 是否正確（需包含 `https://`）
- 確認模型是否已成功拉取（`ollama list`）

---

### 錯誤 4：密碼驗證失敗

**原因**：API Key 與 Ollama 設定的密碼不一致

**解決對策**：
- 確認 `models.providers.ollama.apiKey` 與 `OLLAMA_ADMIN_KEY` 一致

---

### 錯誤 5：跨專案內網不通

**原因**：Zeabur 不同專案之間的內網 DNS 不互通

**解決對策**：
- 使用 Ollama 的公開網址
- 或在同專案內建立 Ollama

---

## 5. 因果驗證：每步驗證指令

### 步驟 1：確認 Ollama 運行

```bash
curl -s https://你的-ollama-網址.zeabur.app/api/tags | head -c 200
```

**預期輸出**：JSON 格式的模型列表

---

### 步驟 2：確認模型已拉取

在 Ollama 容器中執行：

```bash
ollama list
```

**預期輸出**：應看到 `bge-m3`

---

### 步驟 3：確認 OpenClaw 設定

```bash
openclaw config get agents.defaults.memorySearch
```

**預期輸出**：
```json
{
  "provider": "ollama",
  "model": "bge-m3",
  "fallback": "none"
}
```

---

### 步驟 4：確認 Ollama 連線資訊

```bash
openclaw config get models.providers.ollama
```

**預期輸出**：
```json
{
  "baseUrl": "https://your-ollama-url.zeabur.app",
  "apiKey": "***",
  "models": []
}
```

---

### 步驟 5：測試記憶搜尋

對 OpenClaw 說：

```
測試記憶搜尋，請找出我之前說過要用繁體中文
```

**預期輸出**：找到相關記憶內容，且 `provider` 顯示為 `ollama`

---

## 6. 部署檢查清單

- [ ] Ollama 服務建立並執行中
- [ ] bge-m3 模型已拉取
- [ ] 公開網址已取得
- [ ] 密碼已設定（可選）
- [ ] OpenClaw 設定已更新
- [ ] Gateway 已重啟
- [ ] 記憶搜尋功能正常運作

---

## 7. 相關參考文件

- [Zeabur 官方文件](https://zeabur.com)
- [Ollama 官方文件](https://github.com/ollama/ollama)
- [OpenClaw 文件](./ARCHIE_AUTOMATION_MIGRATION_GUIDE.md)（第二大腦部署）
