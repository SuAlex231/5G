// API types
export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Role {
  id: number;
  name: string;
  description: string;
  permissions: Record<string, string[]>;
}

export interface RoleAssignment {
  id: number;
  user_id: number;
  role_id: number;
  created_at: string;
  role: Role;
}

export interface UserWithRoles extends User {
  role_assignments: RoleAssignment[];
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Ticket types
export enum TicketStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export interface TicketType {
  id: number;
  name: string;
  description: string;
  schema_config: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FormField {
  id: number;
  ticket_type_id: number;
  field_name: string;
  field_type: string;
  field_label: string;
  config: Record<string, any>;
  order_index: number;
  is_required: boolean;
  created_at: string;
}

export interface Ticket {
  id: number;
  ticket_type_id: number;
  user_id: number;
  ticket_number: string;
  title: string;
  status: TicketStatus;
  data: Record<string, any>;
  assigned_to?: number;
  created_at: string;
  updated_at: string;
}

export interface TicketWithDetails extends Ticket {
  ticket_type: TicketType;
  images: TicketImage[];
}

export interface TicketListResponse {
  items: Ticket[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// File types
export interface TicketImage {
  id: number;
  ticket_id: number;
  filename: string;
  original_filename: string;
  minio_key: string;
  file_size: number;
  mime_type: string;
  order_index: number;
  metadata: Record<string, any>;
  created_at: string;
}

export interface OCRResult {
  id: number;
  image_id: number;
  text_data: Record<string, any>;
  confidence: number;
  bbox_data?: Record<string, any>;
  processing_time?: number;
  created_at: string;
}

export interface FileUploadResponse {
  upload_url: string;
  file_key: string;
  fields?: Record<string, any>;
}

// Component types
export interface TableColumn {
  title: string;
  dataIndex: string;
  key: string;
  render?: (value: any, record: any, index: number) => React.ReactNode;
  width?: number;
  fixed?: 'left' | 'right';
  sorter?: boolean;
  filters?: Array<{ text: string; value: any }>;
}

export interface FormFieldConfig extends FormField {
  component?: React.ComponentType<any>;
  rules?: any[];
}