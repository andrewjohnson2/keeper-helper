<script setup>
import { getPenaltyForDroppingPlayer } from '@/utils';
import { defineProps } from 'vue';

const props = defineProps(["player", "state", "border", "isSelecting"]);

function selectPlayer(p1) {
  if (props.state === 'PENDING') {
    p1.selected = !p1.selected;
  }
  console.log(props.state, props.isSelecting)
  if (props.isSelecting &&
       (props.state === 'CONTRACT' || props.state === 'DROPPED') && 
      !props.player.wasDropped) {

    p1.isCuttingPlayer = !p1.isCuttingPlayer;
    if (p1.isCuttingPlayer) {
      p1.selected = false;
    } else {
      p1.selected = true;
    }
  }
}

function penalty() {
  return getPenaltyForDroppingPlayer(props.player);
}
</script>

<template>
  <div @click="selectPlayer(player)" style="z-index: 9;"
  :class="'mx-2 gap-2 items-center justify-between flex flex-nowrap truncate bg-white ' +

(border ? 'rounded-lg m-2 py-1 px-3 ' : 'py-1 ') +
  (state === 'PENDING' ? 'cursor-pointer hover:opacity-70 ' : '') +
    (player.selected ? 'border border-slate-400 bg-slate-200 ' : ' border border-white ') +
    (state === 'EXPIRED' ? 'opacity-50 ' : '') + 
    (state === 'DROPPED' ? 'opacity-50 bg-red-300 ' : '')">
    <div class="truncate">
      <div class="text-xs text-gray-400 flex items-center gap-x-1 truncate pt-1">
        {{ player.team }} ({{ player.position }})
      </div>
      <div class="flex gap-2 items-center text-lg truncate text-ellipsis">
        {{ player.name }} <span v-if="state === 'DROPPED' && !player.isMinorLeagueEligible">(Forfeit {{ penalty() }} pick)</span>
      </div>
    </div>
    <div class="">
      <slot></slot>
    </div>
  </div>
</template>
