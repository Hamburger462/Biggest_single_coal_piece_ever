import axios from "axios";
import type { AxiosInstance } from "axios";

export const api: AxiosInstance = axios.create({
  baseURL: "http://127.0.0.1:8000",
  // timeout: 10000,
});

// Api endpoints
//  / - Check api's health
//  /predict/single - Model predicts a text output of a image-text input
//  /predict/candidates - Model predicts a probabilities of fixed or lower amount of candidates based on a image-text input