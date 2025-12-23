import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  VStack,
  HStack,
  Text,
  Spinner,
  SimpleGrid,
  Badge,
  Image,
  Flex,
} from '@chakra-ui/react';
import { getArtworks, updateArtwork } from '../api/artworksApi';
import type { Artwork } from '../types/models';

const getFileTypeColor = (fileType: string): string => {
  const colors: Record<string, string> = {
    'image/png': 'blue',
    'image/jpeg': 'green',
    'image/jpg': 'green',
    'image/svg+xml': 'purple',
    'application/pdf': 'red',
  };
  return colors[fileType] || 'gray';
};

const formatFileType = (fileType: string): string => {
  const types: Record<string, string> = {
    'image/png': 'PNG',
    'image/jpeg': 'JPEG',
    'image/jpg': 'JPEG',
    'image/svg+xml': 'SVG',
    'application/pdf': 'PDF',
  };
  return types[fileType] || fileType.split('/')[1]?.toUpperCase() || 'Unknown';
};

export const Artworks: React.FC = () => {
  const [artworks, setArtworks] = useState<Artwork[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchArtworks = async (): Promise<void> => {
      try {
        const data = await getArtworks();
        setArtworks(data);
      } catch {
        setError('Failed to load artworks');
      } finally {
        setLoading(false);
      }
    };
    fetchArtworks();
  }, []);

  const handleToggleActive = async (artwork: Artwork): Promise<void> => {
    try {
      const updated = await updateArtwork(artwork.id, { is_active: !artwork.is_active });
      setArtworks(prev => prev.map(a => a.id === artwork.id ? updated : a));
    } catch {
      setError('Failed to update artwork');
    }
  };

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

  const activeArtworks = artworks.filter(a => a.is_active);
  const inactiveArtworks = artworks.filter(a => !a.is_active);

  return (
    <VStack align="stretch" gap={6}>
      <Flex justify="space-between" align="center">
        <Heading color="white">Artworks</Heading>
        <HStack gap={4}>
          <Badge colorPalette="green" px={3} py={1}>
            {activeArtworks.length} Active
          </Badge>
          <Badge colorPalette="gray" px={3} py={1}>
            {inactiveArtworks.length} Inactive
          </Badge>
        </HStack>
      </Flex>

      {artworks.length === 0 ? (
        <Box textAlign="center" py={10}>
          <Text fontSize="4xl" mb={2}>🎨</Text>
          <Text color="gray.400">No artworks found.</Text>
          <Text color="gray.500" fontSize="sm" mt={2}>
            Upload artwork files to use them in your orders.
          </Text>
        </Box>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={6}>
          {artworks.map((artwork) => (
            <Box
              key={artwork.id}
              bg="gray.800"
              borderRadius="lg"
              overflow="hidden"
              border="1px solid"
              borderColor={artwork.is_active ? 'green.600' : 'gray.700'}
              _hover={{ borderColor: 'blue.500', transform: 'translateY(-2px)' }}
              transition="all 0.2s"
            >
              {/* Image Preview */}
              <Box
                bg="gray.900"
                h="160px"
                display="flex"
                alignItems="center"
                justifyContent="center"
                overflow="hidden"
              >
                {artwork.file_type.startsWith('image/') ? (
                  <Image
                    src={artwork.file_url}
                    alt={artwork.name}
                    maxH="160px"
                    maxW="100%"
                    objectFit="contain"
                  />
                ) : (
                  <VStack>
                    <Text fontSize="4xl">📄</Text>
                    <Text fontSize="sm" color="gray.500">
                      {formatFileType(artwork.file_type)}
                    </Text>
                  </VStack>
                )}
              </Box>

              {/* Details */}
              <Box p={4}>
                <VStack align="start" gap={3}>
                  <HStack justify="space-between" w="100%">
                    <Text fontWeight="bold" fontSize="lg" color="white" lineClamp={1}>
                      {artwork.name}
                    </Text>
                    <Badge
                      colorPalette={artwork.is_active ? 'green' : 'gray'}
                      cursor="pointer"
                      onClick={() => handleToggleActive(artwork)}
                      _hover={{ opacity: 0.8 }}
                    >
                      {artwork.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </HStack>

                  <HStack gap={3} wrap="wrap">
                    <Badge colorPalette={getFileTypeColor(artwork.file_type)} size="sm">
                      {formatFileType(artwork.file_type)}
                    </Badge>
                    <Text fontSize="xs" color="gray.400">
                      {artwork.width_px} × {artwork.height_px} px
                    </Text>
                  </HStack>

                  <Text fontSize="xs" color="gray.500" fontFamily="mono">
                    {artwork.id}
                  </Text>

                  <Text fontSize="xs" color="gray.500">
                    Uploaded {new Date(artwork.created_at).toLocaleDateString()}
                  </Text>
                </VStack>
              </Box>
            </Box>
          ))}
        </SimpleGrid>
      )}
    </VStack>
  );
};
