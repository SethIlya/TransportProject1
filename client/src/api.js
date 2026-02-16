import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- CRUD операции (без изменений) ---
export const getProjects = () => apiClient.get('projects/');
export const createProject = (data) => apiClient.post('projects/', data);
export const updateProject = (id, data) => apiClient.put(`projects/${id}/`, data);
export const deleteProject = (id) => apiClient.delete(`projects/${id}/`);

export const getTransportTypes = () => apiClient.get('transport-types/');
export const createTransportType = (data) => apiClient.post('transport-types/', data);
export const updateTransportType = (id, data) => apiClient.put(`transport-types/${id}/`, data);
export const deleteTransportType = (id) => apiClient.delete(`transport-types/${id}/`);

export const getStops = () => apiClient.get('stops/');
export const createStop = (data) => apiClient.post('stops/', data);
export const updateStop = (id, data) => apiClient.put(`stops/${id}/`, data);
export const deleteStop = (id) => apiClient.delete(`stops/${id}/`);

export const getRoutes = () => apiClient.get('routes/');
export const getRoute = (id) => apiClient.get(`routes/${id}/`);
export const createRoute = (data) => apiClient.post('routes/', data);
export const updateRoute = (id, data) => apiClient.put(`routes/${id}/`, data);
export const deleteRoute = (id) => apiClient.delete(`routes/${id}/`);

export const getRouteStops = () => apiClient.get('route-stops/');
export const createRouteStop = (data) => apiClient.post('route-stops/', data);
export const updateRouteStop = (id, data) => apiClient.put(`route-stops/${id}/`, data);
export const deleteRouteStop = (id) => apiClient.delete(`route-stops/${id}/`);

export const getConnections = () => apiClient.get('connections/');
export const createConnection = (data) => apiClient.post('connections/', data);
export const updateConnection = (id, data) => apiClient.put(`connections/${id}/`, data);
export const deleteConnection = (id) => apiClient.delete(`connections/${id}/`);

export const getVehicles = () => apiClient.get('vehicles/');
export const getVehicle = (id) => apiClient.get(`vehicles/${id}/`);
export const getVehiclePositions = (vehicleId = null, routeId = null) => {
    const params = new URLSearchParams();
    if (vehicleId) params.append('vehicle_id', vehicleId);
    if (routeId) params.append('route_id', routeId);
    return apiClient.get(`vehicle-positions/?${params.toString()}`);
};

// --- File Uploads ---
export const uploadGeoJSONFile = (file) => {
    const formData = new FormData();
    formData.append('geojson_file', file);
    return apiClient.post('upload-geojson/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
};

export const uploadBusDataFiles = (files) => {
    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file);
    }
    return apiClient.post('upload-bus-data/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
};

// --- Функции для экспорта данных ---

function downloadFile(response, defaultFilename) {
    const disposition = response.headers['content-disposition'];
    let filename = defaultFilename;
    if (disposition && disposition.indexOf('attachment') !== -1) {
        const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        const matches = filenameRegex.exec(disposition);
        if (matches != null && matches[1]) {
            filename = matches[1].replace(/['"]/g, '');
        }
    }
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
}

// Экспорт остановок
export const exportStopsCSV = async () => {
    const response = await apiClient.get('export/stops/csv/', { responseType: 'blob' });
    downloadFile(response, 'stops.csv');
};
export const exportStopsGeoJSON = async () => {
    const response = await apiClient.get('export/stops/geojson/', { responseType: 'blob' });
    downloadFile(response, 'stops.geojson');
};

// Экспорт позиций по маршруту
export const exportRoutePositionsCSV = async (routeId) => {
    const response = await apiClient.get(`export/route-positions/${routeId}/csv/`, { responseType: 'blob' });
    downloadFile(response, `route_${routeId}_positions.csv`);
};
export const exportRoutePositionsJSON = async (routeId) => {
    const response = await apiClient.get(`export/route-positions/${routeId}/json/`, { responseType: 'blob' });
    downloadFile(response, `route_${routeId}_positions.json`);
};

// Запускает только сбор и очистку данных
export const startCollectionPipeline = () => apiClient.post('start-collection-pipeline/');

// Запускает только импорт в БД
export const startImportPipeline = () => apiClient.post('start-import-pipeline/');

export const deleteMonitoringData = (routeIds = [], deleteAll = false) => {
    return apiClient.post('delete-monitoring-data/', {
        route_ids: routeIds,
        delete_all: deleteAll
    });
};