import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  VStack,
  HStack,
  Text,
  Button,
  Input,
  Spinner,
} from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';
import { getUsersByCompany, createUser } from '../api/usersApi';
import type { User, CreateUserRequest } from '../types/models';

export const Users: React.FC = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ email: '', password: '' });

  const fetchUsers = async (): Promise<void> => {
    if (!currentUser?.company_id) return;
    try {
      const data = await getUsersByCompany(currentUser.company_id);
      setUsers(data);
    } catch {
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [currentUser?.company_id]);

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    if (!currentUser?.company_id) return;

    const request: CreateUserRequest = {
      email: formData.email,
      password: formData.password,
      company_id: currentUser.company_id,
    };

    try {
      await createUser(request);
      setShowForm(false);
      setFormData({ email: '', password: '' });
      await fetchUsers();
    } catch {
      setError('Failed to create user');
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
        <Heading color="white">Users</Heading>
        <Button
          bg={showForm ? 'gray.600' : 'blue.600'}
          color="white"
          _hover={{ bg: showForm ? 'gray.500' : 'blue.500' }}
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : 'Add User'}
        </Button>
      </HStack>

      {error && <Text color="red.400">{error}</Text>}

      {showForm && (
        <Box bg="gray.800" p={6} borderRadius="lg">
          <form onSubmit={handleSubmit}>
            <VStack gap={4}>
              <Input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
                bg="gray.700"
                color="white"
                borderColor="gray.600"
                _placeholder={{ color: 'gray.400' }}
              />
              <Input
                type="password"
                placeholder="Password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                bg="gray.700"
                color="white"
                borderColor="gray.600"
                _placeholder={{ color: 'gray.400' }}
              />
              <Button type="submit" bg="blue.600" color="white" _hover={{ bg: 'blue.500' }} w="full">
                Create User
              </Button>
            </VStack>
          </form>
        </Box>
      )}

      {users.length === 0 ? (
        <Text color="gray.400">No users found.</Text>
      ) : (
        <Box bg="gray.800" borderRadius="lg" overflow="hidden">
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#2D3748' }}>
                <th style={{ padding: '16px', textAlign: 'left', color: '#E2E8F0', fontWeight: 600, borderBottom: '1px solid #4A5568' }}>Email</th>
                <th style={{ padding: '16px', textAlign: 'left', color: '#E2E8F0', fontWeight: 600, borderBottom: '1px solid #4A5568' }}>Created</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user, index) => (
                <tr
                  key={user.id}
                  style={{
                    backgroundColor: index % 2 === 0 ? '#1A202C' : '#2D3748',
                    borderBottom: '1px solid #4A5568'
                  }}
                >
                  <td style={{ padding: '16px', color: '#E2E8F0' }}>
                    {user.email}
                  </td>
                  <td style={{ padding: '16px', color: '#A0AEC0' }}>
                    {new Date(user.created_at).toLocaleDateString()}
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
