<!-- client/src/views/StopView.vue -->
<!-- client/src/views/StopView.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import { getStops, createStop, updateStop, deleteStop } from '@/api';
// Возможно, понадобится библиотека для работы с GeoJSON/WKT на фронтенде, но для начала обойдемся без нее
// import { point } from '@turf/helpers'; // Пример с turf.js

const stops = ref([]);
// Инициализируем lat/lon для формы
const newStop = ref({ name: '', latitude: null, longitude: null });
const editingStop = ref(null); // При редактировании будем хранить данные Stop + lat/lon для формы

const fetchStops = async () => {
  try {
    const response = await getStops(); // GET запрос вернет Stop объекты с полем location (например, в WKT) и @property lat/lon
    stops.value = response.data;
    console.log("Fetched Stops:", stops.value); // Посмотрите в консоль, какой формат у поля location
  } catch (error) {
    console.error("Error fetching stops:", error);
  }
};

const createItem = async () => {
  // Валидация на наличие name и координат
  if (!newStop.value.name || newStop.value.latitude === null || newStop.value.longitude === null) return;
   // Валидация на числовые координаты (уже есть в type="number", но можно продублировать)
  if (typeof newStop.value.latitude !== 'number' || typeof newStop.value.longitude !== 'number') {
      alert("Широта и долгота должны быть числами.");
      return;
  }

  try {
    // Преобразуем отдельные широту/долготу в формат WKT Point для отправки на бэкенд
    // Формат WKT POINT: POINT(долгота широта)
    const locationWKT = `POINT(${newStop.value.longitude} ${newStop.value.latitude})`;

    // Отправляем данные, включая поле location в формате WKT
    await createStop({
      name: newStop.value.name,
      location: locationWKT, // Отправляем WKT строку
      // Старые поля latitude/longitude из формы не отправляем, если они удалены из модели
    });

    // Очищаем форму
    newStop.value = { name: '', latitude: null, longitude: null };
    fetchStops(); // Обновляем список
  } catch (error) {
    console.error("Error creating stop:", error);
    console.error("Response data:", error.response?.data);
  }
};

const startEditing = (stop) => {
   // Копируем объект для редактирования
   editingStop.value = {
       id: stop.id,
       name: stop.name,
       // Извлекаем lat/lon из объекта stop (они приходят благодаря @property)
       latitude: stop.latitude,
       longitude: stop.longitude,
       // Поле location из базы тоже копируем, хотя для формы редактирования оно напрямую не нужно
       location: stop.location
   };
};

const cancelEditing = () => {
  editingStop.value = null;
};

const updateItem = async () => {
  // Валидация
  if (!editingStop.value || !editingStop.value.name || editingStop.value.latitude === null || editingStop.value.longitude === null) return;
   if (typeof editingStop.value.latitude !== 'number' || typeof editingStop.value.longitude !== 'number') {
      alert("Широта и долгота должны быть числами.");
      return;
  }

  try {
    // Преобразуем отдельные широту/долготу в формат WKT Point для отправки на бэкенд
    const locationWKT = `POINT(${editingStop.value.longitude} ${editingStop.value.latitude})`;

    // Отправляем данные, включая поле location в формате WKT
    await updateStop(editingStop.value.id, {
      name: editingStop.value.name,
      location: locationWKT, // Отправляем WKT строку
       // Старые поля latitude/longitude из формы не отправляем
    });

    cancelEditing(); // Завершить редактирование
    fetchStops(); // Обновить список
  } catch (error) {
    console.error("Error updating stop:", error);
    console.error("Response data:", error.response?.data);
  }
};

const deleteItem = async (id) => {
  if (confirm('Вы уверены, что хотите удалить эту остановку?')) {
    try {
      await deleteStop(id);
      fetchStops(); // Обновить список
    } catch (error) {
      console.error("Error deleting stop:", error);
    }
  }
};

onMounted(fetchStops);
</script>

<template>
  <div class="mt-4">
    <h1>Остановки</h1>

    <!-- Форма создания -->
    <div v-if="!editingStop" class="mb-4">
      <h2>Добавить новую</h2>
      <form @submit.prevent="createItem" class="row g-3 align-items-center">
        <div class="col-md-4">
           <label for="newStopName" class="visually-hidden">Название остановки</label>
          <input type="text" class="form-control" id="newStopName" v-model="newStop.name" placeholder="Название остановки" required />
        </div>
         <div class="col-md-3">
           <label for="newStopLat" class="visually-hidden">Широта</label>
          <input type="number" step="0.000001" class="form-control" id="newStopLat" v-model.number="newStop.latitude" placeholder="Широта" required />
        </div>
         <div class="col-md-3">
           <label for="newStopLon" class="visually-hidden">Долгота</label>
          <input type="number" step="0.000001" class="form-control" id="newStopLon" v-model.number="newStop.longitude" placeholder="Долгота" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary">Создать</button>
        </div>
      </form>
    </div>

    <!-- Форма редактирования -->
    <div v-if="editingStop" class="mb-4">
      <h2>Редактировать остановку (ID: {{ editingStop.id }})</h2>
      <form @submit.prevent="updateItem" class="row g-3 align-items-center">
         <div class="col-md-4">
           <label for="editStopName" class="visually-hidden">Название остановки</label>
          <input type="text" class="form-control" id="editStopName" v-model="editingStop.name" placeholder="Название остановки" required />
        </div>
         <div class="col-md-3">
            <label for="editStopLat" class="visually-hidden">Широта</label>
          <input type="number" step="0.000001" class="form-control" id="editStopLat" v-model.number="editingStop.latitude" placeholder="Широта" required />
        </div>
         <div class="col-md-3">
           <label for="editStopLon" class="visually-hidden">Долгота</label>
          <input type="number" step="0.000001" class="form-control" id="editStopLon" v-model.number="editingStop.longitude" placeholder="Долгота" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-success">Сохранить</button>
        </div>
        <div class="col-auto">
          <button type="button" class="btn btn-secondary" @click="cancelEditing">Отмена</button>
        </div>
      </form>
    </div>

    <!-- Список остановок -->
    <h2>Список</h2>
    <table class="table table-striped">
      <thead>
        <tr>
          <th>ID</th>
          <th>Название</th>
          <th>Широта</th> <!-- Теперь получаем через @property -->
          <th>Долгота</th> <!-- Теперь получаем через @property -->
          <th>Location (WKT)</th> <!-- Опционально: показать сырые данные Point -->
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="stop in stops" :key="stop.id">
          <td>{{ stop.id }}</td>
          <td>{{ stop.name }}</td>
          <td>{{ stop.latitude !== null ? stop.latitude.toFixed(6) : 'N/A' }}</td> <!-- Используем @property, форматируем -->
          <td>{{ stop.longitude !== null ? stop.longitude.toFixed(6) : 'N/A' }}</td> <!-- Используем @property, форматируем -->
          <td>{{ stop.location || 'N/A' }}</td> <!-- Показываем сырые данные Point -->
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
/* Стили Bootstrap уже добавлены */
</style>