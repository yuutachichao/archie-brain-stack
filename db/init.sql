create table if not exists articles (
  id uuid primary key,
  title text,
  source_url text,
  source_type text,
  author text,
  language text,
  raw_content text,
  clean_content text,
  summary text,
  key_points jsonb default '[]'::jsonb,
  tags jsonb default '[]'::jsonb,
  assistant_notes text,
  status text default 'processed',
  created_at timestamptz default now()
);

create table if not exists article_chunks (
  id uuid primary key,
  article_id uuid references articles(id) on delete cascade,
  chunk_index int,
  chunk_text text,
  token_count int,
  embedding_provider text,
  embedding_model text,
  embedding_dim int,
  embedding_version text,
  qdrant_collection text,
  qdrant_point_id uuid,
  created_at timestamptz default now()
);

create table if not exists ingestion_logs (
  id bigserial primary key,
  source_url text,
  article_id uuid,
  status text,
  message text,
  created_at timestamptz default now()
);

create index if not exists idx_articles_created_at on articles(created_at desc);
create index if not exists idx_chunks_article_id on article_chunks(article_id);
