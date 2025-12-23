import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  VStack,
  HStack,
  Button,
  Input,
  Text,
  Spinner,
  Badge,
  SimpleGrid,
} from '@chakra-ui/react';
import type { ShippingAddress, CreateShippingAddressRequest } from '../types/models';
import {
  getShippingAddresses,
  createShippingAddress,
  setDefaultShippingAddress,
} from '../api/shippingApi';

export const ShippingAddresses: React.FC = () => {
  const [addresses, setAddresses] = useState<ShippingAddress[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState<CreateShippingAddressRequest>({
    label: '',
    street_address: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'USA',
    is_default: false,
  });

  const fetchAddresses = async (): Promise<void> => {
    try {
      const data = await getShippingAddresses();
      setAddresses(data);
    } catch {
      setError('Failed to load addresses');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAddresses();
  }, []);

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      await createShippingAddress(form);
      setShowForm(false);
      setForm({
        label: '',
        street_address: '',
        city: '',
        state: '',
        postal_code: '',
        country: 'USA',
        is_default: false,
      });
      await fetchAddresses();
    } catch {
      setError('Failed to create address');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSetDefault = async (addressId: string): Promise<void> => {
    try {
      await setDefaultShippingAddress(addressId);
      await fetchAddresses();
    } catch {
      setError('Failed to set default address');
    }
  };

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
      </Box>
    );
  }

  return (
    <VStack align="stretch" gap={6}>
      <HStack justify="space-between">
        <Heading color="white">Shipping Addresses</Heading>
        <Button
          bg={showForm ? 'gray.600' : 'blue.600'}
          color="white"
          _hover={{ bg: showForm ? 'gray.500' : 'blue.500' }}
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : 'Add Address'}
        </Button>
      </HStack>

      {error && <Text color="red.400">{error}</Text>}

      {showForm && (
        <Box bg="gray.800" p={6} borderRadius="lg" border="1px solid" borderColor="gray.700">
          <form onSubmit={handleSubmit}>
            <VStack gap={4}>
              <Input
                placeholder="Label (e.g., Main Office)"
                value={form.label}
                onChange={(e) => setForm({ ...form, label: e.target.value })}
                required
                bg="gray.700"
                color="white"
                borderColor="gray.600"
                _placeholder={{ color: 'gray.400' }}
              />
              <Input
                placeholder="Street Address"
                value={form.street_address}
                onChange={(e) => setForm({ ...form, street_address: e.target.value })}
                required
                bg="gray.700"
                color="white"
                borderColor="gray.600"
                _placeholder={{ color: 'gray.400' }}
              />
              <HStack gap={4} w="full">
                <Input
                  placeholder="City"
                  value={form.city}
                  onChange={(e) => setForm({ ...form, city: e.target.value })}
                  required
                  bg="gray.700"
                  color="white"
                  borderColor="gray.600"
                  _placeholder={{ color: 'gray.400' }}
                />
                <Input
                  placeholder="State"
                  value={form.state}
                  onChange={(e) => setForm({ ...form, state: e.target.value })}
                  required
                  bg="gray.700"
                  color="white"
                  borderColor="gray.600"
                  _placeholder={{ color: 'gray.400' }}
                />
              </HStack>
              <HStack gap={4} w="full">
                <Input
                  placeholder="Postal Code"
                  value={form.postal_code}
                  onChange={(e) => setForm({ ...form, postal_code: e.target.value })}
                  required
                  bg="gray.700"
                  color="white"
                  borderColor="gray.600"
                  _placeholder={{ color: 'gray.400' }}
                />
                <Input
                  placeholder="Country"
                  value={form.country}
                  onChange={(e) => setForm({ ...form, country: e.target.value })}
                  required
                  bg="gray.700"
                  color="white"
                  borderColor="gray.600"
                  _placeholder={{ color: 'gray.400' }}
                />
              </HStack>
              <Button
                type="submit"
                bg="blue.600"
                color="white"
                _hover={{ bg: 'blue.500' }}
                loading={submitting}
                w="full"
              >
                Save Address
              </Button>
            </VStack>
          </form>
        </Box>
      )}

      {addresses.length === 0 ? (
        <Text color="gray.400">No shipping addresses. Add your first address!</Text>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2 }} gap={6}>
          {addresses.map((addr) => (
            <Box
              key={addr.id}
              bg="gray.800"
              p={5}
              borderRadius="lg"
              border="1px solid"
              borderColor={addr.is_default ? 'green.500' : 'gray.700'}
            >
              <HStack justify="space-between" mb={3}>
                <Text fontWeight="bold" color="white" fontSize="lg">{addr.label}</Text>
                {addr.is_default && (
                  <Badge colorPalette="green">Default</Badge>
                )}
              </HStack>
              <Text color="gray.300">{addr.street_address}</Text>
              <Text color="gray.300">
                {addr.city}, {addr.state} {addr.postal_code}
              </Text>
              <Text color="gray.400">{addr.country}</Text>
              {!addr.is_default && (
                <Button
                  size="sm"
                  bg="gray.700"
                  color="white"
                  _hover={{ bg: 'gray.600' }}
                  mt={4}
                  onClick={() => handleSetDefault(addr.id)}
                >
                  Set as Default
                </Button>
              )}
            </Box>
          ))}
        </SimpleGrid>
      )}
    </VStack>
  );
};
