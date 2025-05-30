<!-- client/src/views/RouteStopView.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import { getRouteStops, createRouteStop, updateRouteStop, deleteRouteStop, getRoutes, getStops } from '@/api';

const routeStops = ref([]);
const routes = ref([]);
const stops = ref([]);
const newRouteStop = ref({ route: null, stop: null, order: null });
const editingRouteStop = ref(null);

const fetchRouteStops = async () => {
  try {
    const response = await getRouteStops();
    routeStops.value = response.data;
  } catch (error) {
    console.error("Error fetching route stops:", error);
  }
};

const fetchRoutes = async () => {
  try {
    const response = await getRoutes();
    routes.value = response.data;
  } catch (error) {
    console.error("Error fetching routes for dropdown:", error);
  }
};

const fetchStops = async () => {
  try {
    const response = await getStops();
    stops.value = response.data;
  } catch (error) {
    console.error("Error fetching stops for dropdown:", error);
  }
};


const createItem = async () => {
  if (newRouteStop.value.route === null || newRouteStop.value.stop === null || newRouteStop.value.order === null) return;
  if (newRouteStop.value.order < 0 || !Number.isInteger(Number(newRouteStop.value.order))) {
     alert("Порядок должен быть положительным целым числом.");
     return;
  }
  try {
    await createRouteStop({
      route: newRouteStop.value.route,
      stop: newRouteStop.value.stop,
      order: newRouteStop.value.order
    });
    newRouteStop.value = { route: null, stop: null, order: null };
    fetchRouteStops();
  } catch (error) {
    console.error("Error creating route stop:", error);
    console.error("Response data:", error.response?.data);
  }
};

const startEditing = (item) => {
   editingRouteStop.value = {
    id: item.id,
    route: item.route ? item.route.id : null,
    stop: item.stop ? item.stop.id : null,
    order: item.order
   };
};

const cancelEditing = () => {
  editingRouteStop.value = null;
};

const updateItem = async () => {
   if (editingRouteStop.value === null || editingRouteStop.value.route === null || editingRouteStop.value.stop === null || editingRouteStop.value.order === null) return;
   if (editingRouteStop.value.order < 0 || !Number.isInteger(Number(editingRouteStop.value.order))) {
     alert("Порядок должен быть положительным целым числом.");
     return;
   }
  try {
    await updateRouteStop(editingRouteStop.value.id, {
      route: editingRouteStop.value.route,
      stop: editingRouteStop.value.stop,
      order: editingRouteStop.value.order
    });
    cancelEditing();
    fetchRouteStops();
  } catch (error) {
    console.error("Error updating route stop:", error);
    console.error("Response data:", error.response?.data);
  }
};

const deleteItem = async (id) => {
  if (confirm('Вы уверены, что хотите удалить эту маршрутную остановку?')) {
    try {
      await deleteRouteStop(id);
      fetchRouteStops();
    } catch (error) {
      console.error("Error deleting route stop:", error);
    }
  }
};

onMounted(() => {
  fetchRouteStops();
  fetchRoutes();
  fetchStops();
});
</script>

<template>
  <div class="mt-4">
    <h1>Маршрутные остановки</h1>

    <!-- Форма создания -->
    <div v-if="!editingRouteStop" class="mb-4">
      <h2>Добавить новую</h2>
      <form @submit.prevent="createItem" class="row g-3 align-items-center">
        <div class="col-md-4">
           <label for="newRouteStopRoute" class="visually-hidden">Маршрут</label>
           <select class="form-select" id="newRouteStopRoute" v-model="newRouteStop.route" required>
            <option :value="null" disabled>Выберите маршрут</option>
            <option v-for="route in routes" :key="route.id" :value="route.id">
              {{ route.name }}
            </option>
          </select>
        </div>
         <div class="col-md-4">
           <label for="newRouteStopStop" class="visually-hidden">Остановка</label>
           <select class="form-select" id="newRouteStopStop" v-model="newRouteStop.stop" required>
            <option :value="null" disabled>Выберите остановку</option>
            <option v-for="stop in stops" :key="stop.id" :value="stop.id">
              {{ stop.name }}
            </option>
          </select>
        </div>
         <div class="col-md-2">
           <label for="newRouteStopOrder" class="visually-hidden">Порядок</label>
          <input type="number" min="0" step="1" class="form-control" id="newRouteStopOrder" v-model.number="newRouteStop.order" placeholder="Порядок" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary">Создать</button>
        </div>
      </form>
    </div>

    <!-- Форма редактирования -->
    <div v-if="editingRouteStop" class="mb-4">
      <h2>Редактировать маршрутную остановку</h2>
      <form @submit.prevent="updateItem" class="row g-3 align-items-center">
         <div class="col-md-4">
           <label for="editRouteStopRoute" class="visually-hidden">Маршрут</label>
           <select class="form-select" id="editRouteStopRoute" v-model="editingRouteStop.route" required>
            <option :value="null" disabled>Выберите маршрут</option>
            <option v-for="route in routes" :key="route.id" :value="route.id">
              {{ route.name }}
            </option>
          </select>
        </div>
         <div class="col-md-4">
           <label for="editRouteStopStop" class="visually-hidden">Остановка</label>
           <select class="form-select" id="editRouteStopStop" v-model="editingRouteStop.stop" required>
            <option :value="null" disabled>Выберите остановку</option>
            <option v-for="stop in stops" :key="stop.id" :value="stop.id">
              {{ stop.name }}
            </option>
          </select>
        </div>
         <div class="col-md-2">
           <label for="editRouteStopOrder" class="visually-hidden">Порядок</label>
           <input type="number" min="0" step="1" class="form-control" id="editRouteStopOrder" v-model.number="editingRouteStop.order" placeholder="Порядок" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-success">Сохранить</button>
        </div>
        <div class="col-auto">
          <button type="button" class="btn btn-secondary" @click="cancelEditing">Отмена</button>
        </div>
      </form>
    </div>

    <!-- Список маршрутных остановок -->
    <h2>Список</h2>
     <table class="table table-striped">
      <thead>
        <tr>
          <th>ID</th>
          <th>Маршрут</th>
          <th>Остановка</th>
          <th>Порядок</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in routeStops" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.route ? item.route.name : 'N/A' }}</td>
          <td>{{ item.stop ? item.stop.name : 'N/A' }}</td>
          <td>{{ item.order }}</td>
          <td>
            <button class="btn btn-secondary btn-sm me-2" @click="startEditing(item)">Редактировать</button>
            <button class="btn btn-danger btn-sm" @click="deleteItem(item.id)">Удалить</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
/* Удаляем старые стили */
</style>