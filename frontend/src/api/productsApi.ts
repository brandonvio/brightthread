import { get } from './client';
import type { Product } from '../types/models';

export const getProducts = async (): Promise<Product[]> => {
  const response = await get<{ products: Product[] }>('/v1/products');
  return response.products;
};
