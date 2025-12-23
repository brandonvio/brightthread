import { get, post, patch } from './client';
import type { ShippingAddress, CreateShippingAddressRequest } from '../types/models';

interface ShippingAddressListResponse {
  addresses: ShippingAddress[];
  total: number;
}

export const getShippingAddresses = async (): Promise<ShippingAddress[]> => {
  const response = await get<ShippingAddressListResponse>('/v1/shipping');
  return response.addresses;
};

export const getDefaultShippingAddress = async (): Promise<ShippingAddress> => {
  return get<ShippingAddress>('/v1/shipping/default');
};

export const createShippingAddress = async (
  data: CreateShippingAddressRequest
): Promise<ShippingAddress> => {
  return post<ShippingAddress>('/v1/shipping', data);
};

export const setDefaultShippingAddress = async (addressId: string): Promise<ShippingAddress> => {
  return patch<ShippingAddress>(`/v1/shipping/${addressId}/set-default`, {});
};
