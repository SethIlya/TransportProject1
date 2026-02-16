<script setup>
import { ref } from 'vue';
import { uploadGeoJSONFile } from '@/api';
import { useRouter } from 'vue-router';

const file = ref(null);
const isLoading = ref(false);
const uploadMessage = ref('');
const errorsList = ref([]); // Для хранения ошибок обработки отдельных записей
const router = useRouter();

// Обработчик выбора файла в input
const handleFileChange = (event) => {
  const selectedFile = event.target.files ? event.target.files[0] : null;

  if (selectedFile) {
    // Проверяем расширение файла на клиенте для быстрой обратной связи
    if (selectedFile.name.toLowerCase().endsWith('.geojson')) {
      file.value = selectedFile;
      uploadMessage.value = `Выбран файл: ${selectedFile.name}`;
      errorsList.value = []; // Очищаем старые ошибки
    } else {
      file.value = null;
      uploadMessage.value = 'Ошибка: Пожалуйста, выберите файл в формате .geojson';
      errorsList.value = [];
      // Очищаем поле ввода, чтобы пользователь мог выбрать тот же файл снова после ошибки
      event.target.value = '';
    }
  } else {
    file.value = null;
    uploadMessage.value = '';
    errorsList.value = [];
  }
};

// Обработчик клика по кнопке "Загрузить"
const handleUpload = async () => {
  if (!file.value) {
    uploadMessage.value = 'Пожалуйста, выберите файл для загрузки.';
    errorsList.value = [];
    return;
  }

  isLoading.value = true;
  uploadMessage.value = 'Загрузка и обработка...';
  errorsList.value = [];

  try {
    const response = await uploadGeoJSONFile(file.value);

    // Обработка успешного ответа от сервера
    uploadMessage.value = response.data.message || 'Файл успешно обработан.';
    errorsList.value = response.data.errors || [];

    // Очищаем поле ввода после успешной обработки
    file.value = null;
    const fileInput = document.getElementById('geojsonFileInput');
    if (fileInput) {
      fileInput.value = '';
    }

    // Если всё прошло идеально (нет ошибок в отдельных записях),
    // перенаправляем пользователя на страницу остановок через 2 секунды.
    if (response.status === 200 && errorsList.value.length === 0) {
      setTimeout(() => {
        router.push('/stops');
      }, 2000);
    } else if (errorsList.value.length > 0) {
      // Если были ошибки, обновляем сообщение для пользователя
      uploadMessage.value = `Импорт завершен. Обнаружены проблемы в ${errorsList.value.length} записях.`;
    }

  } catch (error) {
    console.error("Error uploading file:", error);
    // Обработка ошибок сети или сервера (например, 400, 500)
    uploadMessage.value = `Ошибка при загрузке: ${error.response?.data?.error || error.message}`;
    errorsList.value = error.response?.data?.errors || [];
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="container mt-4">
    <h1>Импорт остановок (GeoJSON)</h1>
    <p class="text-muted">
      Выберите файл <code>.geojson</code> для создания или обновления остановок в системе.
    </p>

    <div class="mb-3">
      <label for="geojsonFileInput" class="form-label">Файл GeoJSON:</label>
      <input
        class="form-control"
        type="file"
        id="geojsonFileInput"
        @change="handleFileChange"
        accept=".geojson"
      />
    </div>

    <button
      class="btn btn-primary"
      @click="handleUpload"
      :disabled="!file || isLoading"
    >
      <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
      <span v-if="isLoading">Обработка...</span>
      <span v-else>Загрузить и импортировать</span>
    </button>

    <!-- Блок для отображения результата -->
    <div v-if="uploadMessage" class="mt-4 alert" :class="{
      'alert-info': isLoading,
      'alert-success': !isLoading && errorsList.length === 0 && uploadMessage.includes('завершен'),
      'alert-warning': !isLoading && errorsList.length > 0,
      'alert-danger': !isLoading && uploadMessage.toLowerCase().includes('ошибка')
    }">
      <p class="mb-1">{{ uploadMessage }}</p>
      
      <!-- Если есть ошибки, показываем их списком -->
      <div v-if="errorsList.length > 0" class="mt-2">
        <strong>Список проблем:</strong>
        <ul class="mb-0">
          <li v-for="(error, index) in errorsList" :key="index">
            {{ error }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>