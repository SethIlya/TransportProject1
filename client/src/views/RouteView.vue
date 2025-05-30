<!-- client/src/views/RouteView.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import { getRoutes, createRoute, updateRoute, deleteRoute, getTransportTypes } from '@/api';

const routes = ref([]);
const transportTypes = ref([]);
const newRoute = ref({ name: '', transport_type: null });
const editingRoute = ref(null);

const fetchRoutes = async () => {
  try {
    const response = await getRoutes();
    routes.value = response.data;
  } catch (error) {
    console.error("Error fetching routes:", error);
  }
};

const fetchTransportTypes = async () => {
  try {
    const response = await getTransportTypes();
    transportTypes.value = response.data;
  } catch (error) {
    console.error("Error fetching transport types for dropdown:", error);
  }
};

const createItem = async () => {
  if (!newRoute.value.name || newRoute.value.transport_type === null) return;
  try {
    await createRoute({
      name: newRoute.value.name,
      transport_type: newRoute.value.transport_type
    });
    newRoute.value = { name: '', transport_type: null };
    fetchRoutes();
  } catch (error) {
    console.error("Error creating route:", error);
    console.error("Response data:", error.response?.data);
  }
};

const startEditing = (route) => {
  editingRoute.value = {
    id: route.id,
    name: route.name,
    transport_type: route.transport_type ? route.transport_type.id : null
  };
};

const cancelEditing = () => {
  editingRoute.value = null;
};

const updateItem = async () => {
  if (!editingRoute.value || !editingRoute.value.name || editingRoute.value.transport_type === null) return;
  try {
    await updateRoute(editingRoute.value.id, {
      name: editingRoute.value.name,
      transport_type: editingRoute.value.transport_type
    });
    cancelEditing();
    fetchRoutes();
  } catch (error) {
    console.error("Error updating route:", error);
    console.error("Response data:", error.response?.data);
  }
};

const deleteItem = async (id) => {
  if (confirm('Вы уверены, что хотите удалить этот маршрут?')) {
    try {
      await deleteRoute(id);
      fetchRoutes();
    } catch (error) {
      console.error("Error deleting route:", error);
    }
  }
};

onMounted(() => {
  fetchRoutes();
  fetchTransportTypes();
});
</script>

<template>
  <div class="mt-4">
    <h1>Маршруты</h1>

    <!-- Форма создания -->
    <div v-if="!editingRoute" class="mb-4">
      <h2>Добавить новый</h2>
      <form @submit.prevent="createItem" class="row g-3 align-items-center">
        <div class="col-md-6">
           <label for="newRouteName" class="visually-hidden">Название маршрута</label>
          <input type="text" class="form-control" id="newRouteName" v-model="newRoute.name" placeholder="Название маршрута" required />
        </div>
         <div class="col-md-4">
           <label for="newRouteTransportType" class="visually-hidden">Тип транспорта</label>
           <select class="form-select" id="newRouteTransportType" v-model="newRoute.transport_type" required>
            <option :value="null" disabled>Выберите тип транспорта</option>
            <option v-for="type in transportTypes" :key="type.id" :value="type.id">
              {{ type.name }}
            </option>
          </select>
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary">Создать</button>
        </div>
      </form>
    </div>

    <!-- Форма редактирования -->
    <div v-if="editingRoute" class="mb-4">
      <h2>Редактировать маршрут</h2>
      <form @submit.prevent="updateItem" class="row g-3 align-items-center">
         <div class="col-md-6">
            <label for="editRouteName" class="visually-hidden">Название маршрута</label>
           <input type="text" class="form-control" id="editRouteName" v-model="editingRoute.name" placeholder="Название маршрута" required />
         </div>
         <div class="col-md-4">
            <label for="editRouteTransportType" class="visually-hidden">Тип транспорта</label>
           <select class="form-select" id="editRouteTransportType" v-model="editingRoute.transport_type" required>
            <option :value="null" disabled>Выберите тип транспорта</option>
            <option v-for="type in transportTypes" :key="type.id" :value="type.id">
              {{ type.name }}
            </option>
          </select>
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-success">Сохранить</button>
        </div>
        <div class="col-auto">
          <button type="button" class="btn btn-secondary" @click="cancelEditing">Отмена</button>
        </div>
      </form>
    </div>

    <!-- Список маршрутов -->
    <h2>Список</h2>
    <table class="table table-striped">
      <thead>
        <tr>
          <th>ID</th>
          <th>Название</th>
          <th>Тип транспорта</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="route in routes" :key="route.id">
          <td>{{ route.id }}</td>
          <td>{{ route.name }}</td>
          <td>{{ route.transport_type ? route.transport_type.name : 'N/A' }}</td>
          <td>
            <button class="btn btn-secondary btn-sm me-2" @click="startEditing(route)">Редактировать</button>
            <button class="btn btn-danger btn-sm" @click="deleteItem(route.id)">Удалить</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
/* Удаляем старые стили */
</style>