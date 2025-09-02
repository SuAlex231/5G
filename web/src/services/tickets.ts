import { apiClient } from './api';
import { 
  Ticket, 
  TicketWithDetails, 
  TicketListResponse, 
  TicketType, 
  FormField, 
  TicketStatus 
} from '@/types';

export const ticketService = {
  // Ticket CRUD
  async getTickets(params?: {
    skip?: number;
    limit?: number;
    status?: TicketStatus;
    search?: string;
    ticket_type_id?: number;
  }): Promise<TicketListResponse> {
    return apiClient.get<TicketListResponse>('/tickets', params);
  },

  async getTicket(id: number): Promise<TicketWithDetails> {
    return apiClient.get<TicketWithDetails>(`/tickets/${id}`);
  },

  async createTicket(ticket: {
    ticket_type_id: number;
    title: string;
    data: Record<string, any>;
  }): Promise<Ticket> {
    return apiClient.post<Ticket>('/tickets', ticket);
  },

  async updateTicket(id: number, updates: {
    title?: string;
    status?: TicketStatus;
    data?: Record<string, any>;
    assigned_to?: number;
  }): Promise<Ticket> {
    return apiClient.put<Ticket>(`/tickets/${id}`, updates);
  },

  async deleteTicket(id: number): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>(`/tickets/${id}`);
  },

  // Ticket Types
  async getTicketTypes(): Promise<TicketType[]> {
    return apiClient.get<TicketType[]>('/tickets/types');
  },

  async getTicketTypeFields(ticketTypeId: number): Promise<FormField[]> {
    return apiClient.get<FormField[]>(`/tickets/types/${ticketTypeId}/fields`);
  },

  async createTicketType(ticketType: {
    name: string;
    description?: string;
    schema_config: Record<string, any>;
  }): Promise<TicketType> {
    return apiClient.post<TicketType>('/tickets/types', ticketType);
  },
};