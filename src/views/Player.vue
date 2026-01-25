<script setup>
import { getPenaltyForDroppingPlayer } from "@/utils";
import { defineProps } from "vue";

const props = defineProps(["player", "state", "border", "isSelecting"]);

function selectPlayer(p1) {
  if (props.state === "PENDING") {
    p1.selected = !p1.selected;
  }
}

function penalty() {
  return getPenaltyForDroppingPlayer(props.player);
}
</script>

<template>
  <div
    :class="
      'mx-2 bg-white ' +
      (border ? 'rounded-lg m-2 py-1 px-3 ' : 'py-1 ') +
      (state === 'PENDING' ? 'cursor-pointer hover:opacity-70 ' : '') +
      (player.selected
        ? 'border border-slate-400 bg-slate-200 '
        : ' border border-white ') +
      (state === 'EXPIRED' ? 'opacity-50 ' : '') +
      (state === 'DROPPED' && (player.wasDropped || !isSelecting) ? 'opacity-50 bg-red-300 ' : '')
    "
  >
    <div
      @click="selectPlayer(player)"
      style="z-index: 9"
      :class="'flex flex-nowrap truncate  gap-2 items-center justify-between'"
    >
      <div class="truncate">
        <div
          class="text-xs text-gray-400 flex items-center gap-x-1 truncate pt-1"
        >
          {{ player.team }} ({{ player.position }})
        </div>
        <div class="flex gap-2 items-center text-lg truncate text-ellipsis">
          {{ player.name }}
        </div>
      </div>
      <div class="">
        <slot></slot>
      </div>
    </div>
    <slot name="bottom"></slot>
  </div>
</template>
