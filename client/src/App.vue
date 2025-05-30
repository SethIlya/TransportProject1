<!-- client/src/App.vue -->
<!-- client/src/App.vue -->
<script setup>
import { RouterLink, RouterView } from 'vue-router';
</script>

<template>
  <!-- Используем классы Bootstrap для навигационной панели -->
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container">
      <RouterLink class="navbar-brand" to="/">Transport App</RouterLink>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav">
          <li class="nav-item">
            <RouterLink class="nav-link" active-class="active" to="/">Главная</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" active-class="active" to="/transport-types">Тип транспорта</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" active-class="active" to="/stops">Остановки</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" active-class="active" to="/routes">Маршруты</RouterLink>
          </li>

          <li class="nav-item">
            <RouterLink class="nav-link" active-class="active" to="/connections">Последовательность остановок</RouterLink>
          </li>
           <li class="nav-item"> 
            <RouterLink class="nav-link" active-class="active" to="/upload">Загрузка</RouterLink>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- Добавим отступ сверху для основного контента -->
  <div class="container mt-4">
    <RouterView />
  </div>
</template>

<style scoped>
/* Ваши стили */
</style>