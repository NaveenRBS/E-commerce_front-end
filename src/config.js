import API_BASE_URL from "./config.js";

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`
});