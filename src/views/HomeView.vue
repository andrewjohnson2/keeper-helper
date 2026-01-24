<script setup>
import { RouterLink, RouterView, useRouter } from "vue-router";
import { computed, onMounted } from "vue";
import { getAllTeams, setCurrentTeam } from "@/team";
import Page from "@/views/Page.vue";


const router = useRouter();


const allTeams = computed(() => {
  return getAllTeams().sort((t1, t2) => t1.name.toLowerCase() > t2.name.toLowerCase());
})

function loadTeam(team) {
  setCurrentTeam(team);

  router.push({
    name: "team"
  })
}
</script>

<template>
  <Page>
    <div class="sticky top-0">
      <div class="bg-white px-4 pt-2 border-b border-slate-200">
        <div class="flex items-center pb-2">
          <div class="text-2xl">Select Team</div>
        </div>
      </div>
    </div>

    <div class="m-2">
      <div v-for="team in allTeams"
        class="justify-between flex items-center p-2 bg-white rounded-lg my-2 border border-slate-200 center text-xl hover:opacity-50 cursor-pointer"
        @click="loadTeam(team.id)">
        <div class="text-gray-800">
          {{ team.name }}
        </div>
      </div>
    </div>
  </Page>
</template>
