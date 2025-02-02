<script setup>
import { RouterLink, RouterView, useRouter } from "vue-router";
import { computed, onMounted } from "vue";
import { getAllTeams, setCurrentTeam } from "@/team";
import Page from "@/views/Page.vue";


const router = useRouter();


const allTeams = computed(() => {
  return getAllTeams();
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
    <div class="flex justify-center my-3">
      <div class="text-2xl">Select Team</div>
    </div>
    <div class="divide-y bg-white rounded-lg px-3">
      <div v-for="team in allTeams"
        class="justify-between flex items-center py-3 center text-2xl hover:opacity-50 cursor-pointer"
        @click="loadTeam(team.id)">
        <div>
          {{ team.name }}
        </div>
        <div class="text-sm">
          >
        </div>
      </div>
    </div>
  </Page>
</template>
