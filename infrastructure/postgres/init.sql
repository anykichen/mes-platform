-- MES 平台数据库初始化
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- 支持模糊搜索站点名

-- 设置时区
SET timezone = 'Asia/Bangkok';
