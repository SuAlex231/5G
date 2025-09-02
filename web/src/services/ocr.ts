import { apiClient } from './api';
import { OCRResult } from '@/types';

export const ocrService = {
  async triggerImageOCR(imageId: number): Promise<{ message: string; result_id: number }> {
    return apiClient.post<{ message: string; result_id: number }>(`/ocr/images/${imageId}/process`);
  },

  async getImageOCRResults(imageId: number): Promise<OCRResult> {
    return apiClient.get<OCRResult>(`/ocr/images/${imageId}/results`);
  },

  async applyOCRToTicket(ticketId: number, fieldMappings: Record<string, string>): Promise<{
    message: string;
    applied_mappings: Record<string, any>;
  }> {
    return apiClient.post<{
      message: string;
      applied_mappings: Record<string, any>;
    }>(`/ocr/tickets/${ticketId}/apply-ocr`, {
      field_mappings: fieldMappings,
    });
  },

  async getAvailableOCRData(ticketId: number): Promise<Record<string, {
    image_filename: string;
    text_data: Record<string, any>;
    confidence: number;
    processing_time?: number;
  }>> {
    return apiClient.get<Record<string, any>>(`/ocr/tickets/${ticketId}/available-ocr-data`);
  },
};