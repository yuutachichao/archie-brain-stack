# OPENCLAW_INTEGRATION_CHECKLIST

> 目的：當你新增一套 OpenClaw（例如孩子、家人、分身助理）時，快速接上既有第二大腦。

---

## 1. 新 OpenClaw 如何接第二大腦

### 必要條件
- 已存在可用的 second brain API
- 已知：
  - `api_url`
  - `api_key`
- 新 OpenClaw 可寫入自己的 workspace

### 最小接線步驟
1. 在新 OpenClaw 的 workspace 建立：
   - `brain-tools/brain_config.json`
   - `brain-tools/brain_search.py`
   - `brain-tools/brain_push.py`
2. `brain_config.json` 內容：

```json
{
  "api_url": "https://your-brain-api.example.com",
  "api_key": "YOUR_API_KEY"
}
```

3. 驗證搜尋：
```bash
python3 /path/to/brain-tools/brain_search.py "國二理化重點" --top-k 3
```

4. 驗證寫入：
```bash
python3 /path/to/brain-tools/brain_push.py --title "接線測試" --raw-content "這是一筆 OpenClaw 接線測試資料。" --summary "integration test" --tags test integration
```

---

## 2. 公開網址 vs 內網網址：怎麼判斷

## 優先判斷
### 用內網網址的情況
- OpenClaw 和 second brain 在**同一 Zeabur 專案**
- 服務 host 可以互相解析
- 已確認 `http://service-xxxx:8080` 可通

### 用公開網址的情況
- OpenClaw 和 second brain 在**不同 Zeabur 專案**
- 內網 DNS 無法互通
- 出現 `Name or service not known`
- 想快速打通，不想先處理網路隔離

## 判斷原則
- **同專案優先內網**
- **不同專案優先公開網址**
- 若內網測不到，直接切公開網址，不要硬耗

---

## 3. 最後驗收標準

## A. 搜尋成功
應回傳：
- `ok: true`
- `results: [...]`
- 至少一筆命中結果（若資料庫已有內容）

## B. 寫入成功
應回傳：
- `ok: true`
- `article_id`
- `chunks`

## C. 實際可用
至少完成以下 3 件事：
1. 查得到既有內容
2. 能寫入一筆新資料
3. 寫入後立刻能搜到剛寫入內容

> 這 3 項都過，才算「正式接通」。

---

## 4. 常見失敗原因

### 4.1 DNS 無法解析
**症狀**
- `Name or service not known`

**原因**
- 不同專案內網不互通

**解法**
- 改用公開網址

### 4.2 API key 錯誤
**症狀**
- 401 unauthorized

**原因**
- `brain_config.json` 的 key 錯
- key 已旋轉但 OpenClaw 還在用舊的

**解法**
- 更新 `api_key`

### 4.3 工具檔缺漏
**症狀**
- `No such file or directory`
- 找不到 `brain_search.py` / `brain_push.py`

**解法**
- 重建 `brain-tools/` 三個檔案

### 4.4 容器缺少 curl / requests
**症狀**
- `curl: command not found`
- `ModuleNotFoundError: requests`

**解法**
- 優先使用 `python3 + urllib`
- 工具腳本盡量避免依賴 requests

### 4.5 API 有通但寫入失敗
**症狀**
- search OK，但 ingest 500

**原因**
- 後端 second brain 本身有問題（DB/Qdrant/Ollama/schema）

**解法**
- 回頭檢查 second brain 的 deploy playbook
- 不要先懷疑 OpenClaw 工具

---

## 5. 建議的標準流程

1. 先決定用內網還是公開網址
2. 建立 `brain-tools/`
3. 先測搜尋
4. 再測寫入
5. 再測「寫入後能被搜尋到」
6. 成功後記錄到文件與 changelog

---

## 6. 接通成功的定義

當你看到以下結果，就代表成功：
- 搜尋測試：成功
- 寫入測試：成功
- 寫入後查詢：成功
- Bot 可正常接受「查第二大腦 / 存進第二大腦」類型任務
