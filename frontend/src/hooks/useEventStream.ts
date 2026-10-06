import { useEffect, useRef, useState } from 'react';
import { AgentEvent } from '../types';

export function useEventStream(taskId: string | null) {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!taskId) {
      setEvents([]);
      setIsConnected(false);
      return;
    }

    // MOCK EVENT STREAM FOR UI DEVELOPMENT
    setIsConnected(true);
    let step = 1;
    const steps = [
      'Repository scanned',
      'Architecture reconstructed',
      'Issue understood',
      'Relevant symbols identified',
      'Impact radius calculated',
      'Patch strategy selected',
      'Files modified',
      'Regression test generated',
      'Tests executed',
      'Patch validated',
      'Confidence score calculated'
    ];
    
    const interval = setInterval(() => {
      if (step > steps.length) {
        clearInterval(interval);
        return;
      }
      
      const newEvent: AgentEvent = {
        id: Math.random().toString(36),
        taskId,
        timestamp: new Date().toISOString(),
        type: 'step_update',
        stepName: steps[step - 1],
        stepNumber: step,
        status: step === steps.length ? 'success' : 'running',
        message: `Executing ${steps[step - 1]}...`
      };
      
      setEvents(prev => [...prev.filter(e => e.stepNumber !== step), newEvent]);
      
      if (step > 1) {
        setEvents(prev => prev.map(e => 
          e.stepNumber === step - 1 ? { ...e, status: 'success', message: `Completed ${steps[step - 2]}` } : e
        ));
      }
      
      step++;
    }, 2000);

    return () => {
      clearInterval(interval);
    };

    /* REAL IMPLEMENTATION
    const eventSource = new EventSource(`/api/tasks/${taskId}/events`);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const parsedData: AgentEvent = JSON.parse(event.data);
        setEvents((prevEvents) => [...prevEvents, parsedData]);
      } catch (err) {
        console.error('Failed to parse event data:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.error('EventSource error:', err);
      setError(new Error('Connection lost'));
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
    */
  }, [taskId]);

  return { events, isConnected, error };
}
