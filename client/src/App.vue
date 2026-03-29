<!-- client/src/App.vue -->
<script setup>
import { ref } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

const route = useRoute()

// Гамбургер — только загрузка и импорт
const hamOpen = ref(false)

// Модальное окно "Данные общественного транспорта"
const transportModalOpen = ref(false)

function openTransportModal() {
  transportModalOpen.value = true
  hamOpen.value = false
}
</script>

<template>
  <!-- ══ NAVBAR ══════════════════════════════════════ -->
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">

      <!-- Гамбургер — только загрузка и импорт -->
      <div class="dropdown me-2">
        <button
          class="btn btn-dark border-0 px-2 py-1"
          @click="hamOpen = !hamOpen"
          title="Загрузка и импорт"
        >
          <!-- Три полоски -->
          <svg width="20" height="16" viewBox="0 0 20 16" fill="none">
            <rect y="0"  width="20" height="2" rx="1" fill="white"/>
            <rect y="7"  width="20" height="2" rx="1" fill="white"/>
            <rect y="14" width="20" height="2" rx="1" fill="white"/>
          </svg>
        </button>

        <ul v-if="hamOpen" class="dropdown-menu dropdown-menu-dark show mt-1"
            style="min-width:230px;"
            v-click-outside="() => hamOpen = false">
          <li>
            <span class="dropdown-header" style="font-size:10px; letter-spacing:.5px;">
              ЗАГРУЗКА ДАННЫХ
            </span>
          </li>
          <li>
            <RouterLink class="dropdown-item" to="/data-processing" @click="hamOpen = false">
              Сбор и обработка данных
            </RouterLink>
          </li>
          <li><hr class="dropdown-divider"/></li>
          <li>
            <span class="dropdown-header" style="font-size:10px; letter-spacing:.5px;">
              ИМПОРТ
            </span>
          </li>
          <li>
            <RouterLink class="dropdown-item" to="/upload" @click="hamOpen = false">
              Импорт остановок (GeoJSON)
            </RouterLink>
          </li>
          <li>
            <RouterLink class="dropdown-item" to="/upload-bus-data" @click="hamOpen = false">
              Импорт данных о движении
            </RouterLink>
          </li>
        </ul>
      </div>

      <RouterLink class="navbar-brand" to="/">TransportGIS</RouterLink>

      <div class="collapse navbar-collapse">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">

          <!-- Данные общественного транспорта → открывает модалку -->
          <li class="nav-item">
            <button class="nav-link btn btn-link text-white border-0 bg-transparent px-3"
                    style="text-decoration:none; font-size:1rem;"
                    @click="openTransportModal">
              Данные общественного транспорта
            </button>
          </li>

          <!-- Ранжирование -->
          <li class="nav-item">
            <a class="nav-link" href="/analysis/ranking">Ранжирование</a>
          </li>

          <!-- Анализ доступности -->
          <li class="nav-item">
            <a class="nav-link" href="/analysis">Анализ доступности</a>
          </li>

        </ul>
      </div>
    </div>
  </nav>

  <!-- ══ МОДАЛКА «Данные общественного транспорта» ══ -->
  <Transition name="modal-fade">
    <div v-if="transportModalOpen"
         class="transport-modal-overlay"
         @click.self="transportModalOpen = false">
      <div class="transport-modal">
        <div class="tm-header">
          <span class="tm-title">Данные общественного транспорта</span>
          <button class="tm-close btn-close" @click="transportModalOpen = false"></button>
        </div>
        <div class="tm-body">

          <div class="tm-col">
            <div class="tm-group-title">Справочники</div>
            <RouterLink class="tm-link" to="/transport-types" @click="transportModalOpen = false">
              Типы транспорта
            </RouterLink>
            <RouterLink class="tm-link" to="/stops" @click="transportModalOpen = false">
              Остановки
            </RouterLink>
            <RouterLink class="tm-link" to="/routes" @click="transportModalOpen = false">
              Маршруты
            </RouterLink>

          </div>

          <div class="tm-col">
            <div class="tm-group-title">Мониторинг и данные</div>
            <RouterLink class="tm-link" to="/monitoring" @click="transportModalOpen = false">
              Мониторинг по маршрутам
            </RouterLink>
            <RouterLink class="tm-link" to="/data-processing" @click="transportModalOpen = false">
              Обработка данных
            </RouterLink>
          </div>

          <div class="tm-col">
            <div class="tm-group-title">Импорт</div>
            <RouterLink class="tm-link" to="/upload" @click="transportModalOpen = false">
              Импорт остановок (GeoJSON)
            </RouterLink>
            <RouterLink class="tm-link" to="/upload-bus-data" @click="transportModalOpen = false">
              Импорт данных о движении
            </RouterLink>
          </div>

        </div>
      </div>
    </div>
  </Transition>

  <!-- ══ КОНТЕНТ СТРАНИЦ ══════════════════════════════ -->
  <main :class="route.path === '/' ? 'flex-grow-1 overflow-hidden' : 'container mt-4'">
    <RouterView />
  </main>
</template>

<style>
html, body { height: 100%; margin: 0; }
#app { display: flex; flex-direction: column; height: 100vh; }

.dropdown-item.router-link-active.router-link-exact-active {
  background-color: rgba(255,255,255,.1);
}

/* ── Модальное окно ─────────────────────────────── */
.transport-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, .55);
  z-index: 1050;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 80px;
}

.transport-modal {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0,0,0,.3);
  width: 700px;
  max-width: 95vw;
  overflow: hidden;
}

.tm-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid #dee2e6;
  background: #f8f9fa;
}

.tm-title {
  font-size: 15px;
  font-weight: 700;
  color: #212529;
}

.tm-close { flex-shrink: 0; }

.tm-body {
  display: flex;
  gap: 0;
  padding: 24px;
  gap: 32px;
}

.tm-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.tm-group-title {
  font-size: 10px;
  font-weight: 700;
  color: #adb5bd;
  text-transform: uppercase;
  letter-spacing: .6px;
  margin-bottom: 8px;
}

.tm-link {
  display: block;
  padding: 7px 10px;
  font-size: 14px;
  color: #343a40;
  text-decoration: none;
  border-radius: 6px;
  transition: background .12s, color .12s;
}
.tm-link:hover {
  background: #f0f4ff;
  color: #0d6efd;
}

/* Анимация */
.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity .2s;
}
.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}
</style>