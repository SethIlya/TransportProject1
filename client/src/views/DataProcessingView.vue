<script setup>
import { ref } from 'vue';
import { startCollectionPipeline, startImportPipeline } from '@/api';

const collectionLoading = ref(false);
const importLoading = ref(false);
const message = ref('');
const error = ref('');

const handleStartCollection = async () => {
  collectionLoading.value = true;
  message.value = 'Запускаем процесс сбора...';
  error.value = '';
  try {
    const response = await startCollectionPipeline();
    message.value = response.data.message;
  } catch (err) {
    handleError(err);
  } finally {
    collectionLoading.value = false;
  }
};

const handleStartImport = async () => {
  importLoading.value = true;
  message.value = 'Запускаем процесс импорта...';
  error.value = '';
  try {
    const response = await startImportPipeline();
    message.value = response.data.message;
  } catch (err) {
    handleError(err);
  } finally {
    importLoading.value = false;
  }
};

const handleError = (err) => {
  error.value = `Произошла ошибка: ${err.response?.data?.error || err.message}`;
  message.value = '';
};
</script>

<template>
  <div class="mt-4">
    <h1>Обработка данных</h1>
    <p class="text-muted">
      Управление процессами сбора данных с сайта irkbus.ru и их загрузки в базу данных.
    </p>

    <div class="row">
      <!-- Карточка для сбора данных -->
      <div class="col-md-6 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Этап 1: Сбор и очистка данных</h5>
            <p class="card-text">
              Запускает процесс, который собирает свежие данные с сайта, удаляет дубликаты и сортирует их по файлам в папку <code>data_processing_files/sorted_routes</code>.
            </p>
            <button class="btn btn-primary" @click="handleStartCollection" :disabled="collectionLoading || importLoading">
              <span v-if="collectionLoading" class="spinner-border spinner-border-sm me-2"></span>
              {{ collectionLoading ? 'Выполняется...' : '1. Собрать данные' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Карточка для импорта -->
      <div class="col-md-6 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Этап 2: Импорт в базу данных</h5>
            <p class="card-text">
              Берет ранее собранные и отсортированные файлы из папки <code>sorted_routes</code> и загружает их в базу данных.
            </p>
            <button class="btn btn-success" @click="handleStartImport" :disabled="collectionLoading || importLoading">
              <span v-if="importLoading" class="spinner-border spinner-border-sm me-2"></span>
              {{ importLoading ? 'Выполняется...' : '2. Импортировать в БД' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="message" class="alert alert-info mt-3">
      {{ message }}
    </div>
    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>
  </div>
</template>