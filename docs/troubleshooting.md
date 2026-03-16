# Brain-API Troubleshooting Guide

## 問題：新增 DELETE 端點後出現 500 錯誤

### 錯誤訊息
```
TypeError: Object of type UUID is not JSON serializable
```

### 發生情境
在 brain-api 新增 `DELETE /article/{article_id}` 端點，用於刪除文章及其向量。

### 根本原因
從 PostgreSQL 查詢回來的 `qdrant_point_id` 是 UUID 物件，無法直接轉換成 JSON 傳給 Qdrant API。

### 解決方法
將 UUID 轉換為字串：

```python
# 錯誤寫法
point_ids = [row[0] for row in cur.fetchall()]

# 正確寫法
point_ids = [str(row[0]) for row in cur.fetchall()]
```

### 完整 DELETE 端點範例

```python
@app.delete("/article/{article_id}")
def delete_article(article_id: str, authorization: Optional[str] = Header(default=None)):
    check_auth(authorization)
    
    # 1. Get all chunk IDs for this article
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select qdrant_point_id from article_chunks where article_id = %s",
                (article_id,),
            )
            point_ids = [str(row[0]) for row in cur.fetchall()]  # 注意這裡用 str()
    
    # 2. Delete vectors from Qdrant
    if point_ids:
        qres = requests.post(
            f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/delete",
            json={"points": point_ids},
            headers=QDRANT_HEADERS,
            timeout=60,
        )
        if qres.status_code not in (200, 201):
            pass
    
    # 3. Delete from PostgreSQL (chunks first, then article)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("delete from article_chunks where article_id = %s", (article_id,))
            cur.execute("delete from articles where id = %s", (article_id,))
            conn.commit()
    
    return {"ok": True, "deleted": article_id, "vectors_deleted": len(point_ids)}
```

### 除錯技巧
1. **查看 Zeabur Container Logs**：部署後如有 500 錯誤，去 Zeabur 後台看 logs
2. **先測試 GET**：確認 API 運作正常，再測試 DELETE
3. **UUID 轉字串**：任何從資料庫拿出來的 UUID，在傳給 JSON API 前都要轉成 str()

---

**更新時間**：2026-03-16
