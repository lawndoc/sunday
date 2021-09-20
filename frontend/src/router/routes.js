const routes = [
    {
      path: '/',
      component: () => import('layouts/MainLayout.vue'),
      children: [
        {path: '', component: () => import('pages/Dashboard.vue')},
        {path: '/Meets', component: () => import('pages/Meets.vue')},
        {path: '/Results', component: () => import('pages/Results.vue')}
      ]
    },
  
    // Always leave this as last one,
    // but you can also remove it
    {
      path: '/:catchAll(.*)*',
      component: () => import('pages/Error404.vue')
    },
    {
      path: '/Meets',
      component: () => import('pages/Meets.vue')
    },
    {
      path: '/Results',
      component: () => import('pages/Results.vue')
    },
    {
      path: '/Maintenance',
      component: () => import('pages/Maintenance.vue')
    }
  ]
  
  export default routes