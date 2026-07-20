<template>
  <div class="card-picker">
    <div class="picker-legend" aria-hidden="true">
      <span class="legend-item"><span class="dot dot-free"></span> ባዶ</span>
      <span class="legend-item"><span class="dot dot-mine"></span> የኔ</span>
      <span class="legend-item"><span class="dot dot-busy"></span> የተያዘ</span>
    </div>

    <div class="cards-grid">
      <button
        v-for="num in cardNumbers"
        :key="num"
        type="button"
        class="card-option"
        :class="{
          taken: isTaken(num) && selectedCard !== num,
          selected: selectedCard === num
        }"
        :disabled="isTaken(num) && selectedCard !== num"
        :aria-label="cardAriaLabel(num)"
        :aria-pressed="selectedCard === num"
        @click="selectCard(num)"
      >
        <span v-if="selectedCard === num" class="selected-mark" aria-hidden="true">✓</span>
        <span class="card-num">{{ num }}</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardSelector',
  props: {
    availableCards: {
      type: Array,
      default: () => []
    },
    takenCards: {
      type: Array,
      default: () => []
    },
    selectedCard: {
      type: Number,
      default: null
    },
    totalCards: {
      type: Number,
      default: 200
    }
  },
  computed: {
    cardNumbers() {
      return Array.from({ length: this.totalCards }, (_, i) => i + 1)
    }
  },
  methods: {
    isTaken(num) {
      return this.takenCards.includes(num)
    },
    cardAriaLabel(num) {
      if (this.selectedCard === num) return `Cartela ${num}, yours`
      if (this.isTaken(num)) return `Cartela ${num}, taken`
      return `Cartela ${num}, available`
    },
    selectCard(num) {
      if (!this.isTaken(num) || this.selectedCard === num) {
        this.$emit('select-card', num)
      }
    }
  }
}
</script>

<style scoped>
.card-picker {
  padding: 0;
}

.picker-legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-bottom: 14px;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  color: var(--picker-legend-text, #475569);
  letter-spacing: 0.02em;
}

.dot {
  width: 14px;
  height: 14px;
  border-radius: 5px;
  flex-shrink: 0;
}

.dot-free {
  background: var(--picker-free-bg, #fff);
  border: 2px solid var(--picker-free-border, #94a3b8);
}

.dot-mine {
  background: var(--picker-mine-bg, #0d9488);
  border: 2px solid var(--picker-mine-border, #0f766e);
  box-shadow: 0 0 0 2px rgba(13, 148, 136, 0.25);
}

.dot-busy {
  background: var(--picker-busy-bg, #e2e8f0);
  border: 1px solid var(--picker-busy-border, #cbd5e1);
  opacity: 0.85;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 6px;
}

.card-option {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin: 0;
  padding: 0;
  appearance: none;
  -webkit-appearance: none;
  border-radius: 9px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;

  /* Available — quiet, easy to scan */
  background: var(--picker-free-bg, #fff);
  color: var(--picker-free-text, #64748b);
  border: 1.5px solid var(--picker-free-border, #cbd5e1);
  font-weight: 400;
  font-size: 13px;
  min-height: 28px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.card-num {
  line-height: 1;
}

.card-option:hover:not(:disabled):not(.selected) {
  background: var(--picker-free-hover-bg, #f0fdfa);
  border-color: var(--picker-free-hover-border, #5eead4);
  color: var(--picker-free-hover-text, #0f766e);
  transform: translateY(-1px);
}

.card-option:focus-visible {
  outline: 2px solid var(--picker-mine-bg, #0d9488);
  outline-offset: 2px;
}

/* Taken — faded, never loud (no orange) */
.card-option.taken {
  background: var(--picker-busy-bg, #eef2f6);
  color: var(--picker-busy-text, #a8b4c4);
  border-color: var(--picker-busy-border, #e2e8f0);
  font-weight: 400;
  font-size: 12px;
  cursor: not-allowed;
  opacity: 0.55;
  box-shadow: none;
}

.card-option.taken .card-num {
  text-decoration: line-through;
  text-decoration-thickness: 1px;
}

/* Your card — only strong highlight on the page */
.card-option.selected {
  background: linear-gradient(160deg, #14b8a6 0%, var(--picker-mine-bg, #0d9488) 50%, #0f766e 100%);
  color: #fff;
  font-weight: 800;
  font-size: 14px;
  border: 2px solid #fff;
  outline: 2px solid var(--picker-mine-bg, #0d9488);
  transform: scale(1.1);
  box-shadow:
    0 0 0 3px rgba(13, 148, 136, 0.3),
    0 8px 18px rgba(15, 118, 110, 0.35);
  z-index: 2;
  opacity: 1;
}

.card-option.selected.taken {
  cursor: pointer;
}

.selected-mark {
  position: absolute;
  top: 1px;
  right: 2px;
  font-size: 8px;
  font-weight: 900;
  width: 13px;
  height: 13px;
  border-radius: 50%;
  background: #fff;
  color: #0f766e;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

@media (max-width: 420px) {
  .cards-grid {
    gap: 4px;
  }

  .card-option {
    font-size: 11px;
    border-radius: 7px;
  }

  .card-option.selected {
    font-size: 12px;
    transform: scale(1.08);
  }

  .legend-item {
    font-size: 10px;
  }
}
</style>
