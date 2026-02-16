// client/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ProjectView from '../views/ProjectView.vue'
import TransportTypeView from '../views/TransportTypeView.vue'
import StopView from '../views/StopView.vue'
import RouteView from '../views/RouteView.vue'
import RouteStopView from '../views/RouteStopView.vue'
import ConnectionView from '../views/ConnectionView.vue'
// --- ИСПРАВЛЕНИЕ: Импортируем новые компоненты ---
import FileUploadView from '../views/FileUploadView.vue'
import BusDataUploadView from '../views/BusDataUploadView.vue'
// -------------------------------------------------
import MonitoringRoutesView from '../views/MonitoringRoutesView.vue'
import RoutePositionsView from '../views/RoutePositionsView.vue'

import DataProcessingView from '../views/DataProcessingView.vue';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/projects', name: 'projects', component: ProjectView },
    { path: '/transport-types', name: 'transport-types', component: TransportTypeView },
    { path: '/stops', name: 'stops', component: StopView },
    { path: '/routes', name: 'routes', component: RouteView },
    { path: '/route-stops', name: 'route-stops', component: RouteStopView },
    { path: '/connections', name: 'connections', component: ConnectionView },
    
    // --- Добавляем маршруты для импорта ---
    { path: '/upload', name: 'upload-geojson', component: FileUploadView },
    { path: '/upload-bus-data', name: 'upload-bus-data', component: BusDataUploadView },
    // ---------------------------------------
    
    {
      path: '/monitoring', 
      name: 'monitoring-routes',
      component: MonitoringRoutesView
    },
    {
      path: '/routes/:id/positions', 
      name: 'route-positions',
      component: RoutePositionsView
    },
    {
      path: '/data-processing',
      name: 'data-processing',
      component: DataProcessingView
    }
  ]
})

export default router