import React from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { Box, Flex, Button, HStack, Heading } from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/orders', label: 'Orders' },
  { to: '/shipping', label: 'Shipping' },
  { to: '/artworks', label: 'Artworks' },
  { to: '/company', label: 'Company' },
  { to: '/products', label: 'Products' },
  { to: '/users', label: 'Users' },
];

export const Navigation: React.FC = () => {
  const { logout, user } = useAuth();
  const location = useLocation();

  return (
    <Box bg="gray.800" px={4} py={3} borderBottom="1px" borderColor="gray.700">
      <Flex justify="space-between" align="center">
        <HStack gap={8}>
          <Heading size="md" color="white">BrightThread</Heading>
          <HStack gap={2}>
            {navItems.map((item) => {
              const isActive = location.pathname === item.to ||
                (item.to === '/orders' && location.pathname.startsWith('/orders'));
              return (
                <RouterLink key={item.to} to={item.to}>
                  <Button
                    size="sm"
                    bg={isActive ? 'blue.600' : 'transparent'}
                    color="white"
                    _hover={{ bg: isActive ? 'blue.500' : 'gray.700' }}
                  >
                    {item.label}
                  </Button>
                </RouterLink>
              );
            })}
          </HStack>
        </HStack>
        <HStack gap={4}>
          <Box color="gray.300" fontSize="sm">
            {user?.email}
          </Box>
          <Button onClick={logout} bg="gray.700" color="white" size="sm" _hover={{ bg: 'gray.600' }}>
            Logout
          </Button>
        </HStack>
      </Flex>
    </Box>
  );
};
