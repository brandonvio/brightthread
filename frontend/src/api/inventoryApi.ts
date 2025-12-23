import { get, post } from './client';
import type { Inventory, InventoryAvailabilityRequest, InventoryAvailabilityResponse } from '../types/models';

interface InventoryListResponse {
  inventory_items: Inventory[];
  total: number;
}

export const getInventory = async (): Promise<Inventory[]> => {
  const response = await get<InventoryListResponse>('/v1/inventory');
  return response.inventory_items;
};

export const getInventoryByProduct = async (productId: string): Promise<Inventory[]> => {
  const response = await get<InventoryListResponse>(`/v1/inventory/product/${productId}`);
  return response.inventory_items;
};

export const checkInventoryAvailability = async (
  data: InventoryAvailabilityRequest
): Promise<InventoryAvailabilityResponse> => {
  return post<InventoryAvailabilityResponse>('/v1/inventory/check-availability', data);
};
