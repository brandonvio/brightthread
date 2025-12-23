import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  SimpleGrid,
  Badge,
  Spinner,
  Flex,
} from '@chakra-ui/react';
import { keyframes } from '@emotion/react';
import { useAuth } from '../contexts/AuthContext';
import { getOrders } from '../api/ordersApi';
import { getShippingAddresses } from '../api/shippingApi';
import { getProducts } from '../api/productsApi';
import { getArtworks } from '../api/artworksApi';
import type { Order, ShippingAddress, Product, Artwork } from '../types/models';

const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    CREATED: 'blue',
    APPROVED: 'green',
    IN_PRODUCTION: 'orange',
    READY_TO_SHIP: 'purple',
    SHIPPED: 'teal',
    CANCELLED: 'red',
  };
  return colors[status] || 'gray';
};

interface StatCardProps {
  label: string;
  value: number | string;
  icon: string;
  color: string;
  delay: number;
}

const StatCard: React.FC<StatCardProps> = ({ label, value, icon, color, delay }) => (
  <Box
    bg="gray.800"
    p={5}
    borderRadius="xl"
    borderLeft="4px solid"
    borderColor={`${color}.500`}
    animation={`${fadeInUp} 0.5s ease-out ${delay}s both`}
    _hover={{
      transform: 'translateY(-4px)',
      boxShadow: `0 8px 25px -5px var(--chakra-colors-${color}-500)`,
    }}
    transition="all 0.3s ease"
    cursor="default"
  >
    <HStack justify="space-between">
      <VStack align="start" gap={1}>
        <Text color="gray.400" fontSize="sm" fontWeight="medium">
          {label}
        </Text>
        <Text fontSize="3xl" fontWeight="bold" color="white">
          {value}
        </Text>
      </VStack>
      <Box
        fontSize="3xl"
        opacity={0.8}
        bg={`${color}.900`}
        p={3}
        borderRadius="lg"
      >
        {icon}
      </Box>
    </HStack>
  </Box>
);

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState<Order[]>([]);
  const [addresses, setAddresses] = useState<ShippingAddress[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [artworks, setArtworks] = useState<Artwork[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ordersData, addressesData, productsData, artworksData] = await Promise.all([
          getOrders().catch(() => []),
          getShippingAddresses().catch(() => []),
          getProducts().catch(() => []),
          getArtworks().catch(() => []),
        ]);
        setOrders(ordersData);
        setAddresses(addressesData);
        setProducts(productsData);
        setArtworks(artworksData);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <Flex justify="center" align="center" minH="400px">
        <Spinner size="xl" color="blue.400" />
      </Flex>
    );
  }

  const openOrders = orders.filter(o => !['SHIPPED', 'CANCELLED'].includes(o.status));
  const shippedOrders = orders.filter(o => o.status === 'SHIPPED');
  const recentOrders = [...orders].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ).slice(0, 5);

  const totalSpend = orders.reduce((sum, o) => sum + o.total_amount, 0);

  return (
    <VStack align="stretch" gap={8}>
      {/* Welcome Header */}
      <Box animation={`${fadeInUp} 0.4s ease-out`}>
        <Heading size="xl" color="white" mb={2}>
          Welcome back, {user?.email?.split('@')[0]}!
        </Heading>
        <Text color="gray.400">
          Here's what's happening with your orders today.
        </Text>
      </Box>

      {/* Stats Grid */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} gap={5}>
        <StatCard
          label="Total Orders"
          value={orders.length}
          icon="📦"
          color="blue"
          delay={0}
        />
        <StatCard
          label="Open Orders"
          value={openOrders.length}
          icon="⏳"
          color="orange"
          delay={0.1}
        />
        <StatCard
          label="Shipped"
          value={shippedOrders.length}
          icon="✈️"
          color="green"
          delay={0.2}
        />
        <StatCard
          label="Total Spend"
          value={`$${totalSpend.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
          icon="💳"
          color="purple"
          delay={0.3}
        />
      </SimpleGrid>

      {/* Recent Orders - Full Width */}
      <Box
        bg="gray.800"
        borderRadius="xl"
        p={5}
        animation={`${fadeInUp} 0.5s ease-out 0.2s both`}
      >
        <HStack justify="space-between" mb={4}>
          <Heading size="md" color="white">Recent Orders</Heading>
          <Text
            color="blue.400"
            fontSize="sm"
            cursor="pointer"
            _hover={{ textDecoration: 'underline' }}
            onClick={() => navigate('/orders')}
          >
            View all →
          </Text>
        </HStack>
        
          {recentOrders.length === 0 ? (
            <Box textAlign="center" py={8}>
              <Text fontSize="4xl" mb={2}>📭</Text>
              <Text color="gray.500">No orders yet</Text>
              <Text
                color="blue.400"
                fontSize="sm"
                mt={2}
                cursor="pointer"
                _hover={{ textDecoration: 'underline' }}
                onClick={() => navigate('/orders')}
              >
                Create your first order
              </Text>
            </Box>
          ) : (
            <VStack align="stretch" gap={3}>
              {recentOrders.map((order, idx) => (
                <Box
                  key={order.id}
                  p={4}
                  bg="gray.900"
                  borderRadius="lg"
                  cursor="pointer"
                  onClick={() => navigate(`/orders/${order.id}`)}
                  _hover={{ bg: 'gray.700', transform: 'translateX(4px)' }}
                  transition="all 0.2s ease"
                  animation={`${fadeInUp} 0.3s ease-out ${0.3 + idx * 0.05}s both`}
                >
                  <Flex justify="space-between" align="center" wrap="wrap" gap={3} mb={2}>
                    <HStack gap={4}>
                      <Text fontFamily="mono" fontSize="sm" color="blue.300">
                        {order.id}
                      </Text>
                      <Text fontSize="sm" color="gray.500">
                        {new Date(order.created_at).toLocaleDateString()}
                      </Text>
                    </HStack>
                    <HStack gap={4}>
                      <Text fontWeight="bold" color="green.400">
                        ${order.total_amount.toFixed(2)}
                      </Text>
                      <Badge colorPalette={getStatusColor(order.status)} size="sm">
                        {order.status}
                      </Badge>
                    </HStack>
                  </Flex>
                  {order.line_items && order.line_items.length > 0 && (
                    <Flex gap={2} flexWrap="wrap" mt={2}>
                      {order.line_items.slice(0, 3).map((item) => (
                        <HStack
                          key={item.id}
                          bg="gray.800"
                          px={2}
                          py={1}
                          borderRadius="md"
                          gap={2}
                        >
                          <Box
                            w="10px"
                            h="10px"
                            borderRadius="full"
                            bg={item.color_hex}
                            border="1px solid"
                            borderColor="gray.600"
                          />
                          <Text fontSize="xs" color="gray.300">
                            {item.product_name}
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            {item.size}
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            ×{item.quantity}
                          </Text>
                        </HStack>
                      ))}
                      {order.line_items.length > 3 && (
                        <Text fontSize="xs" color="gray.500" alignSelf="center">
                          +{order.line_items.length - 3} more
                        </Text>
                      )}
                    </Flex>
                  )}
                </Box>
              ))}
            </VStack>
          )}
      </Box>

      {/* Three Section Grid */}
      <SimpleGrid columns={{ base: 1, lg: 3 }} gap={6}>
        {/* Shipping Addresses */}
        <Box
          bg="gray.800"
          borderRadius="xl"
          p={5}
          animation={`${fadeInUp} 0.5s ease-out 0.3s both`}
        >
          <HStack justify="space-between" mb={4}>
            <Heading size="md" color="white">Shipping Addresses</Heading>
            <Text
              color="blue.400"
              fontSize="sm"
              cursor="pointer"
              _hover={{ textDecoration: 'underline' }}
              onClick={() => navigate('/shipping')}
            >
              Manage →
            </Text>
          </HStack>
          
          {addresses.length === 0 ? (
            <Box textAlign="center" py={8}>
              <Text fontSize="4xl" mb={2}>🏠</Text>
              <Text color="gray.500">No addresses saved</Text>
              <Text
                color="blue.400"
                fontSize="sm"
                mt={2}
                cursor="pointer"
                _hover={{ textDecoration: 'underline' }}
                onClick={() => navigate('/shipping')}
              >
                Add an address
              </Text>
            </Box>
          ) : (
            <VStack align="stretch" gap={3}>
              {addresses.slice(0, 3).map((addr, idx) => (
                <Box
                  key={addr.id}
                  p={3}
                  bg="gray.900"
                  borderRadius="lg"
                  borderLeft="3px solid"
                  borderColor={addr.is_default ? 'blue.400' : 'transparent'}
                  animation={`${fadeInUp} 0.3s ease-out ${0.4 + idx * 0.05}s both`}
                >
                  <HStack justify="space-between" align="start">
                    <VStack align="start" gap={0}>
                      <HStack gap={2}>
                        <Text fontWeight="bold" color="white" fontSize="sm">
                          {addr.label}
                        </Text>
                        {addr.is_default && (
                          <Badge colorPalette="blue" size="sm">Default</Badge>
                        )}
                      </HStack>
                      <Text fontSize="xs" color="gray.400">
                        {addr.street_address}
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        {addr.city}, {addr.state} {addr.postal_code}
                      </Text>
                    </VStack>
                    <Text fontSize="lg">📍</Text>
                  </HStack>
                </Box>
              ))}
              {addresses.length > 3 && (
                <Text fontSize="sm" color="gray.500" textAlign="center">
                  +{addresses.length - 3} more addresses
                </Text>
              )}
            </VStack>
          )}
        </Box>

        {/* Products Catalog */}
        <Box
          bg="gray.800"
          borderRadius="xl"
          p={5}
          animation={`${fadeInUp} 0.5s ease-out 0.4s both`}
        >
          <HStack justify="space-between" mb={4}>
            <Heading size="md" color="white">Product Catalog</Heading>
            <Text
              color="blue.400"
              fontSize="sm"
              cursor="pointer"
              _hover={{ textDecoration: 'underline' }}
              onClick={() => navigate('/products')}
            >
              Browse all →
            </Text>
          </HStack>

          {products.length === 0 ? (
            <Box textAlign="center" py={8}>
              <Text fontSize="4xl" mb={2}>👕</Text>
              <Text color="gray.500">No products available</Text>
            </Box>
          ) : (
            <SimpleGrid columns={2} gap={3}>
              {products.slice(0, 4).map((product, idx) => (
                <Box
                  key={product.id}
                  p={3}
                  bg="gray.900"
                  borderRadius="lg"
                  cursor="pointer"
                  onClick={() => navigate('/products')}
                  _hover={{ bg: 'gray.700' }}
                  transition="all 0.2s ease"
                  animation={`${fadeInUp} 0.3s ease-out ${0.5 + idx * 0.05}s both`}
                >
                  <VStack align="start" gap={1}>
                    <Text fontSize="2xl">👕</Text>
                    <Text fontWeight="bold" color="white" fontSize="sm" lineClamp={1}>
                      {product.name}
                    </Text>
                    <Text fontFamily="mono" fontSize="xs" color="gray.500">
                      {product.sku}
                    </Text>
                    <Text fontWeight="bold" color="green.400" fontSize="sm">
                      ${product.base_price.toFixed(2)}
                    </Text>
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          )}
        </Box>

        {/* Artworks */}
        <Box
          bg="gray.800"
          borderRadius="xl"
          p={5}
          animation={`${fadeInUp} 0.5s ease-out 0.45s both`}
        >
          <HStack justify="space-between" mb={4}>
            <Heading size="md" color="white">Artworks</Heading>
            <Text
              color="blue.400"
              fontSize="sm"
              cursor="pointer"
              _hover={{ textDecoration: 'underline' }}
              onClick={() => navigate('/artworks')}
            >
              View all →
            </Text>
          </HStack>

          {artworks.length === 0 ? (
            <Box textAlign="center" py={8}>
              <Text fontSize="4xl" mb={2}>🎨</Text>
              <Text color="gray.500">No artworks uploaded</Text>
              <Text
                color="blue.400"
                fontSize="sm"
                mt={2}
                cursor="pointer"
                _hover={{ textDecoration: 'underline' }}
                onClick={() => navigate('/artworks')}
              >
                Upload artwork
              </Text>
            </Box>
          ) : (
            <VStack align="stretch" gap={3}>
              {artworks.filter(a => a.is_active).slice(0, 3).map((artwork, idx) => (
                <Box
                  key={artwork.id}
                  p={3}
                  bg="gray.900"
                  borderRadius="lg"
                  cursor="pointer"
                  onClick={() => navigate('/artworks')}
                  _hover={{ bg: 'gray.700' }}
                  transition="all 0.2s ease"
                  animation={`${fadeInUp} 0.3s ease-out ${0.55 + idx * 0.05}s both`}
                >
                  <HStack gap={3}>
                    <Box
                      w="40px"
                      h="40px"
                      bg="gray.800"
                      borderRadius="md"
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      overflow="hidden"
                    >
                      {artwork.file_type.startsWith('image/') ? (
                        <img
                          src={artwork.file_url}
                          alt={artwork.name}
                          style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
                        />
                      ) : (
                        <Text fontSize="lg">📄</Text>
                      )}
                    </Box>
                    <VStack align="start" gap={0} flex={1}>
                      <Text fontWeight="bold" color="white" fontSize="sm" lineClamp={1}>
                        {artwork.name}
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        {artwork.width_px} × {artwork.height_px} px
                      </Text>
                    </VStack>
                    <Badge colorPalette="green" size="sm">Active</Badge>
                  </HStack>
                </Box>
              ))}
              {artworks.filter(a => a.is_active).length > 3 && (
                <Text fontSize="sm" color="gray.500" textAlign="center">
                  +{artworks.filter(a => a.is_active).length - 3} more artworks
                </Text>
              )}
            </VStack>
          )}
        </Box>
      </SimpleGrid>

      {/* Quick Actions */}
      <SimpleGrid columns={{ base: 2, md: 5 }} gap={4} animation={`${fadeInUp} 0.5s ease-out 0.5s both`}>
        {[
          { label: 'New Order', icon: '➕', path: '/orders', color: 'blue' },
          { label: 'View Products', icon: '📦', path: '/products', color: 'purple' },
          { label: 'Artworks', icon: '🎨', path: '/artworks', color: 'pink' },
          { label: 'Shipping', icon: '🚚', path: '/shipping', color: 'green' },
          { label: 'Company', icon: '🏢', path: '/company', color: 'orange' },
        ].map((action) => (
          <Box
            key={action.label}
            bg="gray.800"
            p={4}
            borderRadius="xl"
            cursor="pointer"
            onClick={() => navigate(action.path)}
            _hover={{
              bg: `${action.color}.900`,
              transform: 'translateY(-2px)',
            }}
            transition="all 0.2s ease"
            textAlign="center"
          >
            <Text fontSize="2xl" mb={2}>{action.icon}</Text>
            <Text fontWeight="medium" color="white" fontSize="sm">
              {action.label}
            </Text>
          </Box>
        ))}
      </SimpleGrid>
    </VStack>
  );
};
