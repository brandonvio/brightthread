import { get, post, patch, del } from './client';
import type { Order, EnrichedOrder, CreateOrderRequest } from '../types/models';

export const getOrders = async (): Promise<Order[]> => {
  const response = await get<{ orders: Order[] }>('/v1/orders');
  return response.orders;
};

export const getOrder = async (orderId: string): Promise<EnrichedOrder> => {
  return get<EnrichedOrder>(`/v1/orders/${orderId}`);
};

export const createOrder = async (data: CreateOrderRequest): Promise<Order> => {
  return post<Order>('/v1/orders', data);
};

export const updateOrder = async (orderId: string, data: Partial<Order>): Promise<Order> => {
  return patch<Order>(`/v1/orders/${orderId}`, data);
};

export const deleteOrder = async (orderId: string): Promise<void> => {
  await del(`/v1/orders/${orderId}`);
};
