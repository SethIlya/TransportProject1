<!-- client/src/views/FileUploadView.vue -->
<script setup>
import { ref } from 'vue';
import { uploadGeoJSONFile } from '@/api';
import { useRouter } from 'vue-router';

const file = ref(null);
const isLoading = ref(false);
const uploadMessage = ref('');
const errorsList = ref([]); // Для ошибок обработки отдельных записей
const router = useRouter();

const handleFileChange = (event) => {
  const selectedFile = event.target.files ? event.target.files[0] : null;

   if (selectedFile) {
       // Проверяем расширение файла на клиенте
       if (selectedFile.name.toLowerCase().endsWith('.geojson')) {
            file.value = selectedFile;
            uploadMessage.value = `Выбран файл: ${selectedFile.name}`;
            errorsList.value = []; // Очищаем ошибки при выборе нового файла
       } else {
           file.value = null;
           uploadMessage.value = 'Пожалуйста, выберите файл в формате .geojson';
           errorsList.value = [];
           // Очистить поле ввода файла в DOM, чтобы пользователь мог выбрать снова
           const fileInput = document.getElementById('geojsonFileInput');
           if (fileInput) {
               fileInput.value = '';
           }
       }
   } else {
       file.value = null;
       uploadMessage.value = ''; // Очищаем сообщение, если файл отменен
       errorsList.value = [];
   }
};

const handleUpload = async () => {
  if (!file.value) {
    uploadMessage.value = 'Пожалуйста, выберите файл для загрузки.';
    errorsList.value = [];
    return;
  }

  isLoading.value = true;
  uploadMessage.value = 'Загрузка и обработка...';
  errorsList.value = []; // Очищаем ошибки перед новой загрузкой


  try {
    const response = await uploadGeoJSONFile(file.value);

    // Обработка успешного ответа (статус 200 OK)
    uploadMessage.value = response.data.message || 'Файл успешно обработан.';
    errorsList.value = response.data.errors || []; // Ошибки обработки отдельных записей


     console.log("Импорт завершен:", response.data);

     // Очистить выбранный файл и поле ввода после обработки (опционально)
     file.value = null;
     const fileInput = document.getElementById('geojsonFileInput');
     if (fileInput) {
         fileInput.value = '';
     }

     // Перенаправление на страницу остановок через некоторое время
     // (можно сделать это только при полном успехе, или всегда)
      if (response.status === 200 && errorsList.value.length === 0) {
          setTimeout(() => {
              router.push('/stops'); // Перенаправляем на страницу остановок
          }, 1000); // Перенаправить через 2 секунды
      } else if (response.status === 200 && errorsList.value.length > 0) {
          // Если были ошибки обработки отдельных записей, но запрос в целом 200 OK
          // Остаемся на странице, показываем ошибки
          uploadMessage.value = `Импорт завершен с ошибками обработки ${errorsList.value.length} записей.`;
      }


  } catch (error) {
    console.error("Error uploading file:", error);

    // Обработка ошибок ответа (например, 400 Bad Request, 500 Internal Server Error)
    uploadMessage.value = `Ошибка при загрузке файла: ${error.response?.data?.error || error.message}`;
    // Если бэкенд вернул список ошибок обработки в response.data.errors при 400
    errorsList.value = error.response?.data?.errors || [];

  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="container mt-4">
    <h1>Загрузка GeoJSON</h1>

    <div class="mb-3">
        <label for="geojsonFileInput" class="form-label">Выберите файл GeoJSON (.geojson):</label>
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
      <span v-if="isLoading">Загрузка...</span>
      <span v-else>Загрузить и импортировать</span>
    </button>

    <!-- Сообщения о статусе и ошибках -->
    <div v-if="uploadMessage" class="mt-3 alert" :class="{'alert-info': isLoading, 'alert-success': !isLoading && errorsList.length === 0 && uploadMessage.includes('успешно'), 'alert-warning': errorsList.length > 0, 'alert-danger': !isLoading && errorsList.length === 0 && uploadMessage.includes('Ошибка')}">
        {{ uploadMessage }}
         <div v-if="errorsList.length > 0" class="mt-2">
             <strong>Список ошибок:</strong>
             <ul class="list-unstyled"> <!-- Убираем стандартные маркеры Bootstrap списка -->
                 <li v-for="(error, index) in errorsList" :key="index" class="text-danger">
                     {{ error }}
                 </li>
             </ul>
         </div>
    </div>

     <p class="mt-4 text-muted">
     </p>

  </div>
</template>

<style scoped>
/* Дополнительные стили при необходимости */
</style>