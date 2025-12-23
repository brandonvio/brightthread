import type {
  User,
  Company,
  Order,
  Product,
  Inventory,
  ShippingAddress,
  Artwork,
  Conversation,
  ChatMessage,
} from './models';

export interface ApiResponse<T> {
  data: T;
  status: number;
}

export interface ApiError {
  message: string;
  status: number;
}

export interface LoginResponse {
  user: User;
  token: string;
}

export interface OrdersResponse {
  orders: Order[];
}

export interface ProductsResponse {
  products: Product[];
}

export interface InventoryResponse {
  inventory: Inventory[];
}

export interface ShippingAddressesResponse {
  addresses: ShippingAddress[];
}

export interface ArtworksResponse {
  artworks: Artwork[];
}

export interface UsersResponse {
  users: User[];
}

export interface CompanyResponse {
  company: Company;
}

export interface ConversationResponse {
  conversation: Conversation;
}

export interface ChatCompletionResponse {
  message: ChatMessage;
}

export interface InventoryCheckResponse {
  available: boolean;
  available_quantity: number;
}

export interface CatalogItem {
  value: string;
  label: string;
}

export interface CatalogResponse {
  items: CatalogItem[];
}
