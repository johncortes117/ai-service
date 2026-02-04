/**
 * Custom hook for SSE (Server-Sent Events) streaming
 */

import { useEffect, useRef, useCallback } from 'react';
import { SSE_STREAM_URL } from '@/lib/api';
import type { SSEEvent } from '@/lib/types';

interface UseSSEStreamOptions {
    onMessage: (data: SSEEvent) => void;
    onError?: (error: Event) => void;
    enabled?: boolean;
}

export function useSSEStream({ onMessage, onError, enabled = true }: UseSSEStreamOptions) {
    const eventSourceRef = useRef<EventSource | null>(null);
    const onMessageRef = useRef(onMessage);
    const onErrorRef = useRef(onError);

    // Keep refs up to date
    useEffect(() => {
        onMessageRef.current = onMessage;
        onErrorRef.current = onError;
    }, [onMessage, onError]);

    const connect = useCallback(() => {
        if (!enabled) return;

        // Close existing connection
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }

        try {
            const eventSource = new EventSource(SSE_STREAM_URL);

            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data) as SSEEvent;
                    onMessageRef.current(data);
                } catch (error) {
                    console.error('Error parsing SSE data:', error);
                }
            };

            eventSource.onerror = (error) => {
                console.error('SSE connection error:', error);
                onErrorRef.current?.(error);
                // The browser will automatically try to reconnect
            };

            eventSourceRef.current = eventSource;
        } catch (error) {
            console.error('Error creating EventSource:', error);
        }
    }, [enabled]);

    const disconnect = useCallback(() => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
    }, []);

    useEffect(() => {
        connect();

        return () => {
            disconnect();
        };
    }, [connect, disconnect]);

    return { disconnect, reconnect: connect };
}
