<script setup>
import { getCurrentTeam } from "@/team";
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import Player from "@/views/Player.vue";
import Page from "./Page.vue";

const route = useRoute();
const router = useRouter();

const isSelecting = ref(true);

onMounted(() => {
  const team = getCurrentTeam();
  if (team === undefined) {
    router.push({
      name: "home",
    });
    return;
  }
})

function getCostForPlayer(player) {
  if (player === undefined) {
    return "";
  }

  console.log(player);
  if (player.contractDetails?.isMinorLeagueKeeper) {
    return "Free";
  }

  let cost;
  if (player.contractDetails && player.contract !== '1st' && player.contract !== YEAR) {
    player.selected = true;

    cost = parseInt(player.contractDetails.draftPick) - 1;
  } else if (player.draftPick) {
    cost = parseInt(player.draftPick.round) - 1;
  }

  let costAsString;
  if (cost === 1) {
    costAsString = "1st Round";
  } else if (cost === 2) {
    costAsString = "2nd Round";
  } else if (cost <= 0) {
    costAsString = "N/A";
  } else {
    costAsString = cost + "th Round";
  }

  player.costAsString = costAsString;
  return costAsString;
}

const team = computed(() => {
  return getCurrentTeam()?.players || [];
})

const teamName = computed(() => {
  return getCurrentTeam()?.name;
})

const keptPlayers = computed(() => {
  return team.value.filter(p => p.selected)
    .filter(p => !p.isMinorLeagueEligible)
    .length;
})

const hitters = computed(() => {
  return team.value.filter(p => p.selected)
    .filter(p => !["SP", "RP", "P"].includes(p.position))
    .filter(p => !p.isMinorLeagueEligible)
    .length;
})

const pitchers = computed(() => {
  return team.value.filter(p => p.selected)
    .filter(p => ["SP", "RP", "P"].includes(p.position))
    .filter(p => !p.isMinorLeagueEligible)
    .length;
})

const minorLeagues = computed(() => {
  return team.value.filter(p => p.selected)
    .filter(p => p.isMinorLeagueEligible)
    .length;
})

const tooManyPlayers = computed(() => {
  return keptPlayers.value > 10 || hitters.value > 7 || pitchers.value > 7;
});

function back() {
  if (isSelecting.value) {
    router.push({
      name: "home"
    });
  } else {
    team.value
      .forEach(p => {
        if (p.isNewSelection) {
          p.contractDetails = undefined;
          p.contract = "1st";
          p.isNewSelection = undefined;
        }
      })

    isSelecting.value = true;
  }

}

function next() {
  if (isSelecting.value) {
    if (tooManyPlayers.value) {
      return;
    }


    team.value
      .forEach(p => {
        if (p.selected && p.contract === "1st") {
          p.contractDetails = {
            rank: undefined,
            draftPick: p.draftPick.round
          };
          p.contract = "2026";
          p.isNewSelection = true;
        }
      })

    // router.push({
    //   name: "timeline",
    //   params: { team: parseInt(route.params.team) },
    // });

    isSelecting.value = false;

  } else {

    router.push({
      name: "ranking"
    });

  }
}


const YEAR = "2025";
</script>

