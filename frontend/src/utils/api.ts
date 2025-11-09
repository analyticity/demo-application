/*
	author: Veronika Šimková (xsimko14)
	file: api.ts
*/

import axios from "axios";

export const apiClient = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL}/api/v1`,
});
