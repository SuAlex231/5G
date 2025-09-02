import { apiClient } from './api';
import { TicketImage, FileUploadResponse, OCRResult } from '@/types';

export const fileService = {
  // File upload
  async getUploadUrl(): Promise<FileUploadResponse> {
    return apiClient.post<FileUploadResponse>('/files/upload-url');
  },

  async uploadFile(uploadUrl: string, file: File): Promise<void> {
    // Use native fetch for pre-signed URL upload
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(uploadUrl, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type,
      },
    });
    
    if (!response.ok) {
      throw new Error('File upload failed');
    }
  },

  // Ticket images
  async getTicketImages(ticketId: number): Promise<TicketImage[]> {
    return apiClient.get<TicketImage[]>(`/files/tickets/${ticketId}/images`);
  },

  async addTicketImage(ticketId: number, imageData: {
    minio_key: string;
    filename: string;
    original_filename: string;
    file_size: number;
    mime_type: string;
    order_index?: number;
  }): Promise<TicketImage> {
    const formData = new FormData();
    Object.entries(imageData).forEach(([key, value]) => {
      formData.append(key, value.toString());
    });

    const response = await fetch(
      `${import.meta.env.VITE_API_BASE_URL}/api/v1/files/tickets/${ticketId}/images`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error('Failed to add image to ticket');
    }

    return response.json();
  },

  async updateImage(imageId: number, updates: {
    order_index?: number;
    metadata?: Record<string, any>;
  }): Promise<TicketImage> {
    return apiClient.put<TicketImage>(`/files/images/${imageId}`, updates);
  },

  async deleteImage(imageId: number): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>(`/files/images/${imageId}`);
  },

  async getImageDownloadUrl(imageId: number): Promise<{ download_url: string }> {
    return apiClient.get<{ download_url: string }>(`/files/images/${imageId}/download`);
  },
};