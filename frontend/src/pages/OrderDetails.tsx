import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Heading,
  VStack,
  HStack,
  Text,
  Badge,
  Spinner,
  Input,
  Button,
  Flex,
  SimpleGrid,
} from '@chakra-ui/react';
import { keyframes } from '@emotion/react';
import ReactMarkdown from 'react-markdown';
import type { EnrichedOrder, ChatMessage } from '../types/models';
import { getOrder } from '../api/ordersApi';
import { getConversation, sendChatMessage } from '../api/chatApi';

const slideInRight = keyframes`
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
`;

const slideInLeft = keyframes`
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
`;

const pulse = keyframes`
  0%, 80%, 100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
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

const getShortId = (id: string): string => {
  const parts = id.split('-');
  return parts[parts.length - 1] || id;
};

export const OrderDetails: React.FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const [order, setOrder] = useState<EnrichedOrder | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [chatInput, setChatInput] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const fetchData = async (): Promise<void> => {
      if (!orderId) return;

      try {
        const [orderData, conversationData] = await Promise.all([
          getOrder(orderId),
          getConversation(orderId).catch(() => null),
        ]);
        setOrder(orderData);
        if (conversationData) {
          setMessages(conversationData.messages);
        }
      } catch {
        setError('Failed to load order');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [orderId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Refocus input when sending completes
  useEffect(() => {
    if (!sending) {
      inputRef.current?.focus();
    }
  }, [sending]);

  const handleSendMessage = async (): Promise<void> => {
    if (!chatInput.trim() || !orderId || sending) return;

    const messageContent = chatInput;
    const userMessage: ChatMessage = {
      role: 'user',
      content: messageContent,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setChatInput('');
    setSending(true);

    try {
      const response = await sendChatMessage(orderId, messageContent);
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.content,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Refresh order data to capture any changes made by the agent
      const updatedOrder = await getOrder(orderId);
      setOrder(updatedOrder);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error || !order) {
    return <Text color="red.400">{error || 'Order not found'}</Text>;
  }

  return (
    <Flex gap={6} h="calc(100vh - 200px)">
      {/* Order Details Section */}
      <Box flex={1} overflowY="auto">
        <VStack align="stretch" gap={6}>
          <HStack justify="space-between">
            <Heading size="lg" color="white">Order Details</Heading>
            <Badge colorPalette={getStatusColor(order.status)} size="lg">
              {order.status}
            </Badge>
          </HStack>

          {/* Order Summary */}
          <Box bg="gray.800" p={4} borderRadius="md">
            <Heading size="sm" color="white" mb={3}>Order Summary</Heading>
            <SimpleGrid columns={2} gap={2}>
              <Text color="gray.400">Order ID:</Text>
              <Text fontFamily="mono" color="white" fontSize="sm">{order.id}</Text>
              <Text color="gray.400">Placed By:</Text>
              <Text color="white">{order.user_email}</Text>
              <Text color="gray.400">Delivery Date:</Text>
              <Text color="white">{order.delivery_date}</Text>
              <Text color="gray.400">Total Amount:</Text>
              <Text fontWeight="bold" color="green.400">${order.total_amount.toFixed(2)}</Text>
              <Text color="gray.400">Created:</Text>
              <Text color="white">{new Date(order.created_at).toLocaleDateString()}</Text>
            </SimpleGrid>
          </Box>

          {/* Shipping Address */}
          <Box bg="gray.800" p={4} borderRadius="md">
            <Heading size="sm" color="white" mb={3}>Shipping Address</Heading>
            <VStack align="start" gap={1}>
              <Text color="blue.300" fontWeight="bold">{order.shipping_address.label}</Text>
              <Text color="white">{order.shipping_address.street_address}</Text>
              <Text color="white">
                {order.shipping_address.city}, {order.shipping_address.state} {order.shipping_address.postal_code}
              </Text>
              <Text color="gray.400">{order.shipping_address.country}</Text>
            </VStack>
          </Box>

          {/* Artwork */}
          {order.artwork && (
            <Box bg="gray.800" p={4} borderRadius="md">
              <Heading size="sm" color="white" mb={3}>Artwork</Heading>
              <SimpleGrid columns={2} gap={2}>
                <Text color="gray.400">Name:</Text>
                <Text color="white">{order.artwork.name}</Text>
                <Text color="gray.400">File Type:</Text>
                <Text color="white">{order.artwork.file_type}</Text>
                <Text color="gray.400">Dimensions:</Text>
                <Text color="white">{order.artwork.width_px} x {order.artwork.height_px} px</Text>
              </SimpleGrid>
            </Box>
          )}

          {/* Line Items */}
          <Box>
            <Heading size="md" mb={3} color="white">Line Items</Heading>
            {order.line_items && order.line_items.length > 0 ? (
              <Box bg="gray.800" borderRadius="lg" overflow="hidden">
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#2D3748' }}>
                      <th style={{ padding: '12px 16px', textAlign: 'left', color: '#E2E8F0', fontWeight: 600, borderBottom: '1px solid #4A5568' }}>Product</th>
                      <th style={{ padding: '12px 16px', textAlign: 'center', color: '#E2E8F0', fontWeight: 600, borderBottom: '1px solid #4A5568' }}>Variant</th>
                      <th style={{ padding: '12px 16px', textAlign: 'center', color: '#E2E8F0', fontWeight: 600, borderBottom: '1px solid #4A5568' }}>Qty</th>
                      <th style={{ padding: '12px 16px', textAlign: 'right', color: '#E2E8F0', fontWeight: 600, borderBottom: '1px solid #4A5568' }}>Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    {order.line_items.map((item, index) => (
                      <tr
                        key={item.id}
                        style={{
                          backgroundColor: index % 2 === 0 ? '#1A202C' : '#2D3748',
                          borderBottom: '1px solid #4A5568'
                        }}
                      >
                        <td style={{ padding: '14px 16px' }}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                            <span style={{ color: '#E2E8F0', fontWeight: 500 }}>{item.product_name}</span>
                            <span style={{ color: '#63B3ED', fontFamily: 'monospace', fontSize: '12px' }}>{item.product_sku}</span>
                            <span style={{ color: '#718096', fontFamily: 'monospace', fontSize: '11px' }}>#{getShortId(item.id)}</span>
                          </div>
                        </td>
                        <td style={{ padding: '14px 16px', textAlign: 'center' }}>
                          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}>
                            <span style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '6px',
                              backgroundColor: '#374151',
                              padding: '4px 10px',
                              borderRadius: '12px',
                              fontSize: '13px'
                            }}>
                              <span
                                style={{
                                  display: 'inline-block',
                                  width: '10px',
                                  height: '10px',
                                  borderRadius: '50%',
                                  backgroundColor: item.color_hex,
                                  border: '1px solid #4A5568'
                                }}
                              />
                              <span style={{ color: '#E2E8F0' }}>{item.color}</span>
                            </span>
                            <span style={{
                              backgroundColor: '#1F2937',
                              color: '#9CA3AF',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              fontSize: '12px',
                              fontWeight: 500
                            }}>
                              {item.size}
                            </span>
                          </div>
                        </td>
                        <td style={{ padding: '14px 16px', textAlign: 'center', verticalAlign: 'middle' }}>
                          <span style={{
                            color: '#E2E8F0',
                            fontWeight: 600,
                            fontSize: '18px',
                            backgroundColor: '#374151',
                            padding: '6px 14px',
                            borderRadius: '6px'
                          }}>
                            {item.quantity}
                          </span>
                        </td>
                        <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                            <span style={{ color: '#68D391', fontWeight: 600, fontSize: '16px' }}>
                              ${(item.quantity * item.unit_price).toFixed(2)}
                            </span>
                            <span style={{ color: '#718096', fontSize: '12px' }}>
                              ${item.unit_price.toFixed(2)} each
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Box>
            ) : (
              <Text color="gray.400">No line items</Text>
            )}
          </Box>
        </VStack>
      </Box>

      {/* Chat Section */}
      <Box flex={1} display="flex" flexDirection="column" bg="gray.800" borderRadius="md" p={4}>
        <Heading size="md" mb={4}>Order Support Chat</Heading>

        <Box flex={1} overflowY="auto" mb={4} bg="gray.900" borderRadius="md" p={3}>
          <VStack align="stretch" gap={3}>
            {messages.length === 0 ? (
              <Text color="gray.500" textAlign="center" py={4}>
                Ask questions about your order or request changes
              </Text>
            ) : (
              messages.map((msg, idx) => (
                <Box
                  key={idx}
                  bg={msg.role === 'user' ? 'blue.700' : 'gray.700'}
                  p={3}
                  borderRadius="md"
                  alignSelf={msg.role === 'user' ? 'flex-end' : 'flex-start'}
                  maxW="85%"
                  animation={`${msg.role === 'user' ? slideInRight : slideInLeft} 0.3s ease-out`}
                >
                  {msg.role === 'assistant' ? (
                    <Box
                      fontSize="sm"
                      css={{
                        '& p': { marginBottom: '0.5em' },
                        '& p:last-child': { marginBottom: 0 },
                        '& ul, & ol': { paddingLeft: '1.5em', marginBottom: '0.5em' },
                        '& li': { marginBottom: '0.25em' },
                        '& strong': { fontWeight: 600 },
                        '& code': {
                          backgroundColor: 'rgba(0,0,0,0.3)',
                          padding: '0.1em 0.3em',
                          borderRadius: '3px',
                          fontSize: '0.9em',
                        },
                      }}
                    >
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </Box>
                  ) : (
                    <Text fontSize="sm">{msg.content}</Text>
                  )}
                  <Text fontSize="xs" color="gray.400" mt={1}>
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </Text>
                </Box>
              ))
            )}
            {sending && (
              <Box
                bg="gray.700"
                p={3}
                borderRadius="md"
                alignSelf="flex-start"
                maxW="85%"
                animation={`${slideInLeft} 0.3s ease-out`}
              >
                <HStack gap={1}>
                  <Box
                    w="8px"
                    h="8px"
                    borderRadius="full"
                    bg="blue.400"
                    animation={`${pulse} 1.4s infinite ease-in-out`}
                    style={{ animationDelay: '0s' }}
                  />
                  <Box
                    w="8px"
                    h="8px"
                    borderRadius="full"
                    bg="blue.400"
                    animation={`${pulse} 1.4s infinite ease-in-out`}
                    style={{ animationDelay: '0.2s' }}
                  />
                  <Box
                    w="8px"
                    h="8px"
                    borderRadius="full"
                    bg="blue.400"
                    animation={`${pulse} 1.4s infinite ease-in-out`}
                    style={{ animationDelay: '0.4s' }}
                  />
                </HStack>
              </Box>
            )}
            <div ref={messagesEndRef} />
          </VStack>
        </Box>

        <HStack>
          <Input
            ref={inputRef}
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder={sending ? "Waiting for response..." : "Type your message..."}
            bg="gray.700"
            color="white"
            borderColor="gray.600"
            _placeholder={{ color: 'gray.400' }}
            autoFocus
          />
          <Button
            bg="blue.600"
            color="white"
            _hover={{ bg: 'blue.500' }}
            onClick={handleSendMessage}
            loading={sending}
            disabled={!chatInput.trim()}
          >
            Send
          </Button>
        </HStack>
      </Box>
    </Flex>
  );
};
