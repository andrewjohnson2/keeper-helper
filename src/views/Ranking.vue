<script setup>
import { onMounted, reactive } from "vue";
import { getCurrentTeam, getTeamForId } from "@/team";
import { useRoute, useRouter } from "vue-router";
import Page from "./Page.vue";

const router = useRouter();
const route = useRoute();

const data = reactive({
  team: [],

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
    { id: crypto.randomUUID(), placeholder: true }
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

  data.team = getCurrentTeam()?.players
    .filter(p => p.selected)

  const unrankedPlayers = [];
  data.team.forEach(p => {
    if (p.isMinorLeagueEligible) {
      data.minorLeaguers.push(p);
      return;
    }

    if (p.contractDetails.rank === undefined) {
      unrankedPlayers.push(p);
    } else {
      data.ranking[p.contractDetails.rank - 1] = p;
    }
  });

  unrankedPlayers.forEach(urp => {

    for (let i = 0; i < data.ranking.length; ++i) {
      if (data.ranking[i].placeholder) {
        console.log("adding unranked player", i)
        urp.contractDetails.rank = i + 1;
        data.ranking[i] = urp;
        return;
      }
    }
    console.log("cannot find spot for unranked player")
  })





});

function dragStart(index) {
  data.index = String(index);
  setTimeout(() => (data.index = parseInt(index)), 10);
}

function dragOver(e) {
  e.preventDefault();
  const newIndex = e.target.id;

  if (String(newIndex) === String(data.index) ||
    newIndex === ""
  ) {
    return;
  } else {
    console.log("continuing", newIndex, data.index);
  }

  if (!draggable(newIndex)) {
    return;
  }

  if (hasMovedRecently(data.ranking[data.index].id) && hasMovedRecently(data.ranking[newIndex].id)) {
    console.log("old index has moved too recently")
    return;
  }

  const copy = Object.assign({}, data.ranking[data.index]);
  data.ranking[data.index] = data.ranking[parseInt(newIndex)];
  data.ranking[newIndex] = copy;

  data.moving[data.ranking[data.index].id] = new Date();
  data.moving[data.ranking[newIndex].id] = new Date();

  data.index = parseInt(newIndex);

  console.log(data.ranking);
}

function hasMovedRecently(id) {
  if (id in data.moving) {
    const movedDate = data.moving[id];
    return (new Date().getTime() - movedDate.getTime()) < 500;
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
  })

  router.push({
    name: "done"
  })
}

function draggable(index) {
  return data.ranking[index]?.isNewSelection || data.ranking[index].placeholder;
}
</script>

<template>
  <Page>
    <div class="flex justify-center items-center m-1">
      <div class="text-2xl">
        Player Ranking
      </div>
    </div>

    <div class="flex justify-center items-center m-2">
      <div class="text-xs">Rank your players 1-10. Players retain their ranking throughout the lifetime of their
        contract.
      </div>
    </div>

    <div class="p-2" v-if="data.minorLeaguers.length > 0">Major Leaguers</div>
    <div class="bg-slate-200 border rounded-lg px-2">
      <TransitionGroup name="list" tag="div">

        <div v-for="(player, index) in data.ranking" v-bind:key="player.id"
          :class="'border-slate-400 ' + (index !== 0 && index !== data.index && index !== data.index + 1 ? 'border-t ' : '')">

          <div :id="index" :ondragstart="(e) => dragStart(index)" :ondragover="(e) => dragOver(e)"
            :ondragenter="(e) => dragOver(e)" :draggable="draggable(index)" :ondrop="(e) => drop(e)"
            :ondragend="(e) => drop(e)" :class="'py-3 mx-2 flex justify-between items-center ' +
              (!draggable(index) ? 'opacity-30 rounded-lg ' : '') +
              (index === data.index ? 'opacity-0' : '')
              ">
            <div>
              <div class="text-xl">
                {{ player.name || 'Open Slot' }}
              </div>
              <div class="text-xs text-gray-400">
                {{ player.contract }}
              </div>
            </div>
            <div>
              {{ index + 1 }}
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <div class="p-2 mt-4" v-if="data.minorLeaguers.length > 0">Minor Leaguers</div>
    <div v-if="data.minorLeaguers.length > 0" class="bg-slate-200 border rounded-lg px-2 mb-3">
      <div v-for="p in data.minorLeaguers" class="py-3 mx-2">
        {{ p.name }}
      </div>
    </div>

    <Transition name="button">
      <div class="fixed bottom-8 w-full transition" v-if="data.index === undefined">
        <div class="flex gap-2 justify-center">
          <button @click="done" :class="'text-black text-lg bg-blue-200 rounded-full py-2 px-5 shadow-md'">Done</button>
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


/* .list-leave-active {
  position: absolute;
} */
</style>
