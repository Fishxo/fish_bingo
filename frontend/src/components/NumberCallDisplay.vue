<template>
  <div class="number-call-display">
    <div class="current-call" v-if="currentCall">
      <div class="call-number">
        <span class="letter" :class="`letter-${currentCall.letter.toLowerCase()}`">
          {{ currentCall.letter }}
        </span>
        <span class="number">-{{ currentCall.number }}</span>
      </div>
    </div>
    <div class="recent-calls" v-if="recentCalls.length > 0">
      <div
        v-for="(call, idx) in getUniqueRecentCalls"
        :key="`${call.letter}-${call.number}-${idx}`"
        class="recent-call"
        :class="`call-${call.letter.toLowerCase()}`"
      >
        {{ call.letter }}{{ call.number }}
      </div>
    </div>
    <div v-else class="no-calls">
      <p>...</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NumberCallDisplay',
  props: {
    currentCall: {
      type: Object,
      default: null
    },
    recentCalls: {
      type: Array,
      default: () => []
    }
  },
  computed: {
    getUniqueRecentCalls() {
      // Get unique recent calls (last 3, no duplicates)
      const unique = []
      const seen = new Set()
      for (let i = this.recentCalls.length - 1; i >= 0 && unique.length < 3; i--) {
        const call = this.recentCalls[i]
        const key = `${call.letter}-${call.number}`
        if (!seen.has(key)) {
          seen.add(key)
          unique.unshift(call) // Add to beginning to maintain order
        }
      }
      return unique
    }
  }
}
</script>

<style scoped>
.number-call-display {
  background: var(--primary-dark);
  padding: 10px;
  border-radius: 16px;
  margin: 5px;
  text-align: center;
  width: 100%;
  box-sizing: border-box;
  box-shadow: var(--card-shadow);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.number-call-display.compact-call-display {
  width: 100%;
  max-width: 100%;
  padding: 5px;
  margin: 0 0 5px 0;
}

.current-call {
  margin-bottom: 8px;
}

.call-number {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: white;
  padding: 10px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.letter {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: white;
  font-weight: 700;
  font-size: 26px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.letter-b { background: var(--bingo-b); }
.letter-i { background: var(--bingo-i); }
.letter-n { background: var(--bingo-n); }
.letter-g { background: var(--bingo-g); }
.letter-o { background: var(--bingo-o); }

.number {
  font-size: 26px;
  font-weight: 700;
  color: var(--primary-dark);
}

.no-calls {
  color: white;
  font-size: 14px;
  padding: 10px;
}

.recent-calls {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.recent-call {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: white;
  font-weight: 700;
  font-size: 13px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.call-b { background: var(--bingo-b); }
.call-i { background: var(--bingo-i); }
.call-n { background: var(--bingo-n); }
.call-g { background: var(--bingo-g); }
.call-o { background: var(--bingo-o); }
</style>

