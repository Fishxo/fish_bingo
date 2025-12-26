# 🏗️ ARCHITECTURE ANALYSIS & PROBLEMS

## 📋 CURRENT STRUCTURE

### Process Groups (Fly.io)
- **gameplay**: Game APIs (Gunicorn + Uvicorn)
- **registration**: Registration + Telegram bot
- **admin**: Admin dashboard
- **celery**: Background tasks (single worker, 3 queues: gameplay, default, registration)
- **app**: Legacy (backward compatibility)

### Game Start Flow
1. `POST /api/games/{id}/start/` → `start_game()` view
2. Calls `start_game_logic()` → Updates DB (status='active')
3. Initializes Redis state → `initialize_game_live_state()`
4. Schedules Celery task → `task_call_next_number.apply_async(countdown=3)`
5. Task should run after 3 seconds → Call first number
6. Task reschedules itself → Continue calling numbers

### Number Calling System
- **NEW**: `task_call_next_number` (Redis-first, event-driven)
- **OLD**: `task_auto_call_numbers` (DB-heavy, still exists in code)

---

## ❌ PROBLEMS IDENTIFIED

### 1. **Task Not Executing**
- **Symptom**: Game starts, but no numbers are called
- **Evidence**: No logs from `task_call_next_number` in production
- **Possible Causes**:
  - Celery worker not picking up tasks
  - Task not registered properly
  - Queue routing not working
  - Task name mismatch

### 2. **Dual System Conflict**
- **Problem**: Both old (`task_auto_call_numbers`) and new (`task_call_next_number`) systems exist
- **Impact**: Confusion, potential conflicts, maintenance burden
- **Evidence**: Old task still has 15+ references in code

### 3. **Task Registration Issues**
- **Problem**: Using `@shared_task` with explicit `name='api.tasks.task_call_next_number'`
- **Issue**: Celery autodiscovery might not match names correctly
- **Evidence**: Tried explicit lookup with `current_app.tasks.get()` but still not working

### 4. **Redis State Management**
- **Problem**: Redis state initialization happens in view, but task might run before Redis is ready
- **Issue**: Race condition between DB update and Redis initialization
- **Evidence**: Task checks Redis state, but might find empty state

### 5. **Celery Worker Configuration**
- **Current**: Single worker listening to 3 queues (gameplay, default, registration)
- **Problem**: If worker is busy with other tasks, gameplay tasks wait
- **Issue**: No dedicated gameplay worker

### 6. **Error Visibility**
- **Problem**: No clear error messages when task fails to execute
- **Issue**: Silent failures, hard to debug
- **Evidence**: No logs = no visibility into what's happening

---

## 🔍 ROOT CAUSE HYPOTHESIS

**Most Likely**: Celery task is being scheduled but **not executed by worker**

**Why**:
1. Task is scheduled (we see scheduling logs)
2. Task never executes (no execution logs)
3. Worker might not be listening to `gameplay` queue
4. Or task name doesn't match what worker expects
5. Or worker isn't running at all

---

## 📊 CURRENT CODE STRUCTURE

### Task Definition
```python
@shared_task(bind=True, max_retries=2, queue='gameplay', name='api.tasks.task_call_next_number')
def task_call_next_number(self, game_id: int):
    # Redis-first number calling
    # Reads from Redis, calls number, schedules next
```

### Task Scheduling
```python
# In start_game view
task = current_app.tasks.get('api.tasks.task_call_next_number')
result = task.apply_async(args=[game.id], countdown=3)
```

### Celery Worker
```bash
celery -A bingo worker \
    --queues=gameplay,default,registration \
    --concurrency=3
```

---

## 🎯 WHAT'S NEEDED

### Option 1: Fix Current System
- Verify Celery worker is running
- Ensure task registration works
- Fix queue routing
- Add better error handling

### Option 2: Replace with Simpler System
- Remove Celery dependency for number calling
- Use Django background thread or asyncio
- Or use simple periodic task scheduler
- Or use Redis pub/sub for coordination

### Option 3: Hybrid Approach
- Keep Celery for heavy tasks (rewards, cleanup)
- Use simpler system for time-sensitive gameplay (number calling)
- Separate concerns: Celery = async work, Gameplay = real-time

---

## 📝 KEY METRICS

- **Task Scheduling**: ✅ Working (logs show scheduling)
- **Task Execution**: ❌ Not working (no execution logs)
- **Redis State**: ✅ Initialized (but task might not see it)
- **Worker Status**: ❓ Unknown (no visibility)
- **Queue Status**: ❓ Unknown (no visibility)

---

## 🔧 RECOMMENDED SOLUTION APPROACH

### Immediate Fix
1. **Verify Celery worker is running** on `celery` process group
2. **Check worker logs** for task reception
3. **Test task registration** with simple test task
4. **Verify queue exists** in Redis

### Long-term Solution
1. **Simplify number calling**: Remove Celery dependency
2. **Use Django async views** or background threads
3. **Or use Redis pub/sub** for real-time coordination
4. **Keep Celery only for** heavy async work (rewards, cleanup)

---

## 💡 ALTERNATIVE ARCHITECTURE

### Simple Background Thread Approach
```python
# In start_game view
import threading
def call_numbers_loop(game_id):
    while game_active:
        call_number(game_id)
        time.sleep(3)
thread = threading.Thread(target=call_numbers_loop, args=[game.id])
thread.daemon = True
thread.start()
```

### Redis Pub/Sub Approach
```python
# Publisher (when number called)
redis.publish(f'game:{game_id}:call', number)

# Subscriber (background thread)
pubsub = redis.pubsub()
pubsub.subscribe(f'game:{game_id}:call')
for message in pubsub.listen():
    process_number_call(message)
```

### Django Async View Approach
```python
# Use Django async views with asyncio
async def start_game(request, game_id):
    asyncio.create_task(call_numbers_loop(game_id))
    return Response(...)
```

---

## 🎯 DECISION POINTS

1. **Do we need Celery for number calling?**
   - Pro: Distributed, scalable
   - Con: Complex, hard to debug, overkill for simple loop

2. **What's the simplest solution?**
   - Background thread: Simple, but not distributed
   - Redis pub/sub: Distributed, but more complex
   - Django async: Modern, but requires async stack

3. **What's the most reliable?**
   - Background thread: Most reliable, least scalable
   - Celery: Most scalable, least reliable (current issue)
   - Hybrid: Best of both worlds

---

## 📋 SUMMARY

**Current Problem**: Celery task scheduled but not executing
**Root Cause**: Unknown (worker issue, registration issue, or routing issue)
**Impact**: Game starts but no numbers called
**Complexity**: High (Celery + Redis + Django + Fly.io process groups)

**Recommendation**: 
- **Short-term**: Fix Celery (verify worker, check logs, test registration)
- **Long-term**: Simplify (remove Celery for number calling, use simpler approach)

**Key Question**: Is Celery the right tool for time-sensitive, sequential number calling, or is it overkill?

