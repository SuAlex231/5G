import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle auth errors
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Try to refresh token
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const response = await this.api.post('/auth/refresh', {
                refresh_token: refreshToken,
              });
              
              const { access_token, refresh_token: newRefreshToken } = response.data;
              localStorage.setItem('access_token', access_token);
              localStorage.setItem('refresh_token', newRefreshToken);
              
              // Retry original request
              error.config.headers.Authorization = `Bearer ${access_token}`;
              return this.api.request(error.config);
            } catch (refreshError) {
              // Refresh failed, redirect to login
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              window.location.href = '/login';
            }
          } else {
            // No refresh token, redirect to login
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async login(email: string, password: string) {
    const response = await this.api.post('/auth/login', { email, password });
    return response.data;
  }

  async logout() {
    await this.api.post('/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async getCurrentUser() {
    const response = await this.api.get('/users/me');
    return response.data;
  }

  // Ticket types
  async getTicketTypes() {
    const response = await this.api.get('/ticket-types');
    return response.data;
  }

  async getTicketTypeFields(ticketTypeId: number) {
    const response = await this.api.get(`/ticket-types/${ticketTypeId}/fields`);
    return response.data;
  }

  // Tickets
  async getTickets(params?: Record<string, any>) {
    const response = await this.api.get('/tickets', { params });
    return response.data;
  }

  async getTicket(id: number) {
    const response = await this.api.get(`/tickets/${id}`);
    return response.data;
  }

  async createTicket(data: any) {
    const response = await this.api.post('/tickets', data);
    return response.data;
  }

  async updateTicket(id: number, data: any) {
    const response = await this.api.put(`/tickets/${id}`, data);
    return response.data;
  }

  // Images
  async getTicketImages(ticketId: number) {
    const response = await this.api.get(`/tickets/${ticketId}/images`);
    return response.data;
  }

  async uploadTicketImage(ticketId: number, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.api.post(`/tickets/${ticketId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async deleteTicketImage(ticketId: number, imageId: number) {
    await this.api.delete(`/tickets/${ticketId}/images/${imageId}`);
  }

  // OCR
  async triggerOCR(ticketId: number, imageId: number) {
    const response = await this.api.post(`/tickets/${ticketId}/images/${imageId}/ocr`);
    return response.data;
  }

  async getOCRResult(ticketId: number, imageId: number) {
    const response = await this.api.get(`/tickets/${ticketId}/images/${imageId}/ocr-result`);
    return response.data;
  }

  async applyOCR(ticketId: number, fieldMappings: Record<string, string>) {
    const response = await this.api.post(`/tickets/${ticketId}/apply-ocr`, {
      field_mappings: fieldMappings,
    });
    return response.data;
  }

  // Export
  async exportTicketDocx(ticketId: number) {
    const response = await this.api.get(`/tickets/${ticketId}/export-docx`);
    return response.data;
  }

  async importExcel(ticketTypeId: number, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.api.post(`/ticket-types/${ticketTypeId}/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async exportExcel(ticketTypeId: number, filters?: Record<string, any>) {
    const response = await this.api.post(`/ticket-types/${ticketTypeId}/export`, filters);
    return response.data;
  }

  // Generic request method
  async request(config: AxiosRequestConfig) {
    const response = await this.api.request(config);
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;