<template>
  <Page>
    <div class="flex items-center pb-2 bg-white px-4 pt-2">
      <div class="text-2xl">{{ isSelecting ? 'Select Keepers' : 'Assign Contracts' }}</div>
    </div>

    <div class="bg-white sticky top-0 px-4 border-b border-slate-200">
      <div class="sticky top-0 flex flex-nowrap justify-between bg-white py-2 border-slate-200 border-t"
        v-if="isSelecting">
        <div :class="keptPlayers > 10 ? 'text-red-500' : ''">
          <div class="text-xs text-slate-500">
            Players
          </div>
          {{ keptPlayers }}
        </div>

        <div :class="hitters > 7 ? 'text-red-600' : ''">
          <div class="text-xs text-slate-500">
            Hitters
          </div>
          {{ hitters }}
        </div>

        <div :class="pitchers > 7 ? 'text-red-600' : ''">
          <div class="text-xs text-slate-500">
            Pitchers
          </div>
          {{ pitchers }}
        </div>

        <div :class="minorLeagues > 2 ? 'text-red-600' : ''">
          <div class="text-xs text-slate-500">
            Minor Leaguers
          </div>
          {{ minorLeagues }}
        </div>
      </div>
    </div>


    <TransitionGroup name="list">
      <!-- <div class="mx-3">Pending Extension</div> -->
      <Player :border="true" style="z-index: 9;"
        v-for="player in team.filter((p) => (p.selected && p.isNewSelection) || (p.contract === '1st' && isSelecting))
                            .filter(p => !p.isCuttingPlayer)"
        :key="player.id" :state="isSelecting ? 'PENDING' : 'CONTRACT'" :is-selecting=isSelecting :player="player">
        <div class="flex items-center">
          <div class="py-1" v-if="!isSelecting">
            <div v-if="player.isMinorLeagueEligible">
              Minor Leaguer (Indefinitely)
            </div>
            <template v-else>
              <div class="flex items-center mb-1">
                <input checked :id="'default-radio-1-' + player.id" type="radio" value="2026" :name="player.id"
                  v-model="player.contract"
                  class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                <label :for="'default-radio-1-' + player.id"
                  class="ms-2 text-sm font-medium text-gray-900 dark:text-gray-300">2026</label>
              </div>
              <div class="flex items-center">
                <input :id="'default-radio-2-' + player.id" type="radio" value="2028" :name="player.id"
                  v-model="player.contract"
                  class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                <label :for="'default-radio-2-' + player.id"
                  class="ms-2 text-sm font-medium text-gray-900 dark:text-gray-300">2028</label>
              </div>
            </template>

          </div>
          <div class="ml-2" v-if="isSelecting">
            {{ player.isMinorLeagueEligible ? 'Minor League (No Cost)' : getCostForPlayer(player) }}
          </div>
        </div>
      </Player>

      <!-- <div class="mx-3">Players Under Contract</div> -->
      <Player v-for="player in team.filter((p) => p.contract !== '1st' && p.contract !== YEAR && !p.isNewSelection)
                                    .filter(p => !p.isCuttingPlayer)"
        :key="player.id" :player="player" state="CONTRACT" :border="true" :is-selecting=isSelecting>
        <div>
          {{ player.contract }}

          <template v-if="isSelecting">
            ({{ getCostForPlayer(player) }})
          </template>
        </div>
      </Player>

      <Player state="DROPPED"
      v-for="player in team.filter(p => p.isCuttingPlayer)"
      :player="player" :border="true" :is-selecting="isSelecting">
          <div>
            {{ player.wasDropped ? 'Dropped' : 'Released' }}
          </div>
      </Player>

      <!-- <div class="mx-3">Expired Contracts</div> -->
      <Player v-for="player in team.filter((p) => p.contract === YEAR)
                                    .filter(p => isSelecting)
                                    .filter(p => !p.isCuttingPlayer)" :key="player.id"
        :player="player" state="EXPIRED" :border="true">
        <div>
          Expired
        </div>
      </Player>
    </TransitionGroup>
    <!-- <div style="z-index: 10;">

      <div class="fixed gap-x-2 z-100" v-if="isSelecting" style="right: 5px; top: 8px;">
        <div class="">
          <div
            :class="(keptPlayers > 10 ? 'bg-red-400' : 'bg-slate-200') + ' text-sm border border-slate-400 rounded-lg mt-1 mb-2 py-1 px-3'">
            {{ keptPlayers }} Players
          </div>

          <div
            :class="(hitters > 7 ? 'bg-red-400' : 'bg-slate-200') + ' text-sm border border-slate-400 rounded-lg my-2 py-1 px-3'">
            {{ hitters }} Hitters
          </div>

          <div
            :class="(pitchers > 7 ? 'bg-red-400' : 'bg-slate-200') + ' text-sm border border-slate-400 rounded-lg my-2 py-1 px-3'">
            {{ pitchers }} Pitchers
          </div>

          <div
            :class="(pitchers > 7 ? 'bg-red-400' : 'bg-slate-200') + ' text-sm border border-slate-400 rounded-lg my-2 py-1 px-3'">
            {{ minorLeagues }} Minors
          </div>
        </div>
      </div>
    </div> -->

    <div class="fixed bottom-4 w-full">
      <div class="flex justify-center flex-wrap items-center mx-4">

        <div>
          <div class="flex gap-3 justify-center place-self-center">
            <button @click="back" :class="'text-black text-lg bg-white rounded-full py-2 px-8 shadow-lg'">Back</button>
            <button @click="next" :class="'text-black text-lg bg-blue-200 rounded-full py-2 px-8 shadow-lg ' +
              (tooManyPlayers ? 'opacity-50' : 'cursor-pointer')">Next</button>
          </div>
        </div>

      </div>

    </div>
  </Page>
</template>

<style>
.list-move,
/* apply transition to moving elements */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  /* transform: translateX(30px); */
}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
.list-leave-active {
  position: absolute;
}
</style>
