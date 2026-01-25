<script setup>
import { computed, onMounted, reactive } from "vue";
import { getCurrentTeam, getTeamForId } from "@/team";
import { useRoute, useRouter } from "vue-router";
import Player from "./Player.vue";
import Page from "./Page.vue";
import {
  formatRound,
  getPenaltyForDroppingPlayer,
  getPenaltyForDroppingPlayerUnformatted,
} from "@/utils";

const route = useRoute();
const router = useRouter();
const data = reactive({
  team: [],
  teanName: "",
});
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
    .filter((p) => p.selected)
    .map((p) => {
      p.cost = getCostForPlayer(p);
      return p;
    });

  data.costs = [];

  data.team.forEach((p) => {
    let lowerCost = 0;

    data.costs.push({
      id: p.id,
      cost: p.cost,
    });
  });

  data.costs = data.costs.sort((c1, c2) => (c1.cost < c2.cost ? -1 : 1));

  for (let i = 0; i < data.costs.length && i < 5; ++i) {
    data.costs[i].cost = "Free";
  }

  data.droppedPlayers = team?.players.filter((p) => p.isCuttingPlayer);
});

const majorLeaguers = computed(() => {
  return data.team
    .filter((p) => !p.isMinorLeagueEligible)
    .sort((a, b) =>
      parseInt(a.contractDetails.rank) < parseInt(b.contractDetails.rank)
        ? -1
        : 1
    );
});

const minorLeaguers = computed(() => {
  return data.team.filter((p) => p.isMinorLeagueEligible);
});

const releasedPlayers = computed(() => {
  return data.droppedPlayers || [];
});

function penalty(player) {
  return getPenaltyForDroppingPlayer(player);
}

function getCostForPlayer(p) {
  if (p.contractDetails && p.contract !== "1st" && p.contract !== "2025") {
    return parseInt(p.contractDetails.draftPick) - 1;
  } else if (p.draftPick) {
    return parseInt(p.draftPick.round) - 1;
  } else {
    console.log("cannot find cost");
  }
}

function _formatRound(round) {
  return formatRound(round);
}

// function getCostForPlayer(p) {
//   let picks = [];
//   let freePlayers = [];
//   data.team.forEach((p) => {
//     if (freePlayers.length < 5) {
//       freePlayers.push(p);
//       return;
//     }

//     let cost = getCostForPlayer(p);

//     let freePlayerToGetRidOf = undefined;
//     for (let i = 0; i < freePlayers.length; ++i) {
//       let freePlayerCost = getCostForPlayer(freePlayers[i]);
//       if (freePlayerCost > cost) {
//         if (
//           !freePlayerToGetRidOf ||
//           getCostForPlayer(freePlayerToGetRidOf) < freePlayerCost
//         ) {
//           freePlayerToGetRidOf = freePlayers[i];
//         }
//       }
//     }

//     if (freePlayerToGetRidOf) {
//       picks.push({
//         pick: getCostForPlayer(freePlayerToGetRidOf),
//         reason: "Keeping " + freePlayerToGetRidOf.name,
//       });

//       freePlayers = freePlayers.filter((p) => p.id !== freePlayerToGetRidOf.id);
//       freePlayers.push(p);
//     } else {
//       picks.push({
//         pick: cost,
//         reason: "Keeping " + p.name,
//       });
//     }
//   });

//   data.droppedPlayers?.forEach((dp) => {
//     picks.push({
//       pick: getPenaltyForDroppingPlayerUnformatted(dp),
//       reason: "Dropping " + dp.name,
//     });
//   });

//   picks = picks.sort((p1, p2) => (p1.pick < p2.pick ? -1 : 1));

//   while (areAnyPicksDuplicates(picks)) {
//     for (let i = 0; i < picks.length - 1; ++i) {
//       if (picks[i + 1].pick === picks[i].pick) {
//         picks[i].pick -= 1;
//       }
//     }
//   }

//   picks = picks.sort((p1, p2) => (p1.pick < p2.pick ? -1 : 1));

//   return picks;
// });

function areAnyPicksDuplicates(picks) {
  for (let i = 0; i < picks.length; ++i) {
    for (let j = i + 1; j < picks.length; ++j) {
      if (picks[i].pick === picks[j].pick) {
        return true;
      }
    }
  }
  return false;
}
</script>
<template>
  <Page>
    <div class="sticky top-0">
      <div class="bg-white px-4 pt-2 border-b border-slate-200 pb-2">
        <div class="text-2xl">{{ data.teamName }} 2026 Keepers</div>
      </div>
    </div>

    <div class="rounded-lg px-1">
      <div class="m-2">Major League Keepers</div>
      <div v-for="(player, index) in majorLeaguers">
        <div
          :class="
            'mx-2 gap-2 items-center justify-between flex flex-nowrap truncate bg-white my-2 py-2 px-3 rounded-lg ' +
            (state === 'EXPIRED' ? 'opacity-50' : '')
          "
        >
          <div class="truncate">
            <div class="flex gap-2 items-center truncate text-ellipsis">
              <template v-if="player.contractDetails.rank">
                {{ player.contractDetails.rank }}.
              </template>
              {{ player.name }}
            </div>
          </div>
          <div class="">
            <div class="text-right">
              <div>
                {{
                  player.isMinorLeagueEligible
                    ? ""
                    : "Cost: " +
                      formatRound(
                        data.costs.find((c) => c.id === player.id)?.cost
                      )
                }}
              </div>
              <div>
                {{
                  player.isMinorLeagueEligible
                    ? "N/A"
                    : "Signed Through: " + player.contract
                }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <template v-if="minorLeaguers.length > 0">
        <div class="m-2">Minor League Keepers</div>
        <div v-for="player in minorLeaguers">
          <div
            :class="
              'mx-2 gap-2 items-center justify-between flex flex-nowrap truncate bg-white my-2 py-2 px-3 rounded-lg ' +
              (state === 'EXPIRED' ? 'opacity-50' : '')
            "
          >
            <div class="truncate">
              <div class="flex gap-2 items-center truncate text-ellipsis">
                <template v-if="player.contractDetails.rank">
                  {{ player.contractDetails.rank }}.
                </template>
                {{ player.name }}
              </div>
            </div>
            <div class="">
              <div class="text-right">
                <div>
                  {{
                    player.isMinorLeagueEligible
                      ? "N/A"
                      : "Through: " + player.contract
                  }}
                </div>
                <div>
                  {{
                    player.isMinorLeagueEligible
                      ? ""
                      : "Cost: " +
                        formatRound(
                          data.costs.find((c) => c.id === player.id)?.cost
                        )
                  }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template v-if="releasedPlayers.length > 0">
        <div class="m-2">Released Players</div>
        <div v-for="player in releasedPlayers">
          <div
            :class="
              'mx-2 gap-2 items-center justify-between flex flex-nowrap truncate bg-white my-2 py-2 px-3 rounded-lg ' +
              (state === 'EXPIRED' ? 'opacity-50' : '')
            "
          >
            <div class="truncate">
              <div class="flex gap-2 items-center truncate text-ellipsis">
                {{ player.name }}
              </div>
            </div>
            <div class="">
              <div class="text-right">
                <div>Cost: {{ penalty(player) }}</div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </Page>
</template>
