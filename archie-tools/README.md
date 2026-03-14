# archie-tools 使用說明

## 1) 設定
```bash
cp archie_config.json.example archie_config.json
```

編輯 `archie_config.json`：
```json
{
  "api_url": "http://localhost:8080",
  "api_key": "你的_archie_api_key"
}
```

## 2) 搜尋
```bash
python3 archie_search.py "自然-理化 重點" --top-k 5
```

## 3) 寫入
```bash
python3 archie_push.py \
  --title "理化複習：酸鹼中和" \
  --raw-content "酸鹼中和重點..." \
  --summary "本篇整理酸鹼中和觀念" \
  --tags subject:自然-理化 type:考前複習 grade:國二
```

## 4) 建議
- 每篇都帶上 `subject:*` + `type:*` + `grade:國二`
- 之後搜尋可用：
  - 「查我的數學錯題」
  - 「整理社會-地理考前重點」
