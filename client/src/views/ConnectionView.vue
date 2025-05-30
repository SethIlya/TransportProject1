<!-- client/src/views/ConnectionView.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import { getConnections, createConnection, updateConnection, deleteConnection, getStops } from '@/api';

const connections = ref([]);
const stops = ref([]);
const newConnection = ref({ from_stop: null, to_stop: null, travel_time: null });
const editingConnection = ref(null);

const fetchConnections = async () => {
  try {
    const response = await getConnections();
    connections.value = response.data;
  } catch (error) {
    console.error("Error fetching connections:", error);
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
  if (newConnection.value.from_stop === null || newConnection.value.to_stop === null || newConnection.value.travel_time === null) return;
  if (newConnection.value.from_stop === newConnection.value.to_stop) {
      alert("Остановки отправления и прибытия должны отличаться.");
      return;
  }
   if (newConnection.value.travel_time < 0 || !Number.isInteger(Number(newConnection.value.travel_time))) {
     alert("Время в пути должно быть неотрицательным целым числом.");
     return;
  }
  try {
    await createConnection({
      from_stop: newConnection.value.from_stop,
      to_stop: newConnection.value.to_stop,
      travel_time: newConnection.value.travel_time
    });
    newConnection.value = { from_stop: null, to_stop: null, travel_time: null };
    fetchConnections();
  } catch (error) {
    console.error("Error creating connection:", error);
    console.error("Response data:", error.response?.data);
  }
};

const startEditing = (item) => {
   editingConnection.value = {
    id: item.id,
    from_stop: item.from_stop ? item.from_stop.id : null,
    to_stop: item.to_stop ? item.to_stop.id : null,
    travel_time: item.travel_time
   };
};

const cancelEditing = () => {
  editingConnection.value = null;
};

const updateItem = async () => {
   if (editingConnection.value === null || editingConnection.value.from_stop === null || editingConnection.value.to_stop === null || editingConnection.value.travel_time === null) return;
   if (editingConnection.value.from_stop === editingConnection.value.to_stop) {
      alert("Остановки отправления и прибытия должны отличаться.");
      return;
   }
    if (editingConnection.value.travel_time < 0 || !Number.isInteger(Number(editingConnection.value.travel_time))) {
     alert("Время в пути должно быть неотрицательным целым числом.");
     return;
   }
  try {
    await updateConnection(editingConnection.value.id, {
      from_stop: editingConnection.value.from_stop,
      to_stop: editingConnection.value.to_stop,
      travel_time: editingConnection.value.travel_time
    });
    cancelEditing();
    fetchConnections();
  } catch (error) {
    console.error("Error updating connection:", error);
    console.error("Response data:", error.response?.data);
  }
};

const deleteItem = async (id) => {
  if (confirm('Вы уверены, что хотите удалить это соединение?')) {
    try {
      await deleteConnection(id);
      fetchConnections();
    } catch (error) {
      console.error("Error deleting connection:", error);
    }
  }
};

onMounted(() => {
  fetchConnections();
  fetchStops();
});
</script>

<template>
  <div class="mt-4">
    <h1>Соединения</h1>

    <!-- Форма создания -->
    <div v-if="!editingConnection" class="mb-4">
      <h2>Добавить новое</h2>
      <form @submit.prevent="createItem" class="row g-3 align-items-center">
        <div class="col-md-4">
           <label for="newConnectionFromStop" class="visually-hidden">От остановки</label>
           <select class="form-select" id="newConnectionFromStop" v-model="newConnection.from_stop" required>
            <option :value="null" disabled>От остановки</option>
            <option v-for="stop in stops" :key="stop.id" :value="stop.id">
              {{ stop.name }}
            </option>
          </select>
        </div>
         <div class="col-md-4">
           <label for="newConnectionToStop" class="visually-hidden">До остановки</label>
           <select class="form-select" id="newConnectionToStop" v-model="newConnection.to_stop" required>
            <option :value="null" disabled>До остановки</option>
            <option v-for="stop in stops" :key="stop.id" :value="stop.id">
              {{ stop.name }}
            </option>
          </select>
        </div>
         <div class="col-md-2">
            <label for="newConnectionTime" class="visually-hidden">Время в пути</label>
           <input type="number" min="0" step="1" class="form-control" id="newConnectionTime" v-model.number="newConnection.travel_time" placeholder="Время (мин)" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary">Создать</button>
        </div>
      </form>
    </div>

    <!-- Форма редактирования -->
    <div v-if="editingConnection" class="mb-4">
      <h2>Редактировать соединение</h2>
      <form @submit.prevent="updateItem" class="row g-3 align-items-center">
         <div class="col-md-4">
           <label for="editConnectionFromStop" class="visually-hidden">От остановки</label>
           <select class="form-select" id="editConnectionFromStop" v-model="editingConnection.from_stop" required>
            <option :value="null" disabled>От остановки</option>
            <option v-for="stop in stops" :key="stop.id" :value="stop.id">
              {{ stop.name }}
            </option>
          </select>
        </div>
         <div class="col-md-4">
           <label for="editConnectionToStop" class="visually-hidden">До остановки</label>
           <select class="form-select" id="editConnectionToStop" v-model="editingConnection.to_stop" required>
            <option :value="null" disabled>До остановки</option>
            <option v-for="stop in stops" :key="stop.id" :value="stop.id">
              {{ stop.name }}
            </option>
          </select>
        </div>
         <div class="col-md-2">
           <label for="editConnectionTime" class="visually-hidden">Время в пути</label>
           <input type="number" min="0" step="1" class="form-control" id="editConnectionTime" v-model.number="editingConnection.travel_time" placeholder="Время (мин)" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-success">Сохранить</button>
        </div>
        <div class="col-auto">
          <button type="button" class="btn btn-secondary" @click="cancelEditing">Отмена</button>
        </div>
      </form>
    </div>

    <!-- Список соединений -->
    <h2>Список</h2>
     <table class="table table-striped">
      <thead>
        <tr>
          <th>ID</th>
          <th>От остановки</th>
          <th>До остановки</th>
          <th>Время в пути (мин)</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in connections" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.from_stop ? item.from_stop.name : 'N/A' }}</td>
          <td>{{ item.to_stop ? item.to_stop.name : 'N/A' }}</td>
          <td>{{ item.travel_time }}</td>
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