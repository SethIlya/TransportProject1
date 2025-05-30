<!-- client/src/views/ProjectView.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import {
  getProjects, createProject, updateProject, deleteProject,
  getTransportTypes, getStops, getRoutes, getRouteStops, getConnections // Добавляем импорты API функций
} from '@/api';

const projects = ref([]);
const newProject = ref({
    name: '',
    transport_types: [], // Теперь это список ID для создания
    stops: [],
    routes: [],
    route_stops: [],
    connections: []
});
const editingProject = ref(null); // При редактировании будем хранить полные объекты, но отправлять ID

// Списки всех доступных связанных объектов для выбора
const allTransportTypes = ref([]);
const allStops = ref([]);
const allRoutes = ref([]);
const allRouteStops = ref([]);
const allConnections = ref([]);


// Загрузка всех проектов
const fetchProjects = async () => {
  try {
    const response = await getProjects(); // GET запрос вернет вложенные объекты благодаря to_representation
    projects.value = response.data;
    console.log("Fetched Projects:", projects.value);
  } catch (error) {
    console.error("Error fetching projects:", error);
  }
};

// Загрузка всех возможных связанных объектов
const fetchAllRelated = async () => {
    try {
        const [
            transportTypesRes,
            stopsRes,
            routesRes,
            routeStopsRes,
            connectionsRes
        ] = await Promise.all([
            getTransportTypes(),
            getStops(),
            getRoutes(),
            getRouteStops(),
            getConnections()
        ]);
        allTransportTypes.value = transportTypesRes.data;
        allStops.value = stopsRes.data;
        allRoutes.value = routesRes.data;
        allRouteStops.value = routeStopsRes.data;
        allConnections.value = connectionsRes.data;

         console.log("Fetched All Related:", {
            transportTypes: allTransportTypes.value,
            stops: allStops.value,
            routes: allRoutes.value,
            routeStops: allRouteStops.value,
            connections: allConnections.value
        });

    } catch (error) {
        console.error("Error fetching all related objects:", error);
    }
};


// Создание нового проекта
const createItem = async () => {
  if (!newProject.value.name) return;
  try {
    // При создании отправляем name и списки ID выбранных связанных объектов
    await createProject({
       name: newProject.value.name,
       transport_types: newProject.value.transport_types, // Список ID
       stops: newProject.value.stops, // Список ID
       routes: newProject.value.routes, // Список ID
       route_stops: newProject.value.route_stops, // Список ID
       connections: newProject.value.connections // Список ID
    });
    // Очистить форму создания
    newProject.value = {
        name: '',
        transport_types: [],
        stops: [],
        routes: [],
        route_stops: [],
        connections: []
    };
    fetchProjects(); // Обновить список проектов
  } catch (error) {
    console.error("Error creating project:", error);
    console.error("Response data:", error.response?.data);
  }
};

// Начало редактирования
const startEditing = (project) => {
  // Копируем объект для редактирования
  editingProject.value = {
      id: project.id,
      name: project.name,
      // Извлекаем только ID из вложенных объектов для форм выбора
      transport_types: project.transport_types.map(item => item.id),
      stops: project.stops.map(item => item.id),
      routes: project.routes.map(item => item.id),
      route_stops: project.route_stops.map(item => item.id),
      connections: project.connections.map(item => item.id),
  };
};

// Отмена редактирования
const cancelEditing = () => {
  editingProject.value = null;
};

// Сохранение изменений
const updateItem = async () => {
  if (!editingProject.value || !editingProject.value.name) return;
  try {
     // При обновлении отправляем ID проекта, name и списки ID выбранных связанных объектов
    await updateProject(editingProject.value.id, {
        name: editingProject.value.name,
        transport_types: editingProject.value.transport_types, // Список ID
        stops: editingProject.value.stops, // Список ID
        routes: editingProject.value.routes, // Список ID
        route_stops: editingProject.value.route_stops, // Список ID
        connections: editingProject.value.connections // Список ID
    });
    cancelEditing(); // Завершить редактирование
    fetchProjects(); // Обновить список
  } catch (error) {
    console.error("Error updating project:", error);
    console.error("Response data:", error.response?.data);
  }
};

