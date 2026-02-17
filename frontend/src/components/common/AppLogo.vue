<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import gsap from 'gsap'

const props = defineProps<{
  size?: 'sm' | 'md' | 'lg'
  showText?: boolean
}>()

const textRef = ref<HTMLElement | null>(null)
const dotRef = ref<HTMLElement | null>(null)
const containerRef = ref<HTMLElement | null>(null)

const sizeMap = {
  sm: { text: 'text-2xl', dot: 'h-0.5 w-0.5', height: 'h-8' },
  md: { text: 'text-3xl', dot: 'h-[3px] w-[3px]', height: 'h-10' },
  lg: { text: 'text-5xl', dot: 'h-1 w-1', height: 'h-16' }
}

const currentSize = computed(() => sizeMap[props.size || 'md'])

const animateLogo = (isHover = false) => {
  if (!textRef.value || !dotRef.value) return

  const tl = gsap.timeline({ defaults: { ease: "none" } })
  const duration = isHover ? 2.2 : 3.5

  gsap.set(textRef.value, { 
    clipPath: 'inset(0 100% 0 0)'
  })
  gsap.set(dotRef.value, { left: "0%", yPercent: -50, opacity: 0, y: 0 })

  tl.to(dotRef.value, { opacity: 1, duration: 0.3 })

  tl.to(dotRef.value, {
    left: "100%",
    duration: duration,
    ease: "power1.inOut",
    onUpdate: function() {
      const progress = parseFloat(dotRef.value?.style.left || "0")
      if (textRef.value) {
        textRef.value.style.clipPath = `inset(0 ${100 - progress}% 0 0)`
      }
    }
  }, 0.3)

  tl.to(dotRef.value, {
    keyframes: [
      { y: -6, duration: 0.4 }, { y: 6, duration: 0.4 },   // M
      { y: -4, duration: 0.4 }, { y: 4, duration: 0.4 },   // M
      { y: 0, duration: 0.3 },                            // e
      { y: -10, duration: 0.4 }, { y: 6, duration: 0.4 },  // d
      { y: 2, duration: 0.3 },                            // i
      { y: -12, duration: 0.4 }, { y: 2, duration: 0.4 },  // b
      { y: -14, duration: 0.4 }, { y: 6, duration: 0.4 },  // l
      { y: 0, duration: 0.3 }                             // e
    ],
    duration: duration,
    ease: "sine.inOut"
  }, 0.3)

  tl.to(dotRef.value, { opacity: 0, duration: 0.4 })
}

onMounted(() => {
  setTimeout(animateLogo, 500)
})
</script>

<template>
  <div 
    ref="containerRef"
    class="relative flex items-center group cursor-pointer" 
    :class="currentSize.height"
    @mouseenter="animateLogo(true)"
  >
    <div class="relative flex items-center">
      <span 
        ref="textRef"
        class="logo-text inline-block font-['Dancing_Script'] font-bold bg-gradient-to-r from-teal-500 to-cyan-500 bg-clip-text text-transparent select-none whitespace-nowrap"
        :class="currentSize.text"
      >
        Medible
      </span>

      <div 
        ref="dotRef"
        class="pen-dot absolute top-1/2 rounded-full bg-teal-400 shadow-[0_0_4px_rgba(45,212,191,1)] dark:bg-teal-300"
        :class="currentSize.dot"
      />
    </div>
  </div>
</template>

<style scoped>
.logo-text {
  position: relative;
  will-change: mask-image, -webkit-mask-image;
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  -webkit-mask-repeat: no-repeat;
  mask-repeat: no-repeat;
}

.pen-dot {
  pointer-events: none;
  z-index: 30;
}
</style>
