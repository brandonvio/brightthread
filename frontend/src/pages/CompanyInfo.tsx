import React, { useState, useEffect } from 'react';
import { Box, Heading, VStack, HStack, Text, Spinner } from '@chakra-ui/react';
import type { Company } from '../types/models';
import { useAuth } from '../contexts/AuthContext';
import { getCompany } from '../api/companiesApi';

export const CompanyInfo: React.FC = () => {
  const { user } = useAuth();
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCompany = async (): Promise<void> => {
      if (!user?.company_id) {
        setError('No company associated with user');
        setLoading(false);
        return;
      }

      try {
        const data = await getCompany(user.company_id);
        setCompany(data);
      } catch {
        setError('Failed to load company information');
      } finally {
        setLoading(false);
      }
    };
    fetchCompany();
  }, [user?.company_id]);

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error || !company) {
    return <Text color="red.400">{error || 'Company not found'}</Text>;
  }

  return (
    <VStack align="stretch" gap={6}>
      <Heading>Company Information</Heading>

      <Box bg="gray.800" p={6} borderRadius="md">
        <VStack align="stretch" gap={4}>
          <HStack justify="space-between">
            <Text color="gray.400">Company Name:</Text>
            <Text fontWeight="bold">{company.name}</Text>
          </HStack>
          <HStack justify="space-between">
            <Text color="gray.400">Company ID:</Text>
            <Text fontFamily="mono">{company.id}</Text>
          </HStack>
          <HStack justify="space-between">
            <Text color="gray.400">Created:</Text>
            <Text>{new Date(company.created_at).toLocaleDateString()}</Text>
          </HStack>
        </VStack>
      </Box>
    </VStack>
  );
};
