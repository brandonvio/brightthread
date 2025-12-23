import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Heading,
  VStack,
  HStack,
  Button,
  Input,
  Text,
  Spinner,
  NativeSelect,
  IconButton,
  SimpleGrid,
  Flex,
} from '@chakra-ui/react';
import type {
  ShippingAddress,
  Product,
  Size,
  Color,
  Inventory,
  Artwork,
  CreateOrderLineItemRequest,
} from '../types/models';
import { getShippingAddresses } from '../api/shippingApi';
import { getProducts } from '../api/productsApi';
import { getSizes, getColors } from '../api/catalogApi';
import { getInventoryByProduct } from '../api/inventoryApi';
import { getActiveArtworks } from '../api/artworksApi';
import { createOrder } from '../api/ordersApi';

interface LineItemForm {
  product_id: string;
  size_id: string;
  color_id: string;
  quantity: number;
  inventory_id: string;
}

export const CreateOrder: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [addresses, setAddresses] = useState<ShippingAddress[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [sizes, setSizes] = useState<Size[]>([]);
  const [colors, setColors] = useState<Color[]>([]);
  const [artworks, setArtworks] = useState<Artwork[]>([]);
  const [inventoryMap, setInventoryMap] = useState<Record<string, Inventory[]>>({});

  const [shippingAddressId, setShippingAddressId] = useState('');
  const [artworkId, setArtworkId] = useState('');
  const [deliveryDate, setDeliveryDate] = useState('');
  const [lineItems, setLineItems] = useState<LineItemForm[]>([
    { product_id: '', size_id: '', color_id: '', quantity: 10, inventory_id: '' },
  ]);

  useEffect(() => {
    const fetchData = async (): Promise<void> => {
      try {
        const [addressData, productData, sizeData, colorData, artworkData] = await Promise.all([
          getShippingAddresses(),
          getProducts(),
          getSizes(),
          getColors(),
          getActiveArtworks(),
        ]);
        setAddresses(addressData);
        setProducts(productData);
        setSizes(sizeData);
        setColors(colorData);
        setArtworks(artworkData);

        if (addressData.length > 0) {
          const defaultAddr = addressData.find((a) => a.is_default) || addressData[0];
          setShippingAddressId(defaultAddr.id);
        }

        // Set default delivery date to 14 days from now
        const defaultDate = new Date();
        defaultDate.setDate(defaultDate.getDate() + 14);
        setDeliveryDate(defaultDate.toISOString().split('T')[0]);
      } catch {
        setError('Failed to load form data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleProductChange = async (index: number, productId: string): Promise<void> => {
    const newItems = [...lineItems];
    newItems[index] = { ...newItems[index], product_id: productId, inventory_id: '' };
    setLineItems(newItems);

    if (productId && !inventoryMap[productId]) {
      const inventory = await getInventoryByProduct(productId);
      setInventoryMap((prev) => ({ ...prev, [productId]: inventory }));
    }
  };

  const findInventoryId = (item: LineItemForm): string => {
    const productInventory = inventoryMap[item.product_id] || [];
    const match = productInventory.find(
      (inv) => inv.size_id === item.size_id && inv.color_id === item.color_id
    );
    return match?.id || '';
  };

  const updateLineItem = (index: number, field: keyof LineItemForm, value: string | number): void => {
    const newItems = [...lineItems];
    newItems[index] = { ...newItems[index], [field]: value };
    if (field === 'size_id' || field === 'color_id') {
      newItems[index].inventory_id = findInventoryId(newItems[index]);
    }
    setLineItems(newItems);
  };

  const addLineItem = (): void => {
    setLineItems([...lineItems, { product_id: '', size_id: '', color_id: '', quantity: 10, inventory_id: '' }]);
  };

  const removeLineItem = (index: number): void => {
    if (lineItems.length > 1) {
      setLineItems(lineItems.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const validLineItems: CreateOrderLineItemRequest[] = lineItems
        .filter((item) => item.inventory_id && item.quantity > 0)
        .map((item) => ({
          inventory_id: item.inventory_id,
          quantity: item.quantity,
        }));

      if (validLineItems.length === 0) {
        setError('Please add at least one valid line item with product, size, and color selected');
        setSubmitting(false);
        return;
      }

      const order = await createOrder({
        shipping_address_id: shippingAddressId,
        artwork_id: artworkId || undefined,
        delivery_date: deliveryDate,
        line_items: validLineItems,
      });

      navigate(`/orders/${order.id}`);
    } catch {
      setError('Failed to create order. Ensure minimum order quantity is 10 items.');
    } finally {
      setSubmitting(false);
    }
  };

  const getSelectedProduct = (productId: string) => products.find(p => p.id === productId);
  const getSelectedColor = (colorId: string) => colors.find(c => c.id === colorId);

  const calculateTotal = () => {
    return lineItems.reduce((sum, item) => {
      const product = getSelectedProduct(item.product_id);
      if (product && item.quantity > 0) {
        return sum + (product.base_price * item.quantity);
      }
      return sum;
    }, 0);
  };

  const getTotalQuantity = () => {
    return lineItems.reduce((sum, item) => sum + (item.quantity || 0), 0);
  };

  if (loading) {
    return (
      <Flex justify="center" align="center" minH="400px">
        <Spinner size="xl" color="blue.400" />
      </Flex>
    );
  }

  return (
    <Box maxW="1000px" mx="auto">
      <VStack align="stretch" gap={6}>
        {/* Header */}
        <HStack justify="space-between" align="center">
          <Box>
            <Heading size="xl" color="white" mb={1}>Create Order</Heading>
            <Text color="gray.400">Fill in the details below to place a new order</Text>
          </Box>
          <Button variant="ghost" color="gray.400" onClick={() => navigate('/orders')}>
            ← Back to Orders
          </Button>
        </HStack>

        {error && (
          <Box bg="red.900" border="1px solid" borderColor="red.600" p={4} borderRadius="lg">
            <Text color="red.200">{error}</Text>
          </Box>
        )}

        <Box as="form" onSubmit={handleSubmit}>
          <SimpleGrid columns={{ base: 1, lg: 2 }} gap={6}>
            {/* Left Column - Order Details */}
            <VStack align="stretch" gap={5}>
              {/* Shipping Section */}
              <Box bg="gray.800" p={5} borderRadius="xl">
                <Heading size="sm" color="white" mb={4}>📦 Shipping Details</Heading>

                <VStack align="stretch" gap={4}>
                  <Box>
                    <Text mb={2} fontSize="sm" color="gray.400" fontWeight="medium">
                      Delivery Address
                    </Text>
                    <NativeSelect.Root size="lg">
                      <NativeSelect.Field
                        value={shippingAddressId}
                        onChange={(e) => setShippingAddressId(e.target.value)}
                        required
                        bg="gray.700"
                        borderColor="gray.600"
                      >
                        <option value="">Select address...</option>
                        {addresses.map((addr) => (
                          <option key={addr.id} value={addr.id}>
                            {addr.label} - {addr.street_address}, {addr.city}
                          </option>
                        ))}
                      </NativeSelect.Field>
                    </NativeSelect.Root>
                  </Box>

                  <Box>
                    <Text mb={2} fontSize="sm" color="gray.400" fontWeight="medium">
                      Requested Delivery Date
                    </Text>
                    <Input
                      type="date"
                      size="lg"
                      value={deliveryDate}
                      onChange={(e) => setDeliveryDate(e.target.value)}
                      required
                      bg="gray.700"
                      borderColor="gray.600"
                    />
                    <Text fontSize="xs" color="gray.500" mt={1}>
                      Minimum 14 days lead time required
                    </Text>
                  </Box>
                </VStack>
              </Box>

              {/* Artwork Section */}
              <Box bg="gray.800" p={5} borderRadius="xl">
                <Heading size="sm" color="white" mb={4}>🎨 Artwork</Heading>

                <Box>
                  <Text mb={2} fontSize="sm" color="gray.400" fontWeight="medium">
                    Select Artwork (Optional)
                  </Text>
                  <NativeSelect.Root size="lg">
                    <NativeSelect.Field
                      value={artworkId}
                      onChange={(e) => setArtworkId(e.target.value)}
                      bg="gray.700"
                      borderColor="gray.600"
                    >
                      <option value="">No artwork - blank items</option>
                      {artworks.map((art) => (
                        <option key={art.id} value={art.id}>
                          {art.name} ({art.file_type})
                        </option>
                      ))}
                    </NativeSelect.Field>
                  </NativeSelect.Root>
                </Box>
              </Box>
            </VStack>

            {/* Right Column - Line Items */}
            <Box bg="gray.800" p={5} borderRadius="xl">
              <HStack justify="space-between" mb={4}>
                <Heading size="sm" color="white">🛒 Line Items</Heading>
                <Button
                  type="button"
                  size="sm"
                  bg="blue.600"
                  color="white"
                  _hover={{ bg: 'blue.500' }}
                  onClick={addLineItem}
                >
                  + Add Item
                </Button>
              </HStack>

              <VStack align="stretch" gap={4}>
                {lineItems.map((item, index) => {
                  const product = getSelectedProduct(item.product_id);
                  const color = getSelectedColor(item.color_id);

                  return (
                    <Box
                      key={index}
                      p={4}
                      bg="gray.900"
                      borderRadius="lg"
                      border="1px solid"
                      borderColor="gray.700"
                    >
                      <HStack justify="space-between" mb={3}>
                        <Text fontSize="sm" color="gray.400" fontWeight="medium">
                          Item {index + 1}
                        </Text>
                        <IconButton
                          aria-label="Remove item"
                          size="xs"
                          colorPalette="red"
                          variant="ghost"
                          onClick={() => removeLineItem(index)}
                          disabled={lineItems.length === 1}
                        >
                          ✕
                        </IconButton>
                      </HStack>

                      <SimpleGrid columns={2} gap={3}>
                        <Box gridColumn="span 2">
                          <Text mb={1} fontSize="xs" color="gray.500">Product</Text>
                          <NativeSelect.Root>
                            <NativeSelect.Field
                              value={item.product_id}
                              onChange={(e) => handleProductChange(index, e.target.value)}
                              bg="gray.800"
                              borderColor="gray.600"
                            >
                              <option value="">Select product...</option>
                              {products.map((p) => (
                                <option key={p.id} value={p.id}>
                                  {p.name} - ${p.base_price.toFixed(2)}
                                </option>
                              ))}
                            </NativeSelect.Field>
                          </NativeSelect.Root>
                        </Box>

                        <Box>
                          <Text mb={1} fontSize="xs" color="gray.500">Size</Text>
                          <NativeSelect.Root>
                            <NativeSelect.Field
                              value={item.size_id}
                              onChange={(e) => updateLineItem(index, 'size_id', e.target.value)}
                              bg="gray.800"
                              borderColor="gray.600"
                              disabled={!item.product_id}
                            >
                              <option value="">Size...</option>
                              {sizes.map((s) => (
                                <option key={s.id} value={s.id}>
                                  {s.name}
                                </option>
                              ))}
                            </NativeSelect.Field>
                          </NativeSelect.Root>
                        </Box>

                        <Box>
                          <Text mb={1} fontSize="xs" color="gray.500">Color</Text>
                          <NativeSelect.Root>
                            <NativeSelect.Field
                              value={item.color_id}
                              onChange={(e) => updateLineItem(index, 'color_id', e.target.value)}
                              bg="gray.800"
                              borderColor="gray.600"
                              disabled={!item.product_id}
                            >
                              <option value="">Color...</option>
                              {colors.map((c) => (
                                <option key={c.id} value={c.id}>
                                  {c.name}
                                </option>
                              ))}
                            </NativeSelect.Field>
                          </NativeSelect.Root>
                        </Box>

                        <Box>
                          <Text mb={1} fontSize="xs" color="gray.500">Quantity</Text>
                          <Input
                            type="number"
                            min={1}
                            value={item.quantity}
                            onChange={(e) => updateLineItem(index, 'quantity', parseInt(e.target.value) || 1)}
                            bg="gray.800"
                            borderColor="gray.600"
                          />
                        </Box>

                        <Box>
                          <Text mb={1} fontSize="xs" color="gray.500">Subtotal</Text>
                          <Text fontSize="lg" fontWeight="bold" color="green.400" pt={2}>
                            ${product ? (product.base_price * item.quantity).toFixed(2) : '0.00'}
                          </Text>
                        </Box>
                      </SimpleGrid>

                      {/* Selected color preview */}
                      {color && (
                        <HStack mt={3} pt={3} borderTop="1px solid" borderColor="gray.700">
                          <Box
                            w="16px"
                            h="16px"
                            borderRadius="full"
                            bg={color.hex_code}
                            border="2px solid"
                            borderColor="gray.500"
                          />
                          <Text fontSize="xs" color="gray.400">
                            {color.name}
                          </Text>
                          {!item.inventory_id && item.product_id && item.size_id && item.color_id && (
                            <Text fontSize="xs" color="orange.400" ml="auto">
                              ⚠️ Combination not in stock
                            </Text>
                          )}
                          {item.inventory_id && (
                            <Text fontSize="xs" color="green.400" ml="auto">
                              ✓ In stock
                            </Text>
                          )}
                        </HStack>
                      )}
                    </Box>
                  );
                })}
              </VStack>
            </Box>
          </SimpleGrid>

          {/* Order Summary & Actions */}
          <Box bg="gray.800" p={5} borderRadius="xl" mt={6}>
            <Flex justify="space-between" align="center" wrap="wrap" gap={4}>
              <VStack align="start" gap={1}>
                <HStack gap={6}>
                  <Box>
                    <Text fontSize="sm" color="gray.400">Total Items</Text>
                    <Text fontSize="xl" fontWeight="bold" color="white">
                      {getTotalQuantity()}
                    </Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.400">Estimated Total</Text>
                    <Text fontSize="xl" fontWeight="bold" color="green.400">
                      ${calculateTotal().toFixed(2)}
                    </Text>
                  </Box>
                </HStack>
                {getTotalQuantity() < 10 && (
                  <Text fontSize="xs" color="orange.400">
                    ⚠️ Minimum order quantity is 10 items
                  </Text>
                )}
              </VStack>

              <HStack gap={3}>
                <Button
                  type="button"
                  variant="outline"
                  borderColor="gray.600"
                  color="gray.300"
                  _hover={{ bg: 'gray.700' }}
                  onClick={() => navigate('/orders')}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  size="lg"
                  bg="blue.600"
                  color="white"
                  _hover={{ bg: 'blue.500' }}
                  loading={submitting}
                  disabled={getTotalQuantity() < 10}
                  px={8}
                >
                  Create Order
                </Button>
              </HStack>
            </Flex>
          </Box>
        </Box>
      </VStack>
    </Box>
  );
};
