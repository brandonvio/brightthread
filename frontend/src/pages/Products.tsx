import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  VStack,
  Text,
  Spinner,
  SimpleGrid,
} from '@chakra-ui/react';
import { getProducts } from '../api/productsApi';
import type { Product } from '../types/models';

export const Products: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProducts = async (): Promise<void> => {
      try {
        const data = await getProducts();
        setProducts(data);
      } catch {
        setError('Failed to load products');
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Text color="red.400">{error}</Text>
      </Box>
    );
  }

  return (
    <VStack align="stretch" gap={6}>
      <Heading color="white">Products</Heading>

      {products.length === 0 ? (
        <Text color="gray.400">No products found.</Text>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={6}>
          {products.map((product) => (
            <Box
              key={product.id}
              bg="gray.800"
              borderRadius="lg"
              p={6}
              border="1px solid"
              borderColor="gray.700"
              _hover={{ borderColor: 'blue.500', transform: 'translateY(-2px)' }}
              transition="all 0.2s"
            >
              <VStack align="start" gap={3}>
                <Text fontWeight="bold" fontSize="lg" color="white">
                  {product.name}
                </Text>
                <Text fontSize="sm" color="blue.300" fontFamily="mono">
                  SKU: {product.sku}
                </Text>
                {product.description && (
                  <Text fontSize="sm" color="gray.300">
                    {product.description}
                  </Text>
                )}
                <Text fontSize="2xl" fontWeight="bold" color="green.400">
                  ${product.base_price.toFixed(2)}
                </Text>
              </VStack>
            </Box>
          ))}
        </SimpleGrid>
      )}
    </VStack>
  );
};
