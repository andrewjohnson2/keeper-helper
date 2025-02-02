<script setup>
import { onMounted, reactive } from 'vue';
import { getCurrentTeam, getTeamForId } from "@/team";
import { useRoute, useRouter } from "vue-router";
import Player from './Player.vue';
import Page from './Page.vue';

const route = useRoute();
const router = useRouter();
const data = reactive({
    team: [],
    teanName: ""
})
onMounted(async () => {
    const team = getCurrentTeam();
    if (team === undefined) {
        router.push({
            name: "home",
        });
        return;
    }

    data.teamName = team.name;
    data.team = team?.players
        .filter(p => p.selected)
    // .map(p => {
    //     p.rank = ids.find(i => i.id === p.id)?.rank;
    //     p.contract = ids.find(i => i.id === p.id)?.contract;
    //     return p;
    // })



    data.team.sort((a, b) => a.contractDetails.rank < b.contractDetails.rank ? -1 : 1)
})
</script>
<template>
    <Page>

        <div class="flex justify-center text-2xl m-3">
            {{ data.teamName }} Keepers
        </div>

        <div class="bg-slate-200 border rounded-lg px-2">
            <div v-for="(player, index) in data.team" :class="index !== 0 ? 'border-t border-slate-400 ' : ''">

                <Player  :player="player" :border="false">
                    <div class="text-right">

                        <div>
                            {{ player.contractDetails.rank }}
                        </div>
                        <div>
                            {{ player.contract }}
                        </div>
                    </div>

                </Player>
            </div>
        </div>
    </Page>

</template>