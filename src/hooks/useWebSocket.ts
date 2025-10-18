import { useEffect, useState, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { 
  PriceData, 
  SentimentData, 
  NewsArticle, 
  PredictionData,
  WebSocketPriceUpdate,
  WebSocketSentimentUpdate,
  WebSocketNewsUpdate,
  WebSocketWhaleUpdate,
  WebSocketData
} from '../types';

const SOCKET_URL = 'http://localhost:3001';
const RECONNECT_DELAY = 3000;
const MAX_RECONNECT_ATTEMPTS = 5;

export const useWebSocket = (): WebSocketData => {
  const [priceData, setPriceData] = useState<Map<string, WebSocketPriceUpdate>>(new Map());
  const [sentiment, setSentiment] = useState<SentimentData | null>(null);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(Date.now());
  const socketRef = useRef<Socket | null>(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const connect = () => {
      if (socketRef.current?.connected) {
        return;
      }

      console.log('🔄 Connecting to WebSocket...');
      
      socketRef.current = io(SOCKET_URL, {
        reconnection: true,
        reconnectionDelay: RECONNECT_DELAY,
        reconnectionAttempts: MAX_RECONNECT_ATTEMPTS,
        transports: ['websocket', 'polling'],
        timeout: 10000,
        forceNew: true
      });

      // Connection event handlers
      socketRef.current.on('connect', () => {
        console.log('✅ WebSocket connected');
        setConnected(true);
        reconnectAttempts.current = 0;
      });

      socketRef.current.on('disconnect', (reason) => {
        console.log('❌ WebSocket disconnected:', reason);
        setConnected(false);
      });

      socketRef.current.on('connect_error', (error) => {
        console.error('❌ WebSocket connection error:', error);
        setConnected(false);
        handleReconnect();
      });

      // Data event handlers
      socketRef.current.on('price_update', (data: WebSocketPriceUpdate) => {
        setPriceData(prev => {
          const newData = new Map(prev);
          newData.set(data.symbol, data);
          return newData;
        });
        setLastUpdate(Date.now());
      });

      socketRef.current.on('sentiment_update', (data: WebSocketSentimentUpdate) => {
        setSentiment(data.sentiment);
        setLastUpdate(Date.now());
      });

      socketRef.current.on('news_update', (data: WebSocketNewsUpdate) => {
        setNews(data.news);
        setLastUpdate(Date.now());
      });

      socketRef.current.on('whale_update', (data: WebSocketWhaleUpdate) => {
        // Handle whale transactions if needed
        setLastUpdate(Date.now());
      });

      socketRef.current.on('initial_prices', (prices: PriceData[]) => {
        console.log('📊 Received initial prices:', prices.length);
        setLastUpdate(Date.now());
      });

      socketRef.current.on('initial_sentiment', (data: SentimentData) => {
        setSentiment(data);
        setLastUpdate(Date.now());
      });

      socketRef.current.on('initial_news', (data: NewsArticle[]) => {
        setNews(data);
        setLastUpdate(Date.now());
      });

      // Error handling
      socketRef.current.on('error', (error) => {
        console.error('❌ WebSocket error:', error);
      });
    };

    const handleReconnect = () => {
      if (reconnectAttempts.current >= MAX_RECONNECT_ATTEMPTS) {
        console.error('❌ Max reconnection attempts reached');
        return;
      }

      reconnectAttempts.current++;
      console.log(`🔄 Reconnection attempt ${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS}`);

      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, RECONNECT_DELAY * reconnectAttempts.current);
    };

    // Initial connection
    connect();

    // Cleanup function
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      
      if (socketRef.current) {
        console.log('🛑 Disconnecting WebSocket');
        socketRef.current.disconnect();
        socketRef.current = null;
      }
    };
  }, []);

  // Manual reconnection function
  const reconnect = () => {
    if (socketRef.current) {
      socketRef.current.disconnect();
    }
    reconnectAttempts.current = 0;
    setTimeout(() => {
      const connect = () => {
        socketRef.current = io(SOCKET_URL, {
          reconnection: true,
          reconnectionDelay: RECONNECT_DELAY,
          reconnectionAttempts: MAX_RECONNECT_ATTEMPTS,
          transports: ['websocket', 'polling'],
          timeout: 10000,
          forceNew: true
        });

        socketRef.current.on('connect', () => {
          console.log('✅ WebSocket reconnected');
          setConnected(true);
          reconnectAttempts.current = 0;
        });

        socketRef.current.on('disconnect', () => {
          setConnected(false);
        });

        socketRef.current.on('price_update', (data: WebSocketPriceUpdate) => {
          setPriceData(prev => {
            const newData = new Map(prev);
            newData.set(data.symbol, data);
            return newData;
          });
          setLastUpdate(Date.now());
        });

        socketRef.current.on('sentiment_update', (data: WebSocketSentimentUpdate) => {
          setSentiment(data.sentiment);
          setLastUpdate(Date.now());
        });

        socketRef.current.on('news_update', (data: WebSocketNewsUpdate) => {
          setNews(data.news);
          setLastUpdate(Date.now());
        });
      };
      connect();
    }, 1000);
  };

  // Expose manual reconnection
  useEffect(() => {
    (window as any).reconnectWebSocket = reconnect;
  }, []);

  return { 
    priceData, 
    sentiment, 
    news, 
    connected, 
    lastUpdate 
  };
};

export default useWebSocket;