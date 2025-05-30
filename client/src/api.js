// client/src/api.js
// client/src/api.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/', 
  headers: {
    'Content-Type': 'application/json', 
  },
});



export const getProjects = () => apiClient.get('projects/');
export const getProject = (id) => apiClient.get(`projects/${id}/`);
export const createProject = (data) => apiClient.post('projects/', data);
export const updateProject = (id, data) => apiClient.put(`projects/${id}/`, data);
export const deleteProject = (id) => apiClient.delete(`projects/${id}/`);

export const getTransportTypes = () => apiClient.get('transport-types/');
export const getTransportType = (id) => apiClient.get(`transport-types/${id}/`);
export const createTransportType = (data) => apiClient.post('transport-types/', data);
export const updateTransportType = (id, data) => apiClient.put(`transport-types/${id}/`, data);
export const deleteTransportType = (id) => apiClient.delete(`transport-types/${id}/`);

export const getStops = () => apiClient.get('stops/');
export const getStop = (id) => apiClient.get(`stops/${id}/`);
export const createStop = (data) => apiClient.post('stops/', data);
export const updateStop = (id, data) => apiClient.put(`stops/${id}/`, data);
export const deleteStop = (id) => apiClient.delete(`stops/${id}/`);

export const getRoutes = () => apiClient.get('routes/');
export const getRoute = (id) => apiClient.get(`routes/${id}/`);
export const createRoute = (data) => apiClient.post('routes/', data);
export const updateRoute = (id, data) => apiClient.put(`routes/${id}/`, data);
export const deleteRoute = (id) => apiClient.delete(`routes/${id}/`);

export const getRouteStops = () => apiClient.get('route-stops/');
export const getRouteStop = (id) => apiClient.get(`route-stops/${id}/`);
export const createRouteStop = (data) => apiClient.post('route-stops/', data);
export const updateRouteStop = (id, data) => apiClient.put(`route-stops/${id}/`, data);
export const deleteRouteStop = (id) => apiClient.delete(`route-stops/${id}/`);

export const getConnections = () => apiClient.get('connections/');
export const getConnection = (id) => apiClient.get(`connections/${id}/`);
export const createConnection = (data) => apiClient.post('connections/', data);
export const updateConnection = (id, data) => apiClient.put(`connections/${id}/`, data);
export const deleteConnection = (id) => apiClient.delete(`connections/${id}/`);


export const uploadGeoJSONFile = (file) => {
    const formData = new FormData();
    formData.append('geojson_file', file); // 'geojson_file' - это ключ, который ожидает бэкенд

    return apiClient.post('upload-geojson/', formData, {
        headers: {
            'Content-Type': undefined,
        }
    });
};