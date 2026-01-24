<script setup>
import { computed, onMounted } from 'vue';
import { getCurrentTeam, init, setCurrentTeam } from '@/team';

onMounted(() => {
    init();
    setCurrentTeam(0);
})

const players = computed(() => {
    return (getCurrentTeam()?.players || []).filter(p => p.selected);
})

const YEARS = [2026, 2027, 2028]
</script>
<template>
    <div v-for="player in players" class="flex grow justify-between">
        <div>{{ player.name }}</div>
        <div v-for="year in YEARS" :style="{
        backgroundColor: parseInt(player.contract) >= year ? 'blue' : '',
        opacity: 1 - (1 / ((parseInt(player.contract) - year) + 2)),
        width: '25%'
    }" :class="'basis-1/4'">
            {{ year }}

        </div>
    </div>

</template>