# Memory Optimization for Markos Bingo

## Problem
The application crashed with OOM (Out of Memory) error on Fly.io. Celery worker was killed due to memory exhaustion.

## Root Causes
1. **Limited VM Memory**: `shared-cpu-2x` VM has only 512MB RAM by default
2. **High Celery Concurrency**: Running 2 concurrent workers doubles memory usage
3. **Multiple Processes**: Django app + Telegram bot + Celery worker all in one VM
4. **No Memory Limits**: No limits on worker memory or task execution
5. **Potential Memory Leaks**: Long-running tasks without worker recycling

## Optimizations Applied

### 1. Increased VM Memory (fly.toml)
- Added explicit `memory_mb = 1024` to allocate 1GB RAM
- This costs ~$5/month but prevents crashes

### 2. Reduced Celery Concurrency (fly.toml)
- Changed from `--concurrency=2` to `--concurrency=1`
- Reduces memory usage by 50% for workers
- Added `--max-tasks-per-child=50` to restart workers after 50 tasks (prevents memory leaks)
- Added `--max-memory-per-child=200000` to kill workers exceeding 200MB

### 3. Celery Memory Settings (settings.py)
- `CELERY_WORKER_MAX_TASKS_PER_CHILD = 50`: Restart worker after 50 tasks
- `CELERY_WORKER_MAX_MEMORY_PER_CHILD = 200000`: Kill worker if >200MB (in KB)
- `CELERY_WORKER_POOL = 'solo'`: Use single-threaded pool (lower memory)
- `CELERY_TASK_IGNORE_RESULT = True`: Don't store task results
- `CELERY_RESULT_EXPIRES = 3600`: Expire results after 1 hour

### 4. Database Connection Optimization (settings.py)
- Added query timeout: `statement_timeout=30000` (30 seconds)
- Kept `CONN_MAX_AGE = 300` (5 minutes) to prevent stale connections

## Cost Impact
- **Memory Increase**: ~$5/month for 1GB RAM (from 512MB)
- **Total Estimated Cost**: ~$5-10/month for stable operation

## Alternative: Further Optimizations (If Still Having Issues)

### Option 1: Split Processes
Run Celery worker in a separate VM:
```toml
[[services]]
  processes = ["app"]

[[services]]
  processes = ["worker"]
  [services.vm]
    memory_mb = 512
```

### Option 2: Use Celery Beat for Scheduled Tasks
Move periodic tasks to Celery Beat to reduce worker load.

### Option 3: Optimize Task Code
- Use `select_related()` and `prefetch_related()` in queries
- Clear large objects after use
- Use generators instead of lists for large datasets
- Limit query result sets

## Monitoring
Monitor memory usage with:
```bash
fly ssh console -a markos-bingo
free -h
ps aux | grep celery
```

## Deployment
After these changes, deploy with:
```bash
fly deploy -a markos-bingo
```

## Expected Results
- Celery workers should use <200MB each
- Total memory usage should stay under 1GB
- Workers will restart automatically after 50 tasks
- No more OOM crashes

