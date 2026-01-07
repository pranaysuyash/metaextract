# Database Performance Indexes Quick Reference

## Migration 009: Metadata Operations Indexes

### metadata_store Table
| Index Name | Columns | Purpose | Query Pattern |
|------------|---------|---------|---------------|
| `idx_metadata_store_file_hash` | file_path | Fast file lookups | `WHERE file_path = ?` |
| `idx_metadata_store_user_created` | user_id, extracted_at DESC | User-based time queries | `WHERE user_id = ? ORDER BY extracted_at DESC` |
| `idx_metadata_store_type_tier` | file_type, tier_used | Type/tier analytics | `WHERE file_type = ? AND tier_used = ?` |
| `idx_metadata_store_extracted_fields` | extracted_at DESC, total_fields_extracted DESC | Recent extraction analysis | `ORDER BY extracted_at DESC, total_fields_extracted DESC` |
| `idx_metadata_store_metadata_gin` | metadata (GIN) | JSONB searches | `WHERE metadata->>'key' = ?` |

### field_analytics Table
| Index Name | Columns | Purpose | Query Pattern |
|------------|---------|---------|---------------|
| `idx_field_analytics_name_type` | field_name, field_type | Field type queries | `WHERE field_name = ? AND field_type = ?` |
| `idx_field_analytics_count_date` | extraction_count DESC, last_extracted_at DESC | Popular fields analysis | `ORDER BY extraction_count DESC` |
| `idx_field_analytics_file_types` | file_types (GIN) | File type filtering | `WHERE file_types @> ?` |
| `idx_field_analytics_examples_gin` | example_values (GIN) | Example value searches | JSONB field searches |

### ui_events Table
| Index Name | Columns | Purpose | Query Pattern |
|------------|---------|---------|---------------|
| `idx_ui_events_time_product` | created_at DESC, product | Time-product analytics | `WHERE created_at > ? AND product = ?` |
| `idx_ui_events_user_product_time` | user_id, product, created_at DESC | User activity tracking | `WHERE user_id = ? AND product = ?` |
| `idx_ui_events_session_time` | session_id, created_at DESC | Session analysis | `WHERE session_id = ? ORDER BY created_at DESC` |
| `idx_ui_events_properties_gin` | properties (GIN) | Event property searches | `WHERE properties->>'key' = ?` |

## Migration 010: JOIN Operations Indexes

### Users and Credit System
| Index Name | Columns | Purpose | Query Pattern |
|------------|---------|---------|---------------|
| `idx_users_email_lower` | LOWER(email) | Case-insensitive email lookup | `WHERE LOWER(email) = LOWER(?)` |
| `idx_users_created` | created_at DESC | Recent user analysis | `ORDER BY created_at DESC` |
| `idx_credit_balances_user_created` | user_id, created_at DESC | User balance history | `WHERE user_id = ? ORDER BY created_at DESC` |
| `idx_credit_transactions_user_time` | balance_id, created_at DESC | Transaction history | `WHERE balance_id = ? ORDER BY created_at DESC` |

### Trial and Usage Tracking
| Index Name | Columns | Purpose | Query Pattern |
|------------|---------|---------|---------------|
| `idx_trial_usages_email_lower` | LOWER(email) | Email-based trial lookup | `WHERE LOWER(email) = LOWER(?)` |
| `idx_trial_usages_session_created` | session_id, used_at DESC | Session trial tracking | `WHERE session_id = ? ORDER BY used_at DESC` |
| `idx_trial_usages_user_created` | user_id, used_at DESC | User trial history | `WHERE user_id = ? ORDER BY used_at DESC` |

### Files and Metadata
| Index Name | Columns | Purpose | Query Pattern |
|------------|---------|---------|---------------|
| `idx_files_metadata_join` | id, file_type | Files with metadata | JOIN optimization |
| `idx_files_analytics` | file_type, extracted_at DESC | File analytics queries | `WHERE file_type = ? ORDER BY extracted_at DESC` |
| `idx_files_size_range` | file_size | Size-based queries | `WHERE file_size BETWEEN ? AND ?` |
| `idx_files_recent` | extracted_at DESC | Recent files filter | Recent file queries |

