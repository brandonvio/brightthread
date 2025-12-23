export interface User {
  id: string;
  company_id: string;
  email: string;
  created_at: string;
}

export interface Company {
  id: string;
  name: string;
  created_at: string;
}

export interface ShippingAddress {
  id: string;
  created_by_user_id: string;
  label: string;
  street_address: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
  created_at: string;
}

export interface Product {
  id: string;
  supplier_id: string;
  sku: string;
  name: string;
  description: string | null;
  base_price: number;
  created_at: string;
}

export interface Size {
  id: string;
  name: string;
  code: string;
  sort_order: number;
}

export interface Color {
  id: string;
  name: string;
  hex_code: string;
}

export interface Inventory {
  id: string;
  product_id: string;
  color_id: string;
  size_id: string;
  available_qty: number;
  reserved_qty: number;
  updated_at: string;
}

export interface Artwork {
  id: string;
  uploaded_by_user_id: string;
  name: string;
  file_url: string;
  file_type: string;
  width_px: number;
  height_px: number;
  is_active: boolean;
  created_at: string;
}

export interface OrderLineItem {
  id: string;
  order_id: string;
  inventory_id: string;
  quantity: number;
  unit_price: number;
}

export interface EnrichedOrderLineItem {
  id: string;
  order_id: string;
  inventory_id: string;
  quantity: number;
  unit_price: number;
  product_name: string;
  product_sku: string;
  size: string;
  color: string;
  color_hex: string;
}

export interface Order {
  id: string;
  user_id: string;
  shipping_address_id: string;
  artwork_id: string | null;
  status: string;
  delivery_date: string;
  total_amount: number;
  created_at: string;
  updated_at: string;
  line_items?: EnrichedOrderLineItem[];
}

export interface EnrichedOrder {
  id: string;
  user_id: string;
  shipping_address_id: string;
  artwork_id: string | null;
  status: string;
  delivery_date: string;
  total_amount: number;
  created_at: string;
  updated_at: string;
  line_items: EnrichedOrderLineItem[];
  user_email: string;
  shipping_address: ShippingAddress;
  artwork: Artwork | null;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Conversation {
  session_id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface CreateOrderLineItemRequest {
  inventory_id: string;
  quantity: number;
}

export interface CreateOrderRequest {
  shipping_address_id: string;
  artwork_id?: string;
  delivery_date: string;
  line_items: CreateOrderLineItemRequest[];
}

export interface CreateShippingAddressRequest {
  label: string;
  street_address: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default?: boolean;
}

export interface CreateUserRequest {
  email: string;
  password: string;
  company_id: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface ChatCompletionRequest {
  model: string;
  messages: { role: string; content: string }[];
  session_id?: string;
}

export interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: { index: number; message: { role: string; content: string }; finish_reason: string }[];
  session_id: string;
}

export interface InventoryAvailabilityRequest {
  product_id: string;
  color_id: string;
  size_id: string;
  quantity: number;
}

export interface InventoryAvailabilityResponse {
  available: boolean;
  available_qty: number;
  reserved_qty: number;
}
