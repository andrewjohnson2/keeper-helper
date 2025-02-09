<script setup>
import { defineProps } from 'vue';

const props = defineProps(["player", "state", "border", "isSelecting"]);

function selectPlayer(p1) {
  if (props.state === 'PENDING') {
    p1.selected = !p1.selected;
  }
}
</script>

<template>
  <div @click="selectPlayer(player)" style="z-index: 9;"
  :class="'mx-2 gap-2 items-center justify-between flex flex-nowrap truncate ' +

  (border ? 'border-2 rounded-lg m-2 py-1 px-3 ' : 'py-1 ') +
  (state === 'PENDING' ? 'cursor-pointer ' : '') +
    (player.selected ? 'border-slate-400 bg-slate-200 ' : ' ') +
    (state === 'EXPIRED' ? 'opacity-50' : 'hover:opacity-90')">
    <div class="truncate">
      <div class="text-s text-gray-400 flex items-center gap-x-1 truncate">
        {{ player.team }} ({{ player.position }})
        <svg v-if="state === 'CONTRACT' && isSelecting" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
  <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
</svg>
      </div>
      <div class="flex gap-2 items-center text-2xl truncate text-ellipsis">
        {{ player.name }}
      </div>
    </div>
    <div class="">
      <slot></slot>
    </div>
  </div>
</template>
