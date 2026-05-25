-- station_summary 按月分区
-- 每月手动或通过脚本创建，示例：2025年全年

ALTER TABLE station_summary PARTITION BY RANGE (report_date);

CREATE TABLE station_summary_2025_01 PARTITION OF station_summary
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE station_summary_2025_02 PARTITION OF station_summary
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE station_summary_2025_03 PARTITION OF station_summary
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

CREATE TABLE station_summary_2025_04 PARTITION OF station_summary
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');

CREATE TABLE station_summary_2025_05 PARTITION OF station_summary
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');

CREATE TABLE station_summary_2025_06 PARTITION OF station_summary
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');

CREATE TABLE station_summary_2025_07 PARTITION OF station_summary
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

CREATE TABLE station_summary_2025_08 PARTITION OF station_summary
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

CREATE TABLE station_summary_2025_09 PARTITION OF station_summary
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');

CREATE TABLE station_summary_2025_10 PARTITION OF station_summary
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

CREATE TABLE station_summary_2025_11 PARTITION OF station_summary
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE station_summary_2025_12 PARTITION OF station_summary
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');