// Удаление проекта
const deleteItem = async (id) => {
  if (confirm('Вы уверены, что хотите удалить этот проект?')) {
    try {
      await deleteProject(id);
      fetchProjects(); // Обновить список
    } catch (error) {
      console.error("Error deleting project:", error);
    }
  }
};

// Загрузить данные при монтировании компонента
onMounted(() => {
  fetchProjects();
  fetchAllRelated(); // Загружаем все возможные связанные объекты
});

// Вспомогательная функция для отображения имен связанных объектов в списках
// (остается как была или улучшается)

</script>

<template>
  <div class="mt-4">
    <h1>Город</h1>

    <!-- Форма создания -->
    <div v-if="!editingProject" class="mb-4">
      <h2>Добавить новый</h2>
      <form @submit.prevent="createItem" class="row g-3">
        <div class="col-md-6">
           <label for="newProjectName" class="form-label">Название города</label>
          <input type="text" class="form-control" id="newProjectName" v-model="newProject.name" placeholder="Название проекта" required />
        </div>

        <!-- Поля для выбора связанных объектов при создании -->
         <div class="col-md-6">
            <label for="newProjectTransportTypes" class="form-label">Типы транспорта</label>
            <select class="form-select" id="newProjectTransportTypes" multiple v-model="newProject.transport_types">
                <option v-for="item in allTransportTypes" :key="item.id" :value="item.id">
                    {{ item.name }}
                </option>
            </select>
            <small class="form-text text-muted">Зажмите Ctrl/Cmd для выбора нескольких.</small>
        </div>
         <div class="col-md-6">
            <label for="newProjectStops" class="form-label">Остановки</label>
            <select class="form-select" id="newProjectStops" multiple v-model="newProject.stops">
                <option v-for="item in allStops" :key="item.id" :value="item.id">
                    {{ item.name }}
                </option>
            </select>
             <small class="form-text text-muted">Зажмите Ctrl/Cmd для выбора нескольких.</small>
        </div>
         <div class="col-md-6">
            <label for="newProjectRoutes" class="form-label">Маршруты</label>
             <select class="form-select" id="newProjectRoutes" multiple v-model="newProject.routes">
                <option v-for="item in allRoutes" :key="item.id" :value="item.id">
                    {{ item.name }}
                </option>
            </select>
             <small class="form-text text-muted">Зажмите Ctrl/Cmd для выбора нескольких.</small>
        </div>
         <div class="col-md-6">
            <label for="newProjectRouteStops" class="form-label">Маршрутные остановки</label>
            <select class="form-select" id="newProjectRouteStops" multiple v-model="newProject.route_stops">
                <option v-for="item in allRouteStops" :key="item.id" :value="item.id">
                    {{ item.route?.name }} - {{ item.stop?.name }} (#{{ item.order }})
                </option>
            </select>
             <small class="form-text text-muted">Зажмите Ctrl/Cmd для выбора нескольких.</small>
        </div>
         <div class="col-md-6">
            <label for="newProjectConnections" class="form-label">Соединения</label>
             <select class="form-select" id="newProjectConnections" multiple v-model="newProject.connections">
                <option v-for="item in allConnections" :key="item.id" :value="item.id">
                    {{ item.from_stop?.name }} -> {{ item.to_stop?.name }} ({{ item.travel_time }} мин)
                </option>
            </select>
             <small class="form-text text-muted">Зажмите Ctrl/Cmd для выбора нескольких.</small>
        </div>


        <div class="col-12">
          <button type="submit" class="btn btn-primary">Создать</button>
        </div>
      </form>
    </div>

    <!-- Форма редактирования -->
    <div v-if="editingProject" class="mb-4">
      <h2>Редактировать проект (ID: {{ editingProject.id }})</h2>
      <form @submit.prevent="updateItem" class="row g-3">
         <div class="col-md-6">
           <label for="editProjectName" class="form-label">Название проекта</label>
           <input type="text" class="form-control" id="editProjectName" v-model="editingProject.name" placeholder="Название проекта" required />
        </div>

         <!-- Поля для выбора связанных объектов при редактировании -->
        <div class="col-md-6">
            <label for="editProjectTransportTypes" class="form-label">Типы транспорта</label>
            <select class="form-select" id="editProjectTransportTypes" multiple v-model="editingProject.transport_types">
                <option v-for="item in allTransportTypes" :key="item.id" :value="item.id">
                    {{ item.name }}
                </option>
            </select>
             <small class="form-text text-muted">Зажмите Ctrl/Cmd для выбора нескольких.</small>
        </div>
         <div class="col-md-6">
            <label for="editProjectStops" class="form-label">Остановки</label>
            <select class="form-select" id="editProjectStops" multiple v-model="editingProject.stops">
                <option v-for="item in allStops" :key="item.id" :value="item.id">
                    {{ item.name }}
                </option>
            </select>
             <small class="form-text text-muted">Зажмите Ctrl/Cmd для выбора нескольких.</small>
        </div>
         <div class="col-md-6">
            <label for="editProjectRoutes" class="form-label">Маршруты</label>
             <select class="form-select" id="editProjectRoutes" multiple v-model="editingProject.routes">
                <option v-for="item in allRoutes" :key="item.id" :value="item.id">
                    {{ item.name }}
                </option>
            </select>
             <small class="form-text text-muted">Зажмите Ctrl/Cmd для выбора нескольких.</small>
        </div>
         <div class="col-md-6">
            <label for="editProjectRouteStops" class="form-label">Маршрутные остановки</label>
            <select class="form-select" id="editProjectRouteStops" multiple v-model="editingProject.route_stops">
                <option v-for="item in allRouteStops" :key="item.id" :value="item.id">
                     {{ item.route?.name }} - {{ item.stop?.name }} (#{{ item.order }})
                </option>
            </select>
             <small class="form-text text-muted">Зажмите Ctrl/Cmd для выбора нескольких.</small>
        </div>
         <div class="col-md-6">
            <label for="editProjectConnections" class="form-label">Соединения</label>
             <select class="form-select" id="editProjectConnections" multiple v-model="editingProject.connections">
                <option v-for="item in allConnections" :key="item.id" :value="item.id">
                    {{ item.from_stop?.name }} -> {{ item.to_stop?.name }} ({{ item.travel_time }} мин)
                </option>
            </select>
             <small class="form-text text-muted">Зажмите Ctrl/Cmd для выбора нескольких.</small>
        </div>


        <div class="col-12">
          <button type="submit" class="btn btn-success me-2">Сохранить</button>
          <button type="button" class="btn btn-secondary" @click="cancelEditing">Отмена</button>
        </div>
      </form>
    </div>

    <!-- Список проектов (остается как была, т.к. GET возвращает вложенные объекты) -->
    <h2>Список</h2>
    <table class="table table-striped">
      <thead>
        <tr>
          <th>ID</th>
          <th>Название</th>
          <th>Связанные данные</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="project in projects" :key="project.id">
          <td>{{ project.id }}</td>
          <td>{{ project.name }}</td>
          <td>
            <!-- Отображение связанных элементов (теперь данные приходят как вложенные объекты) -->
            <div v-if="project.transport_types && project.transport_types.length > 0">
                <small><strong>Типы:</strong> {{ project.transport_types.map(t => t.name).join(', ') }}</small>
            </div>
             <div v-if="project.stops && project.stops.length > 0">
                <small><strong>Остановки:</strong> {{ project.stops.map(s => s.name).join(', ') }}</small>
            </div>
             <div v-if="project.routes && project.routes.length > 0">
                <small><strong>Маршруты:</strong> {{ project.routes.map(r => r.name).join(', ') }}</small>
            </div>
             <div v-if="project.route_stops && project.route_stops.length > 0">
                <small><strong>Маршрутные остановки:</strong> {{ project.route_stops.map(rs => `${rs.route?.name} - ${rs.stop?.name} (#${rs.order})`).join(', ') }}</small>
            </div>
             <div v-if="project.connections && project.connections.length > 0">
                <small><strong>Соединения:</strong> {{ project.connections.map(c => `${c.from_stop?.name} -> ${c.to_stop?.name} (${c.travel_time} мин)`).join(', ') }}</small>
            </div>
             <div v-if="!(project.transport_types?.length || project.stops?.length || project.routes?.length || project.route_stops?.length || project.connections?.length)">
                 <small class="text-muted">Нет связанных данных</small>
             </div>
          </td>
          <td>
            <button class="btn btn-secondary btn-sm me-2" @click="startEditing(project)">Редактировать</button>
            <button class="btn btn-danger btn-sm" @click="deleteItem(project.id)">Удалить</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
/* Стили Bootstrap уже добавлены глобально */
</style>