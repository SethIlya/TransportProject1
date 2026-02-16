<script setup>
import { ref } from 'vue';
import { uploadBusDataFiles } from '@/api';

const files = ref(null);
const isLoading = ref(false);
const uploadResult = ref(null); // Для хранения полного объекта ответа от сервера

// Обработчик выбора файлов
const handleFileChange = (event) => {
  files.value = event.target.files;
  uploadResult.value = null; // Сбрасываем результат при выборе новых файлов
};

// Обработчик клика по кнопке "Загрузить"
const handleUpload = async () => {
  if (!files.value || files.value.length === 0) {
    uploadResult.value = {
      message: "Ошибка: Файлы не выбраны.",
      errors: ['Пожалуйста, выберите один или несколько файлов для загрузки.']
    };
    return;
  }

  isLoading.value = true;
  uploadResult.value = null;

  try {
    // Вызываем API-функцию для загрузки файлов
    const response = await uploadBusDataFiles(files.value);
    uploadResult.value = response.data; // Сохраняем результат
  } catch (error) {
    console.error("Error uploading bus data:", error);
    // Обрабатываем ошибки сети или сервера
    uploadResult.value = error.response?.data || {
      message: "Критическая ошибка: Не удалось связаться с сервером.",
      errors: [error.message]
    };
  } finally {
    isLoading.value = false;
    // Очищаем поле ввода файла и состояние после завершения
    const fileInput = document.getElementById('busDataInput');
    if (fileInput) fileInput.value = '';
    files.value = null;
  }
};
</script>

<template>
  <div class="container mt-4">
    <h1>Импорт данных о движении</h1>
    <p class="text-muted">
      Выберите один или несколько файлов <code>.json</code> или один архив <code>.zip</code> для импорта.
    </p>

    <div class="mb-3">
      <label for="busDataInput" class="form-label">Файлы для загрузки:</label>
      <input
        class="form-control"
        type="file"
        id="busDataInput"
        @change="handleFileChange"
        accept=".json,.zip"
        multiple
      />
    </div>

    <button
      class="btn btn-primary"
      @click="handleUpload"
      :disabled="!files || isLoading"
    >
      <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
      <span v-if="isLoading">Обработка...</span>
      <span v-else>Загрузить и импортировать</span>
    </button>

    <!-- Блок для отображения результата загрузки -->
    <div v-if="uploadResult" class="mt-4 alert" :class="{
      'alert-success': uploadResult.errors?.length === 0,
      'alert-warning': uploadResult.errors?.length > 0,
      'alert-danger': uploadResult.message.toLowerCase().includes('ошибка')
    }">
      <h5 class="alert-heading">{{ uploadResult.message }}</h5>
      
      <!-- Показываем статистику, если она есть -->
      <div v-if="uploadResult.total_positions_created !== undefined">
        <p><strong>Создано новых записей о позициях: {{ uploadResult.total_positions_created }}</strong></p>
      </div>

      <!-- Если есть ошибки, показываем их -->
      <div v-if="uploadResult.errors && uploadResult.errors.length > 0" class="mt-2">
        <hr>
        <strong>Список проблем:</strong>
        <ul>
          <li v-for="(error, index) in uploadResult.errors" :key="index">
            {{ error }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>