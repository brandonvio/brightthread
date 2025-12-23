import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Input,
  VStack,
  Heading,
  Text,
  Container,
} from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxW="md" py={20}>
      <VStack gap={8}>
        <Heading size="2xl">BrightThread</Heading>
        <Box w="full" bg="gray.800" p={8} borderRadius="lg">
          <form onSubmit={handleSubmit}>
            <VStack gap={4}>
              <Heading size="lg">Login</Heading>
              {error && (
                <Text color="red.400" fontSize="sm">
                  {error}
                </Text>
              )}
              <Input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                bg="gray.700"
              />
              <Input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                bg="gray.700"
              />
              <Button
                type="submit"
                colorScheme="blue"
                width="full"
                loading={loading}
              >
                Login
              </Button>
            </VStack>
          </form>
        </Box>
      </VStack>
    </Container>
  );
};