### JOIN Optimization
| Index Name | Columns | Purpose | Query Pattern |
|------------|---------|---------|---------------|
| `idx_favorites_files_join` | file_id, added_at DESC | Favorites with files | JOIN optimization |
| `idx_version_history_files_join` | file_id, changed_at DESC | Version history | JOIN optimization |
| `idx_perceptual_hashes_files_join` | file_id | Perceptual hash joins | JOIN optimization |
| `idx_metadata_category_key_value` | category, key, value | Metadata filtering | `WHERE category = ? AND key = ? AND value = ?` |

## Query Optimization Examples

### Fast Metadata Search
```sql
-- Uses: idx_metadata_store_metadata_gin
SELECT file_path, total_fields_extracted
FROM metadata_store 
WHERE metadata->>'camera_make' = 'Canon'
  AND (indexed_fields->>'processing_time')::numeric < 1000
ORDER BY extracted_at DESC
LIMIT 10;
```

### User Activity Analytics
```sql
-- Uses: idx_ui_events_user_product_time, idx_ui_events_time_product
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    product,
    COUNT(*) as event_count
FROM ui_events 
WHERE user_id = 'user123' 
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at), product
ORDER BY hour DESC;
```

### File Type Analytics
```sql
-- Uses: idx_metadata_store_type_tier, idx_metadata_store_extracted_fields
SELECT 
    file_type,
    tier_used,
    COUNT(*) as file_count,
    AVG(total_fields_extracted) as avg_fields
FROM metadata_store 
WHERE file_type IN ('image', 'video', 'audio')
  AND extracted_at > NOW() - INTERVAL '7 days'
GROUP BY file_type, tier_used
ORDER BY file_count DESC;
```

### Complex JOIN Optimization
```sql
-- Uses: idx_users_email_lower, idx_credit_balances_user_created, idx_credit_transactions_user_time
SELECT 
    u.email,
    cb.credits,
    COUNT(ct.id) as transaction_count,
    SUM(CASE WHEN ct.type = 'debit' THEN ct.amount ELSE 0 END) as total_debits
FROM users u
JOIN credit_balances cb ON u.id = cb.user_id
LEFT JOIN credit_transactions ct ON cb.id = ct.balance_id
WHERE LOWER(u.email) = LOWER('user@example.com')
  AND ct.created_at > NOW() - INTERVAL '30 days'
GROUP BY u.email, cb.credits
ORDER BY transaction_count DESC;
```

## Performance Monitoring

### Check Index Usage
```sql
SELECT schemaname, tablename, indexname, 
       idx_tup_read, idx_tup_fetch,
       ROUND(idx_tup_fetch::numeric / NULLIF(idx_tup_read, 0) * 100, 2) as hit_ratio
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY idx_tup_read DESC;
```

### Monitor Slow Queries
```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000; -- 1 second
SELECT pg_reload_conf();

-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements 
WHERE mean_time > 100  -- 100ms
ORDER BY mean_time DESC;
```

### Index Maintenance
```sql
-- Update statistics
ANALYZE;

-- Check index bloat
SELECT schemaname, tablename, indexname, 
       pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Troubleshooting

### Index Not Being Used
1. **Check statistics**: Run `ANALYZE` to update table statistics
2. **Check selectivity**: Indexes work best on selective queries
3. **Check data types**: Ensure consistent data types in comparisons
4. **Use explicit casting**: `WHERE column::text = 'value'`

### Slow Queries Despite Indexes
1. **Check query plan**: Use `EXPLAIN (ANALYZE, BUFFERS)` 
2. **Check index selectivity**: May need different column order
3. **Consider composite indexes**: Single column indexes may not be sufficient
4. **Check for functions on columns**: `WHERE UPPER(column) = 'VALUE'` prevents index usage

### High Index Maintenance
1. **Monitor write performance**: Indexes slow down INSERT/UPDATE
2. **Remove unused indexes**: Check `pg_stat_user_indexes` for zero usage
3. **Consider partial indexes**: Reduce maintenance overhead
4. **Batch operations**: Group multiple changes into transactions

## Quick Commands

### Apply All Indexes
```bash
psql -h localhost -U postgres -d metaextract -f server/migrations/009_performance_indexes_metadata.sql
psql -h localhost -U postgres -d metaextract -f server/migrations/010_performance_indexes_joins.sql
```

### Check Index Sizes
```sql
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
       pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as indexes_size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Drop Specific Index (if needed)
```sql
DROP INDEX IF EXISTS idx_metadata_store_file_hash;
```

### Rebuild Index (if fragmented)
```sql
REINDEX INDEX CONCURRENTLY idx_metadata_store_file_hash;
```