<!-- client/src/App.vue -->
<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <RouterLink class="navbar-brand" to="/">TransportGIS</RouterLink>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <RouterLink class="nav-link" active-class="active" to="/">Главная</RouterLink>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Справочники
            </a>
            <ul class="dropdown-menu" aria-labelledby="navbarDropdown">
              <li><RouterLink class="dropdown-item" to="/transport-types">Типы транспорта</RouterLink></li>
              <li><RouterLink class="dropdown-item" to="/stops">Остановки</RouterLink></li>
              <li><RouterLink class="dropdown-item" to="/routes">Маршруты</RouterLink></li>
              <li><hr class="dropdown-divider"></li>
              <li><RouterLink class="dropdown-item" to="/route-stops">Маршрутные остановки</RouterLink></li>
              <li><RouterLink class="dropdown-item" to="/connections">Соединения</RouterLink></li>
            </ul>
          </li>
          
          <li class="nav-item">
            <RouterLink class="nav-link" active-class="active" to="/monitoring">Мониторинг</RouterLink>
          </li>

          <li class="nav-item">
            <RouterLink class="nav-link" active-class="active" to="/data-processing">Обработка данных</RouterLink>
          </li>
          <!-- --- ИСПРАВЛЕНИЕ: Добавляем выпадающее меню для импорта --- -->
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarUploadDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Импорт данных
            </a>
            <ul class="dropdown-menu" aria-labelledby="navbarUploadDropdown">
              <li><RouterLink class="dropdown-item" to="/upload">Импорт остановок (GeoJSON)</RouterLink></li>
              <li><RouterLink class="dropdown-item" to="/upload-bus-data">Импорт данных о движении</RouterLink></li>
            </ul>
          </li>
          <!-- ----------------------------------------------------- -->
        </ul>
      </div>
    </div>
  </nav>

  <main class="container mt-4">
    <RouterView />
  </main>
</template>

<style>
.dropdown-item.router-link-active.router-link-exact-active {
  background-color: #e9ecef;
  color: #000;
}
</style>