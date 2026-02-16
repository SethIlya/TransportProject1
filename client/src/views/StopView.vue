<script setup>
import { ref, onMounted } from 'vue';
import { getStops, createStop, updateStop, deleteStop, exportStopsCSV, exportStopsGeoJSON } from '@/api';

const stops = ref([]);
const newStop = ref({ name: '', latitude: null, longitude: null });
const editingStop = ref(null);

const fetchStops = async () => {
  try {
    const response = await getStops();
    stops.value = response.data;
  } catch (error) {
    console.error("Error fetching stops:", error);
  }
};

const createItem = async () => {
  if (!newStop.value.name || newStop.value.latitude === null || newStop.value.longitude === null) return;
  try {
    const locationWKT = `POINT(${newStop.value.longitude} ${newStop.value.latitude})`;
    await createStop({ name: newStop.value.name, location: locationWKT });
    newStop.value = { name: '', latitude: null, longitude: null };
    fetchStops();
  } catch (error) {
    console.error("Error creating stop:", error.response?.data);
  }
};

const startEditing = (stop) => {
   editingStop.value = { ...stop };
};

const cancelEditing = () => {
  editingStop.value = null;
};

const updateItem = async () => {
  if (!editingStop.value) return;
  try {
    const locationWKT = `POINT(${editingStop.value.longitude} ${editingStop.value.latitude})`;
    await updateStop(editingStop.value.id, { name: editingStop.value.name, location: locationWKT });
    cancelEditing();
    fetchStops();
  } catch (error) {
    console.error("Error updating stop:", error.response?.data);
  }
};

const deleteItem = async (id) => {
  if (confirm('Вы уверены, что хотите удалить эту остановку?')) {
    try {
      await deleteStop(id);
      fetchStops();
    } catch (error) {
      console.error("Error deleting stop:", error);
    }
  }
};

const handleExport = async (format) => {
  try {
    if (format === 'csv') {
      await exportStopsCSV();
    } else if (format === 'geojson') {
      await exportStopsGeoJSON();
    }
  } catch (error) {
    console.error(`Ошибка при экспорте остановок в ${format}:`, error);
    alert(`Не удалось экспортировать файл в формате ${format.toUpperCase()}.`);
  }
};

onMounted(fetchStops);
</script>

<template>
  <div class="mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1>Остановки</h1>
      <div class="btn-group">
        <button type="button" class="btn btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
          Экспорт
        </button>
        <ul class="dropdown-menu dropdown-menu-end">
          <li><a class="dropdown-item" href="#" @click.prevent="handleExport('csv')">Экспорт в CSV</a></li>
          <li><a class="dropdown-item" href="#" @click.prevent="handleExport('geojson')">Экспорт в GeoJSON</a></li>
        </ul>
      </div>
    </div>

    <!-- Формы и таблица -->
    <table class="table table-striped">
      <thead>
        <tr>
          <th>ID</th>
          <th>Название</th>
          <th>Широта</th>
          <th>Долгота</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="stop in stops" :key="stop.id">
          <td>{{ stop.id }}</td>
          <td>{{ stop.name }}</td>
          <td>{{ stop.latitude?.toFixed(6) }}</td>
          <td>{{ stop.longitude?.toFixed(6) }}</td>
          <td>
            <button class="btn btn-secondary btn-sm me-2" @click="startEditing(stop)">Редактировать</button>
            <button class="btn btn-danger btn-sm" @click="deleteItem(stop.id)">Удалить</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<style scoped>

</style>