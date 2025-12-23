import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Heading,
  VStack,
  HStack,
  Button,
  Text,
  Badge,
  Spinner,
} from '@chakra-ui/react';
import type { Order } from '../types/models';
import { getOrders } from '../api/ordersApi';

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

export const Orders: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchOrders = async (): Promise<void> => {
      try {
        const data = await getOrders();
        setOrders(data);
      } catch {
        setError('Failed to load orders');
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
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
      <HStack justify="space-between">
        <Heading color="white">Orders</Heading>
        <RouterLink to="/orders/new">
          <Button bg="blue.600" color="white" _hover={{ bg: 'blue.500' }}>
            Create Order
          </Button>
        </RouterLink>
      </HStack>

      {orders.length === 0 ? (
        <Text color="gray.400">No orders found. Create your first order!</Text>
      ) : (
        <Box bg="gray.800" borderRadius="lg" overflow="hidden">
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#2D3748' }}>
                <th style={{ padding: '16px', textAlign: 'left', color: '#E2E8F0', fontWeight: 600, borderBottom: '1px solid #4A5568' }}>Order ID</th>
                <th style={{ padding: '16px', textAlign: 'left', color: '#E2E8F0', fontWeight: 600, borderBottom: '1px solid #4A5568' }}>Status</th>
                <th style={{ padding: '16px', textAlign: 'left', color: '#E2E8F0', fontWeight: 600, borderBottom: '1px solid #4A5568' }}>Delivery Date</th>
                <th style={{ padding: '16px', textAlign: 'right', color: '#E2E8F0', fontWeight: 600, borderBottom: '1px solid #4A5568' }}>Total</th>
                <th style={{ padding: '16px', textAlign: 'left', color: '#E2E8F0', fontWeight: 600, borderBottom: '1px solid #4A5568' }}>Created</th>
                <th style={{ padding: '16px', textAlign: 'center', color: '#E2E8F0', fontWeight: 600, borderBottom: '1px solid #4A5568' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order, index) => (
                <tr
                  key={order.id}
                  style={{
                    backgroundColor: index % 2 === 0 ? '#1A202C' : '#2D3748',
                    borderBottom: '1px solid #4A5568'
                  }}
                >
                  <td style={{ padding: '16px', color: '#A0AEC0', fontFamily: 'monospace', fontSize: '14px' }}>
                    {order.id}
                  </td>
                  <td style={{ padding: '16px' }}>
                    <Badge colorPalette={getStatusColor(order.status)}>
                      {order.status}
                    </Badge>
                  </td>
                  <td style={{ padding: '16px', color: '#E2E8F0' }}>
                    {order.delivery_date}
                  </td>
                  <td style={{ padding: '16px', color: '#68D391', fontWeight: 600, textAlign: 'right' }}>
                    ${order.total_amount.toFixed(2)}
                  </td>
                  <td style={{ padding: '16px', color: '#A0AEC0' }}>
                    {new Date(order.created_at).toLocaleDateString()}
                  </td>
                  <td style={{ padding: '16px', textAlign: 'center' }}>
                    <RouterLink to={`/orders/${order.id}`}>
                      <Button
                        size="sm"
                        bg="blue.600"
                        color="white"
                        _hover={{ bg: 'blue.500' }}
                      >
                        View
                      </Button>
                    </RouterLink>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Box>
      )}
    </VStack>
  );
};
