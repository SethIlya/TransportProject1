// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import ProjectView from '../views/ProjectView.vue';
import TransportTypeView from '../views/TransportTypeView.vue';
import StopView from '../views/StopView.vue';
import RouteView from '../views/RouteView.vue';
import RouteStopView from '../views/RouteStopView.vue';
import ConnectionView from '../views/ConnectionView.vue';
import FileUploadView from '../views/FileUploadView.vue'; // <-- Импортируем новый компонент

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    // Маршруты для CRUD моделей
    {
      path: '/projects',
      name: 'projects',
      component: ProjectView
    },
    {
      path: '/transport-types',
      name: 'transport-types',
      component: TransportTypeView
    },
    {
      path: '/stops',
      name: 'stops',
      component: StopView
    },
    {
      path: '/routes',
      name: 'routes',
      component: RouteView
    },
    {
      path: '/route-stops',
      name: 'route-stops',
      component: RouteStopView
    },
    {
      path: '/connections',
      name: 'connections',
      component: ConnectionView
    },
     { // <-- Новый маршрут для загрузки файла
       path: '/upload',
       name: 'upload-geojson',
       component: FileUploadView
     },
  ]
});

export default router;