<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useMouse, useWindowSize } from '@vueuse/core'
import { Plus, Pill, Heart, Shield, Activity, Stethoscope, Syringe, Thermometer } from 'lucide-vue-next'

const { x: mouseX, y: mouseY } = useMouse()
const { width, height } = useWindowSize()

interface FloatingIcon {
  id: number
  icon: any
  size: number
  y: number
  baseX: number
  speed: number
  offsetX: number
  offsetY: number
  rotation: number
  rotSpeed: number
  opacity: number
}

const icons = [Plus, Pill, Heart, Shield, Activity, Stethoscope, Syringe, Thermometer]
const floatingItems = ref<FloatingIcon[]>([])

const initIcons = () => {
  floatingItems.value = Array.from({ length: 200 }).map((_, i) => {
    return {
      id: i,
      icon: icons[Math.floor(Math.random() * icons.length)],
      size: 18 + Math.random() * 18, // 18 to 36
      y: Math.random() * 100,
      baseX: Math.random() * 100,
      speed: 0.03 + Math.random() * 0.08,
      offsetX: 0,
      offsetY: 0,
      rotation: Math.random() * 360,
      rotSpeed: (Math.random() - 0.5) * 2,
      opacity: 0.35 + Math.random() * 0.45 // 35% to 80%
    }
  })
}

let rafId: number

const updatePositions = () => {
  const w = width.value
  const h = height.value
  const mX = mouseX.value
  const mY = mouseY.value
  
  // Check if mouse has actually moved from (0,0)
  const isMouseActive = mX > 0 || mY > 0

  floatingItems.value.forEach((item) => {
    item.y -= item.speed
    if (item.y < -10) {
      item.y = 110
      item.baseX = Math.random() * 100
    }

    const itemPX = (item.baseX / 100) * w
    const itemPY = (item.y / 100) * h

    let attractX = 0
    let attractY = 0

    if (isMouseActive) {
      const dx = mX - itemPX
      const dy = mY - itemPY
      const distance = Math.sqrt(dx * dx + dy * dy)
      const radius = 400

      if (distance < radius && distance > 10) {
        const force = (radius - distance) / radius
        attractX = (dx / distance) * force * 120
        attractY = (dy / distance) * force * 120
      }
    }

    item.offsetX += (attractX - item.offsetX) * 0.05
    item.offsetY += (attractY - item.offsetY) * 0.05
    item.rotation += item.rotSpeed
  })

  rafId = requestAnimationFrame(updatePositions)
}

onMounted(() => {
  initIcons()
  updatePositions()
})

onUnmounted(() => {
  cancelAnimationFrame(rafId)
})
</script>

<template>
  <div class="fixed inset-0 -z-20 overflow-hidden bg-background">
    <!-- Layer 1: Animated Mesh Gradient Blobs -->
    <div class="absolute inset-0">
      <div class="blob blob-1 absolute left-[10%] top-[10%] h-[600px] w-[600px] rounded-full bg-teal-500/15 dark:bg-teal-500/10 blur-[120px]" />
      <div class="blob blob-2 absolute right-[10%] top-[30%] h-[500px] w-[500px] rounded-full bg-cyan-500/15 dark:bg-cyan-500/10 blur-[120px]" />
      <div class="blob blob-3 absolute bottom-[10%] left-[30%] h-[550px] w-[550px] rounded-full bg-teal-600/10 dark:bg-teal-600/5 blur-[120px]" />
    </div>

    <!-- Layer 2: Floating Interactive Icons -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <div 
        v-for="item in floatingItems" 
        :key="item.id"
        class="absolute text-teal-600 dark:text-teal-400/30 will-change-transform"
        :style="{
          left: `${item.baseX}%`,
          top: `${item.y}%`,
          opacity: item.opacity,
          transform: `translate(${item.offsetX}px, ${item.offsetY}px) rotate(${item.rotation}deg)`
        }"
      >
        <component :is="item.icon" :size="item.size" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.blob {
  animation: drift 20s infinite alternate ease-in-out;
}
.blob-2 { animation-delay: -5s; animation-duration: 25s; }
.blob-3 { animation-delay: -10s; animation-duration: 30s; }

@keyframes drift {
  0% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, 50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0, 0) scale(1); }
}
</style>



