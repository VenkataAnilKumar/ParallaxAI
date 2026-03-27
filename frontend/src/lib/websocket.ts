const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

export type WSEventType =
  | "task.started"
  | "agent.started"
  | "agent.progress"
  | "agent.completed"
  | "agent.failed"
  | "validation.started"
  | "validation.completed"
  | "synthesis.started"
  | "task.completed"
  | "task.failed";

export interface WSEvent {
  event: WSEventType;
  task_id: string;
  data: Record<string, unknown>;
  timestamp: string;
}

type EventHandler = (event: WSEvent) => void;

export class ResearchSocket {
  private ws: WebSocket | null = null;
  private handlers: Map<WSEventType, EventHandler[]> = new Map();
  private reconnectDelay = 1000;
  private reconnectAttempts = 0;
  private maxReconnects = 5;
  private taskId: string;

  constructor(taskId: string) {
    this.taskId = taskId;
  }

  connect(): void {
    const url = `${WS_URL}/ws/research/${this.taskId}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
    };

    this.ws.onmessage = (ev) => {
      try {
        const event: WSEvent = JSON.parse(ev.data);
        const handlers = this.handlers.get(event.event) ?? [];
        handlers.forEach((h) => h(event));
      } catch {
        // ignore malformed messages
      }
    };

    this.ws.onclose = () => {
      if (this.reconnectAttempts < this.maxReconnects) {
        this.reconnectAttempts++;
        setTimeout(() => this.connect(), this.reconnectDelay);
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, 10000);
      }
    };

    this.ws.onerror = (err) => {
      console.error("[ResearchSocket] error", err);
    };
  }

  on(event: WSEventType, handler: EventHandler): this {
    const existing = this.handlers.get(event) ?? [];
    this.handlers.set(event, [...existing, handler]);
    return this;
  }

  off(event: WSEventType, handler: EventHandler): this {
    const existing = this.handlers.get(event) ?? [];
    this.handlers.set(
      event,
      existing.filter((h) => h !== handler),
    );
    return this;
  }

  disconnect(): void {
    this.maxReconnects = 0; // prevent reconnect
    this.ws?.close();
    this.ws = null;
  }
}
