<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getRoute, getVehiclePositions, exportRoutePositionsCSV, exportRoutePositionsJSON } from '@/api';

const route = useRoute();
const routeId = route.params.id;

const currentRoute = ref(null);
const positions = ref([]);
const isLoading = ref(true);

const formatTimestamp = (ts) => new Date(ts).toLocaleString('ru-RU');

const fetchAllData = async () => {
  isLoading.value = true;
  try {
    const [routeRes, positionsRes] = await Promise.all([
      getRoute(routeId),
      getVehiclePositions(null, routeId)
    ]);
    currentRoute.value = routeRes.data;
    positions.value = positionsRes.data;
  } catch (error) {
    console.error("Ошибка при загрузке данных о позициях:", error);
  } finally {
    isLoading.value = false;
  }
};

const handleExport = async (format) => {
  try {
    if (format === 'csv') {
      await exportRoutePositionsCSV(routeId);
    } else if (format === 'json') {
      await exportRoutePositionsJSON(routeId);
    }
  } catch (error) {
    console.error(`Ошибка при экспорте позиций в ${format}:`, error);
    alert(`Не удалось экспортировать файл в формате ${format.toUpperCase()}.`);
  }
};

onMounted(fetchAllData);
</script>

<template>
  <div class="mt-4">
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
    </div>
    <div v-else-if="currentRoute">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h1>История движения по маршруту: {{ currentRoute.name }}</h1>
        <div class="btn-group">
          <button type="button" class="btn btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
            Экспорт
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="#" @click.prevent="handleExport('csv')">Экспорт в CSV</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="handleExport('json')">Экспорт в JSON</a></li>
          </ul>
        </div>
      </div>

      <table class="table table-sm table-striped">
        <thead>
          <tr>
            <th>Время</th>
            <th>Гос. номер ТС</th>
            <th>Скорость (км/ч)</th>
            <th>Координаты (Ш, Д)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pos in positions" :key="pos.id">
            <td>{{ formatTimestamp(pos.timestamp) }}</td>
            <td>{{ pos.vehicle ? pos.vehicle.gos_num : 'N/A' }}</td>
            <td>{{ pos.speed }}</td>
            <td>{{ pos.latitude ? pos.latitude.toFixed(6) : 'N/A' }}, {{ pos.longitude ? pos.longitude.toFixed(6) : 'N/A' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="alert alert-warning">
        Не удалось загрузить информацию о маршруте.
    </div>
  </div>
</template>