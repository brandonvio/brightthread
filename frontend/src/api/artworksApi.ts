import { get, post, patch } from './client';
import type { Artwork } from '../types/models';

export const getArtworks = async (): Promise<Artwork[]> => {
  const response = await get<{ artworks: Artwork[] }>('/v1/artworks');
  return response.artworks;
};

export const getActiveArtworks = async (): Promise<Artwork[]> => {
  const response = await get<{ artworks: Artwork[] }>('/v1/artworks/active');
  return response.artworks;
};

export const getArtwork = async (artworkId: string): Promise<Artwork> => {
  const response = await get<Artwork>(`/v1/artworks/${artworkId}`);
  return response;
};

export interface UploadArtworkRequest {
  name: string;
  file_url: string;
  file_type: string;
  width_px: number;
  height_px: number;
}

export const uploadArtwork = async (data: UploadArtworkRequest): Promise<Artwork> => {
  const response = await post<Artwork>('/v1/artworks', data);
  return response;
};

export interface UpdateArtworkRequest {
  name?: string;
  is_active?: boolean;
}

export const updateArtwork = async (
  artworkId: string,
  data: UpdateArtworkRequest
): Promise<Artwork> => {
  const response = await patch<Artwork>(`/v1/artworks/${artworkId}`, data);
  return response;
};
