<script setup>
import { onMounted, reactive } from "vue";
import { getCurrentTeam, getTeamForId } from "@/team";
import { useRoute, useRouter } from "vue-router";
import Page from "./Page.vue";

const router = useRouter();
const route = useRoute();

const data = reactive({
  team: [],
  showInfo: false,

  ranking: [
    { id: crypto.randomUUID(), placeholder: true },
    { id: crypto.randomUUID(), placeholder: true },
    { id: crypto.randomUUID(), placeholder: true },
    { id: crypto.randomUUID(), placeholder: true },
    { id: crypto.randomUUID(), placeholder: true },
    { id: crypto.randomUUID(), placeholder: true },
    { id: crypto.randomUUID(), placeholder: true },
    { id: crypto.randomUUID(), placeholder: true },
    { id: crypto.randomUUID(), placeholder: true },
    { id: crypto.randomUUID(), placeholder: true },
  ],
  moving: [],
  minorLeaguers: [],

  index: undefined,
});

onMounted(async () => {
  const team = getCurrentTeam();
  if (team === undefined) {
    router.push({
      name: "home",
    });
    return;
  }

  data.team = getCurrentTeam()?.players.filter((p) => p.selected);

  const unrankedPlayers = [];
  const duplicateRank = [];
  data.team.forEach((p) => {
    if (p.isMinorLeagueEligible) {
      data.minorLeaguers.push(p);
      return;
    }

    if (p.contractDetails.rank === undefined) {
      unrankedPlayers.push(p);
    } else {
      if (data.ranking[p.contractDetails.rank - 1].placeholder) {
        data.ranking[p.contractDetails.rank - 1] = p;
      } else {
        duplicateRank.push(p);
      }
    }
  });


  duplicateRank.forEach((dp) => {
    let i = dp.contractDetails.rank - 1;

    let foundSpot = false;
    while (!foundSpot) {
      if (i >= 0 && data.ranking[i].placeholder) {
        data.ranking[i] = dp;
        foundSpot = true;
      }
      i -= 1;

      if (i < 0) {
        console.error("cannot find spot for duplicate player");
        break;
      }
    }

    let j = dp.contractDetails.rank + 1;
    while (!foundSpot) {
      if (j < data.ranking.length && data.ranking[i].placeholder) {
        data.ranking[j] = dp;
        data.ranking[j].overrideRank = dp.contractDetails.rank
        break;
      }
      j += 1;

      if (j >= data.ranking.length) {
        console.error("cannot find spot for duplicate player");
        break;
      }
    }


  })

  unrankedPlayers.forEach((urp) => {
    for (let i = 0; i < data.ranking.length; ++i) {
      if (data.ranking[i].placeholder) {
        console.log("adding unranked player", i);
        urp.contractDetails.rank = i + 1;
        data.ranking[i] = urp;
        return;
      }
    }
    console.log("cannot find spot for unranked player");
  });
});

function dragStart(index) {
  data.index = String(index);
  setTimeout(() => (data.index = parseInt(index)), 10);
}

function dragOver(e) {
  e.preventDefault();
  const newIndex = e.target.id;

  if (String(newIndex) === String(data.index) || newIndex === "") {
    return;
  } else {
    console.log("continuing", newIndex, data.index);
  }

  if (!draggable(newIndex)) {
    console.log("not draggable", newIndex);
    return;
  }

  if (
    hasMovedRecently(data.ranking[data.index].id) &&
    hasMovedRecently(data.ranking[newIndex].id)
  ) {
    console.log("old index has moved too recently");
    return;
  }

  console.log(newIndex, data.index);

  const copy = Object.assign({}, data.ranking[data.index]);
  data.ranking[data.index] = data.ranking[parseInt(newIndex)];
  data.ranking[newIndex] = copy;

  data.moving[data.ranking[data.index].id] = new Date();
  data.moving[data.ranking[newIndex].id] = new Date();

  data.index = parseInt(newIndex);

  // setTimeout(() => {
  //   data.index = parseInt(newIndex);
  // }, 200)

  console.log(data.ranking);
}

