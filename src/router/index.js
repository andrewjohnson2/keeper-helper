import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/team',
      name: 'team',
      component: () => import('../views/Team.vue')
    },
    {
      path: "/ranking",
      name: "ranking",
      component: () => import('../views/Ranking.vue')
    },
    {
      path: "/done",
      name: "done",
      component: () => import('../views/PublishView.vue')
    },
    {
      path: "/timeline",
      name: "timeline",
      component: () => import("../views/Timeline.vue")
    }
  ]
})

export default router
