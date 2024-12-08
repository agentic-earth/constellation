import axios from "axios";

// Create an Axios instance
const apiClient = axios.create({
  baseURL: "https://8000-01j4sd3wa349az1zg6nb8anjwx.cloudspaces.litng.ai", // Replace with your backend URL
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(
      `Sending ${config.method?.toUpperCase()} request to ${
        config.url
      } with data:`,
      config.data
    );
    return config;
  },
  (error) => {
    console.error("Error in request:", error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging
apiClient.interceptors.response.use(
  (response) => {
    console.log(
      `Received response from ${response.config.url}:`,
      response.data
    );
    return response;
  },
  (error) => {
    console.error("Error in response:", error);
    return Promise.reject(error);
  }
);

export default apiClient;
