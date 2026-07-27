---
title: Clean Up Event Listeners and Intervals in onUnmounted
impact: HIGH
impactDescription: Failing to clean up side effects causes memory leaks and ghost event handlers
type: capability
tags: [vue3, lifecycle, memory-leak, event-listeners, intervals, cleanup]
---

# Clean Up Event Listeners and Intervals in onUnmounted

**Impact: HIGH** - Failing to clean up event listeners, intervals, timeouts, and subscriptions when a component unmounts causes memory leaks and ghost handlers that continue running, leading to performance degradation and subtle bugs in Single Page Applications.

When using custom events, timers, WebSocket connections, or third-party libraries, always clean up in `onUnmounted`.

## Task Checklist

- [ ] Track all addEventListener calls and remove them in onUnmounted
- [ ] Clear all setInterval and setTimeout calls in onUnmounted
- [ ] Unsubscribe from external event emitters and observables
- [ ] Disconnect WebSocket connections and third-party library instances
- [ ] Use `onBeforeUnmount` if cleanup must happen before DOM removal

**Incorrect:**
```javascript
// Composition API - WRONG: No cleanup
import { onMounted } from 'vue'

export default {
  setup() {
    onMounted(() => {
      // These keep running after component unmounts!
      window.addEventListener('resize', handleResize)
      setInterval(pollServer, 5000)
      socket.on('message', handleMessage)
    })
  }
}
```

**Correct:**
```javascript
// Composition API - CORRECT: Proper cleanup
import { onMounted, onUnmounted, ref } from 'vue'

export default {
  setup() {
    const intervalId = ref(null)

    const handleResize = () => {
      // handle resize
    }

    const handleMessage = (msg) => {
      // handle message
    }

    onMounted(() => {
      window.addEventListener('resize', handleResize)
      intervalId.value = setInterval(pollServer, 5000)
      socket.on('message', handleMessage)
    })

    onUnmounted(() => {
      // Clean up everything!
      window.removeEventListener('resize', handleResize)

      if (intervalId.value) {
        clearInterval(intervalId.value)
      }

      socket.off('message', handleMessage)
    })
  }
}
```

## Using Composable Pattern for Auto-Cleanup

```javascript
// Reusable composable with automatic cleanup
import { onMounted, onUnmounted } from 'vue'

export function useEventListener(target, event, handler) {
  onMounted(() => {
    target.addEventListener(event, handler)
  })

  onUnmounted(() => {
    target.removeEventListener(event, handler)
  })
}

export function useInterval(callback, delay) {
  let intervalId = null

  onMounted(() => {
    intervalId = setInterval(callback, delay)
  })

  onUnmounted(() => {
    if (intervalId) clearInterval(intervalId)
  })
}

// Usage - cleanup is automatic
import { useEventListener, useInterval } from './composables'

export default {
  setup() {
    useEventListener(window, 'resize', handleResize)
    useInterval(pollServer, 5000)
    // No manual cleanup needed!
  }
}
```

## Alternativa via @maxvue/max-use (VueUse)

No engeapp, os composables do VueUse são consumidos SEMPRE via `@maxvue/max-use` (que reexporta o VueUse); nunca importe direto de `@vueuse/core`.

```javascript
// @maxvue/max-use reexporta os composables cleanup-aware do VueUse
import { useEventListener, useIntervalFn } from '@maxvue/max-use'

export default {
  setup() {
    // Automatically cleaned up on unmount
    useEventListener(window, 'resize', handleResize)

    const { pause, resume } = useIntervalFn(pollServer, 5000)
    // Also provides pause/resume controls
  }
}
```

## Reference
- [Vue.js Lifecycle Hooks](https://vuejs.org/guide/essentials/lifecycle.html)
- [VueUse - useEventListener](https://vueuse.org/core/useEventListener/) (no engeapp, importe via `@maxvue/max-use`)
