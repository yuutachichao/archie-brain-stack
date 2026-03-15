# 快速部署 Prompt 參考

> 以後遇到要部署新服務、修復問題時，直接複製這份 prompt 使用。

---

## 基本環境確認

```bash
# 確認目前環境
hostname
env | grep -E 'SERVICE|OLLAMA|POSTGRES|OPENCLAW|ZEABUR'
```

---

## Ollama 部署檢查清單

```bash
# 1. 建立 Ollama 服務（Zeabur）
# 2. 拉模型
ollama pull bge-m3

# 3. 取得公開網址
# （在 Zeabur 取得網址）

# 4. 設定密碼（可選）
# OLLAMA_ADMIN_KEY=你的密碼

# 5. 設定 OpenClaw
openclaw config set agents.defaults.memorySearch.provider "ollama"
openclaw config set agents.defaults.memorySearch.model "bge-m3"
openclaw config set agents.defaults.memorySearch.fallback "none"
openclaw config set models.providers.ollama.models "[]"
openclaw config set models.providers.ollama.baseUrl "https://你的-ollama-網址"
openclaw config set models.providers.ollama.apiKey "你的密碼"

# 6. 重啟
openclaw restart
```

---

## 驗證指令

```bash
# 測 Ollama
curl -s https://你的-ollama-網址/api/tags | head -c 200

# 測 OpenClaw 設定
openclaw config get agents.defaults.memorySearch
openclaw config get models.providers.ollama

# 測記憶搜尋
（對 OpenClaw 說：測試記憶搜尋，請找出我之前說過要用繁體中文）
```

---

## 常見錯誤速查

| 錯誤 | 原因 | 解法 |
| ---- | ---- | ---- |
| fetch failed | 連不上 Ollama | 檢查 URL、密碼 |
| billing_not_active | 雲端額度用完 | 改用本地 Ollama |
| 內網不通 | Zeabur 跨專案限制 | 用公開網址 |
| 密碼錯誤 | API Key 不一致 | 確認兩邊密碼相同 |

---

## 關鍵字

- Ollama
- Zeabur
- 公開網址
- 內網 DNS
- OpenClaw
- memory_search
- embedding

---

> 用 Ctrl+F 快速搜尋！
