<!-- client/src/views/TransportTypeView.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import { getTransportTypes, createTransportType, updateTransportType, deleteTransportType } from '@/api';

const transportTypes = ref([]);
const newTransportType = ref({ name: '' });
const editingTransportType = ref(null);

const fetchTransportTypes = async () => {
  try {
    const response = await getTransportTypes();
    transportTypes.value = response.data;
  } catch (error) {
    console.error("Error fetching transport types:", error);
  }
};

const createItem = async () => {
  if (!newTransportType.value.name) return;
  try {
    await createTransportType(newTransportType.value);
    newTransportType.value.name = '';
    fetchTransportTypes();
  } catch (error) {
    console.error("Error creating transport type:", error);
    console.error("Response data:", error.response?.data);
  }
};

const startEditing = (type) => {
  editingTransportType.value = { ...type };
};

const cancelEditing = () => {
  editingTransportType.value = null;
};

const updateItem = async () => {
  if (!editingTransportType.value || !editingTransportType.value.name) return;
  try {
    await updateTransportType(editingTransportType.value.id, editingTransportType.value);
    cancelEditing();
    fetchTransportTypes();
  } catch (error) {
    console.error("Error updating transport type:", error);
    console.error("Response data:", error.response?.data);
  }
};

const deleteItem = async (id) => {
  if (confirm('Вы уверены, что хотите удалить этот тип транспорта?')) {
    try {
      await deleteTransportType(id);
      fetchTransportTypes();
    } catch (error) {
      console.error("Error deleting transport type:", error);
    }
  }
};

onMounted(fetchTransportTypes);

</script>

<template>
  <!-- Используем классы Bootstrap для отступов и контейнера (контейнер уже в App.vue, здесь отступ) -->
  <div class="mt-4">
    <h1>Типы транспорта</h1>

    <!-- Форма создания -->
    <div v-if="!editingTransportType" class="mb-4">
      <h2>Добавить новый</h2>
      <!-- Используем классы Bootstrap для формы -->
      <form @submit.prevent="createItem" class="row g-3 align-items-center">
        <div class="col-auto">
          <label for="newTypeName" class="visually-hidden">Название типа</label>
          <input type="text" class="form-control" id="newTypeName" v-model="newTransportType.name" placeholder="Название типа" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary">Создать</button>
        </div>
      </form>
    </div>

    <!-- Форма редактирования -->
    <div v-if="editingTransportType" class="mb-4">
      <h2>Редактировать тип транспорта</h2>
      <form @submit.prevent="updateItem" class="row g-3 align-items-center">
         <div class="col-auto">
          <label for="editTypeName" class="visually-hidden">Название типа</label>
          <input type="text" class="form-control" id="editTypeName" v-model="editingTransportType.name" placeholder="Название типа" required />
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-success">Сохранить</button>
        </div>
        <div class="col-auto">
          <button type="button" class="btn btn-secondary" @click="cancelEditing">Отмена</button>
        </div>
      </form>
    </div>

    <!-- Список типов транспорта -->
    <h2>Список</h2>
    <!-- Используем классы Bootstrap для таблицы -->
    <table class="table table-striped">
      <thead>
        <tr>
          <th>ID</th>
          <th>Название</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="type in transportTypes" :key="type.id">
          <td>{{ type.id }}</td>
          <td>{{ type.name }}</td>
          <td>
            <button class="btn btn-secondary btn-sm me-2" @click="startEditing(type)">Редактировать</button>
            <button class="btn btn-danger btn-sm" @click="deleteItem(type.id)">Удалить</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>

</style>