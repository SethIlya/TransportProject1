<script setup>
import { ref, onMounted, computed } from 'vue';
import { getRoutes, deleteMonitoringData } from '@/api';
import { RouterLink } from 'vue-router';

const routes = ref([]);
const isLoading = ref(true);
const selectedRoutes = ref([]); // Массив для хранения ID выбранных маршрутов
const message = ref(''); // Для сообщений об успехе/ошибке

// Вычисляемое свойство для управления главным чекбоксом
const isAllSelected = computed({
  get: () => routes.value.length > 0 && selectedRoutes.value.length === routes.value.length,
  set: (value) => {
    selectedRoutes.value = value ? routes.value.map(r => r.id) : [];
  }
});

const fetchRoutes = async () => {
  isLoading.value = true;
  try {
    const response = await getRoutes();
    routes.value = response.data;
  } catch (error) {
    console.error("Ошибка при загрузке списка маршрутов:", error);
  } finally {
    isLoading.value = false;
  }
};

const handleDeleteSelected = async () => {
  if (selectedRoutes.value.length === 0) {
    alert("Пожалуйста, выберите маршруты для удаления.");
    return;
  }
  if (confirm(`Вы уверены, что хотите удалить все данные о движении для ${selectedRoutes.value.length} выбранных маршрутов?`)) {
    try {
      const response = await deleteMonitoringData(selectedRoutes.value, false);
      message.value = `${response.data.message} Позиций: ${response.data.deleted_positions}, ТС: ${response.data.deleted_vehicles}.`;
      selectedRoutes.value = []; // Очищаем выбор
      // Обновляем список маршрутов, чтобы показать актуальное состояние
      fetchRoutes(); 
    } catch (error) {
      handleError(error);
    }
  }
};

const handleDeleteAll = async () => {
  if (confirm("ВНИМАНИЕ! Это действие удалит ВСЕ данные о движении (все позиции и все транспортные средства) из базы данных. Вы уверены?")) {
    try {
      const response = await deleteMonitoringData([], true);
      message.value = `${response.data.message} Позиций: ${response.data.deleted_positions}, ТС: ${response.data.deleted_vehicles}.`;
      selectedRoutes.value = [];
      fetchRoutes();
    } catch (error) {
      handleError(error);
    }
  }
};

const handleError = (err) => {
  message.value = `Ошибка: ${err.response?.data?.error || err.message}`;
};

onMounted(fetchRoutes);
</script>

<template>
  <div class="mt-4">
    <h1>Мониторинг по маршрутам</h1>
    <p class="text-muted">Список всех маршрутов, по которым были загружены данные о движении.</p>

    <!-- NEW: Панель управления удалением -->
    <div class="mb-3 d-flex gap-2">
      <button 
        class="btn btn-warning" 
        @click="handleDeleteSelected" 
        :disabled="selectedRoutes.length === 0"
      >
        Удалить данные для выбранных
      </button>
      <button 
        class="btn btn-danger" 
        @click="handleDeleteAll"
      >
        Удалить все данные
      </button>
    </div>
    
    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else>
      <table class="table table-striped table-hover">
        <thead class="table-light">
          <tr>
            <th><input type="checkbox" v-model="isAllSelected" class="form-check-input"></th>
            <th>ID</th>
            <th>Название маршрута</th>
            <th>Тип транспорта</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="route in routes" :key="route.id">
            <td><input type="checkbox" :value="route.id" v-model="selectedRoutes" class="form-check-input"></td>
            <td>{{ route.id }}</td>
            <td>{{ route.name }}</td>
            <td>{{ route.transport_type ? route.transport_type.name : 'N/A' }}</td>
            <td>
              <RouterLink :to="`/routes/${route.id}/positions`" class="btn btn-primary btn-sm">
                Посмотреть историю
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>