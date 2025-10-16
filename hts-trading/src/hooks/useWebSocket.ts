import { useEffect, useState, useRef } from 'react';
import io, { Socket } from 'socket.io-client';

interface PriceData {
  symbol: string;
  currentPrice: number;
  rsi: number;
  rsiTrend: string;
  macd: number;
  signal: number;
  histogram: number;
  macdTrend: string;
  timestamp: number;
}

interface SentimentData {
  fearGreed: number;
  redditSentiment: number;
  coinGeckoSentiment: number;
  overallScore: number;
  trend: string;
}

interface NewsArticle {
  id: string;
  title: string;
  description: string;
  url: string;
  source: string;
  image: string;
  published: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

export const useWebSocket = () => {
  const [priceData, setPriceData] = useState<Map<string, PriceData>>(new Map());
  const [sentiment, setSentiment] = useState<SentimentData | null>(null);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(Date.now());
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    // Connect to backend
    socketRef.current = io('http://localhost:8081', {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    socketRef.current.on('connect', () => {
      console.log('✅ WebSocket connected');
      setConnected(true);
    });

    socketRef.current.on('priceUpdate', (data: PriceData) => {
      setPriceData(prev => {
        const newData = new Map(prev);
        newData.set(data.symbol, data);
        return newData;
      });
      setLastUpdate(Date.now());
    });

    socketRef.current.on('sentimentUpdate', (data: SentimentData) => {
      setSentiment(data);
    });

    socketRef.current.on('newsUpdate', (data: NewsArticle[]) => {
      setNews(data);
    });

    socketRef.current.on('disconnect', () => {
      console.log('❌ WebSocket disconnected');
      setConnected(false);
    });

    socketRef.current.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  return { priceData, sentiment, news, connected, lastUpdate };
};

export default useWebSocket;