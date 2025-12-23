import { get, post } from './client';
import type { Conversation, ChatCompletionResponse } from '../types/models';

export const getConversation = async (sessionId: string): Promise<Conversation> => {
  return get<Conversation>(`/v1/conversations/${sessionId}`);
};

interface SendMessageResponse {
  content: string;
  session_id: string;
}

export const sendChatMessage = async (
  orderId: string,
  message: string
): Promise<SendMessageResponse> => {
  const response = await post<ChatCompletionResponse>('/v1/chat/completions', {
    model: 'cx_order_support_agent',
    messages: [{ role: 'user', content: message }],
    order_id: orderId,
    session_id: orderId, // Use order_id as session_id for consistent conversation tracking
  });

  return {
    content: response.choices[0].message.content,
    session_id: response.session_id,
  };
};