function hasMovedRecently(id) {
  if (id in data.moving) {
    const movedDate = data.moving[id];
    return new Date().getTime() - movedDate.getTime() < 500;
  }
  return false;
}

function drop(e) {
  e.preventDefault();

  data.index = undefined;
}

function done() {
  data.ranking.forEach((r, i) => {
    if (r.contractDetails) {
      r.contractDetails.rank = i + 1;
    }
  });

  router.push({
    name: "done",
  });
}

function draggable(index) {
  return data.ranking[index]?.isNewSelection || data.ranking[index].placeholder;
}
</script>

<template>
  <Page>
    <div class="sticky top-0">
      <div class="bg-white px-4 pt-2 border-b border-slate-200 pb-2">
        <div class="flex justify-between items-center">
          <div>
            <div class="text-2xl">Rank Players</div>
            <div class="text-gray-700 text-xs">
              Players retain their ranking throughout the lifetime of their
              contract.
            </div>
          </div>
          <div class="cursor-pointer" @click="data.showInfo = !data.showInfo">
            ⓘ
          </div>
        </div>
        <div v-if="data.showInfo" class="mt-3 text-sm text-gray-500">

          <div>
            Keepers are ranked 1-10. If a keeper is dropped during their contract, a draft pick penalty is assessed based on their ranking.
          </div>
          <div>
            Rank 1-2: 3rd round
          </div>
          <div>
            Rank 3-4: 5th round
          </div>
          <div>
            Rank 5-6: 7th round
          </div>
          <div>
            Rank 7-10: 10th round
          </div>

          <div class="mt-2">Each year remaining on their contract increases the round by 1</div>
        </div>
      </div>
    </div>

    <div class="px-2 pt-2" v-if="data.minorLeaguers.length > 0">
      Major League Keepers
    </div>
    <div class="mx-2 pt-1">
      <TransitionGroup name="list" tag="div">
        <div
          v-for="(player, index) in data.ranking"
          v-bind:key="player.id"
          :class="'py-1 ' + (index === data.index ? 'opacity-0' : '')"
          :id="index"
          :ondragstart="(e) => dragStart(index)"
          :ondragover="(e) => dragOver(e)"
          :ondragenter="(e) => dragOver(e)"
          :draggable="draggable(index)"
          :ondrop="(e) => drop(e)"
          :ondragend="(e) => drop(e)"
        >
          <div
            :class="
              'px-2 py-1 flex justify-between bg-white rounded-lg items-center ' +
              (!draggable(index) ? 'opacity-30 rounded-lg ' : '')
            "
          >
            <div>
              <div class="">
                {{ player.name || "Open Slot" }}
              </div>
              <div class="text-xs text-gray-400">
                {{ player.contract }}
              </div>
            </div>
            <div>
              {{ player.overrideRank ? player.overrideRank : index + 1 }}
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <div class="p-2 mt-3" v-if="data.minorLeaguers.length > 0">
      Minor League Keepers
    </div>
    <div v-if="data.minorLeaguers.length > 0" class="px-2 mb-3">
      <div
        v-for="p in data.minorLeaguers"
        class="px-3 py-1 bg-white rounded-lg"
      >
        {{ p.name }}
      </div>
    </div>

    <Transition name="button">
      <div
        class="fixed bottom-8 w-full transition"
        v-if="data.index === undefined"
      >
        <div class="flex gap-2 justify-center">
          <button
            @click="done"
            :class="'text-black text-lg bg-blue-200 rounded-full py-2 px-5 shadow-md'"
          >
            Done
          </button>
        </div>
      </div>
    </Transition>
  </Page>
</template>

<style>
.button-enter-from,
.button-leave-to {
  opacity: 0;
}

.list-move {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
}
</style>
