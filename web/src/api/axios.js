import axios from "axios";
import { getAuthToken } from "./AuthStorage";

const { REACT_APP_API_BASE_URL } = process.env;

// axios.defaults.headers.common['Authorization'] = `bearer `+ getAuthToken()

// export const api = () => {
//
//     const defaultOptions = {
//         baseURL: "http://localhost:8000/api",
//         headers: {
//             'Content-Type': 'application/json',
//         },
//     };
//
//     // Create instance
//     const instance = axios.create(defaultOptions);
//
//     // Set the AUTH token for any request
//     instance.interceptors.request.use(function (config) {
//         const token = localStorage.getItem('token');
//         config.headers.Authorization = token ? `Bearer ${token}` : '';
//         return config;
//     });
//
//     return instance;
// };

export const api = axios.create({
  // withCredentials: true,
  baseURL: REACT_APP_API_BASE_URL,
  // headers:  {'Authorization': `bearer `+ getAuthToken()}
});

export const api_base = axios.create({
  baseURL: REACT_APP_API_BASE_URL,
});

api.interceptors.request.use(function (config) {
  const token = getAuthToken();
  config.headers.Authorization = `Bearer ` + token;

  return config;
});
