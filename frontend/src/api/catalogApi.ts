import { get } from './client';
import type { Size, Color } from '../types/models';

export const getSizes = async (): Promise<Size[]> => {
  return get<Size[]>('/v1/catalog/sizes');
};

export const getColors = async (): Promise<Color[]> => {
  return get<Color[]>('/v1/catalog/colors');
};
