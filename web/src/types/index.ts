export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  roles: string[];
}

export interface Role {
  id: number;
  name: string;
  description?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface TicketType {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export interface FormField {
  id: number;
  ticket_type_id: number;
  field_name: string;
  field_label: string;
  field_type: string;
  field_options?: any;
  is_required: boolean;
  display_order: number;
  created_at: string;
}

export interface Ticket {
  id: number;
  ticket_type_id: number;
  ticket_number: string;
  title: string;
  status: string;
  priority: string;
  form_data: Record<string, any>;
  created_by_id: number;
  assigned_to_id?: number;
  created_at: string;
  updated_at: string;
}

export interface TicketImage {
  id: number;
  ticket_id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  display_order: number;
  uploaded_at: string;
}

export interface OCRResult {
  id: number;
  image_id: number;
  text_content: string;
  confidence: number;
  bbox_data?: any;
  processed_at: string;
}

export interface Job {
  id: number;
  job_id: string;
  job_type: string;
  status: string;
  result?: any;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}