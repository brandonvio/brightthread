import { get } from './client';
import type { Company } from '../types/models';

interface CompanyListResponse {
  companies: Company[];
  total: number;
}

export const getCompanies = async (): Promise<Company[]> => {
  const response = await get<CompanyListResponse>('/v1/companies');
  return response.companies;
};

export const getCompany = async (companyId: string): Promise<Company> => {
  return get<Company>(`/v1/companies/${companyId}`);
};
