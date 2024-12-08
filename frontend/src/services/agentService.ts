import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

export async function getChatResponse(message: string) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/chat`, {
      message,
    });
    return response.data;
  } catch (error) {
    console.error('Error getting chat response:', error);
    throw error;
  }
}
