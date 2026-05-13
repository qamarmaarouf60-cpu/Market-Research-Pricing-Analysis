import api from "./client";

export const login = (username, password) =>
  api.post("/api/token/", { username, password });

export const register = (data) =>
  api.post("/api/users/register/", data);

export const getMe = () => api.get("/api/users/me/");

export const getProducts = (params = {}) =>
  api.get("/api/products/", { params });

export const getProductStats = (params = {}) =>
  api.get("/api/products/stats/", { params });

export const getSources = () => api.get("/api/products/sources/");

export const globalSearch = (q) =>
  api.get("/api/search/", { params: { q } });

export const getSearchHistory = () => api.get("/api/search/history/");

export const getAnalyticsStats = (params = {}) =>
  api.get("/api/analytics/stats/", { params });

export const getDistribution = (params = {}) =>
  api.get("/api/analytics/distribution/", { params });

export const analyzeQuery = (query) =>
  api.post("/api/analytics/analyze/", { query });

export const scrapeAndAnalyze = (query) =>
  api.post("/api/analytics/scrape-analyze/", { query });

export const getJobStatus = (query) =>
  api.get("/api/analytics/job-status/", { params: { query } });