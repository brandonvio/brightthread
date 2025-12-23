import React, { type ReactNode } from 'react';
import { Box } from '@chakra-ui/react';
import { Navigation } from './Navigation';

interface LayoutProps {
  children: ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <Box minH="100vh" bg="gray.900">
      <Navigation />
      <Box p={8}>{children}</Box>
    </Box>
  );
};
