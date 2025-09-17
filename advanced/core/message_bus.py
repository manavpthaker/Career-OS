"""Message bus for inter-agent communication."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid

from utils import get_logger, log_kv

logger = get_logger("message_bus")


class MessageType(Enum):
    """Types of messages that can be sent between agents."""
    COMPANY_INTEL = "company_intel"
    JOB_ANALYSIS = "job_analysis"
    SCORING_RESULT = "scoring_result"
    POSITIONING_STRATEGY = "positioning_strategy"
    CONTENT_REQUEST = "content_request"
    CONTENT_GENERATED = "content_generated"
    QA_REQUEST = "qa_request"
    QA_RESULT = "qa_result"
    ERROR = "error"
    STATUS = "status"


@dataclass
class AgentMessage:
    """Standardized message format for agent communication."""
    sender: str
    recipient: str
    message_type: MessageType
    data: Dict[str, Any]
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        result = asdict(self)
        result['message_type'] = self.message_type.value
        result['timestamp'] = self.timestamp.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create message from dictionary."""
        data['message_type'] = MessageType(data['message_type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class MessageBus:
    """Central message bus for agent communication."""

    def __init__(self):
        """Initialize the message bus."""
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[AgentMessage] = []
        self.agents: Dict[str, Any] = {}
        self._running = False

    def register_agent(self, agent_name: str, agent_instance: Any) -> None:
        """Register an agent with the message bus.

        Args:
            agent_name: Unique name for the agent
            agent_instance: The agent instance
        """
        self.agents[agent_name] = agent_instance
        logger.info(f"Registered agent: {agent_name}")

    def subscribe(self, agent_name: str, callback: Callable) -> None:
        """Subscribe an agent to receive messages.

        Args:
            agent_name: Name of the subscribing agent
            callback: Function to call when message received
        """
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(callback)
        logger.info(f"Agent {agent_name} subscribed to message bus")

    async def send(self, message: AgentMessage) -> None:
        """Send a message through the bus.

        Args:
            message: The message to send
        """
        # Log the message
        log_kv(logger, "message_sent",
            sender=message.sender,
            recipient=message.recipient,
            type=message.message_type.value,
            correlation_id=message.correlation_id)

        # Add to history
        self.message_history.append(message)

        # Add to queue for processing
        await self.message_queue.put(message)

    async def broadcast(self, message: AgentMessage) -> None:
        """Broadcast a message to all agents.

        Args:
            message: The message to broadcast
        """
        message.recipient = "*"  # Special recipient for broadcast
        await self.send(message)

    async def _process_messages(self) -> None:
        """Process messages from the queue."""
        while self._running:
            try:
                # Get message with timeout to allow checking _running flag
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )

                # Route to recipient(s)
                if message.recipient == "*":
                    # Broadcast to all
                    for agent_name, callbacks in self.subscribers.items():
                        if agent_name != message.sender:  # Don't send to sender
                            for callback in callbacks:
                                await self._deliver_message(callback, message)
                else:
                    # Send to specific recipient
                    if message.recipient in self.subscribers:
                        for callback in self.subscribers[message.recipient]:
                            await self._deliver_message(callback, message)
                    else:
                        logger.warning(f"No subscriber found for recipient: {message.recipient}")

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def _deliver_message(self, callback: Callable, message: AgentMessage) -> None:
        """Deliver a message to a callback.

        Args:
            callback: The callback function to invoke
            message: The message to deliver
        """
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(message)
            else:
                callback(message)
        except Exception as e:
            logger.error(f"Error delivering message to {message.recipient}: {e}")

            # Send error message back to sender
            error_message = AgentMessage(
                sender="message_bus",
                recipient=message.sender,
                message_type=MessageType.ERROR,
                data={
                    "error": str(e),
                    "original_message": message.to_dict()
                },
                correlation_id=message.correlation_id
            )
            await self.message_queue.put(error_message)

    async def start(self) -> None:
        """Start the message bus."""
        if not self._running:
            self._running = True
            asyncio.create_task(self._process_messages())
            logger.info("Message bus started")

    async def stop(self) -> None:
        """Stop the message bus."""
        self._running = False
        logger.info("Message bus stopped")

    def get_history(self,
                   correlation_id: Optional[str] = None,
                   sender: Optional[str] = None,
                   recipient: Optional[str] = None,
                   message_type: Optional[MessageType] = None,
                   limit: int = 100) -> List[AgentMessage]:
        """Get message history with optional filters.

        Args:
            correlation_id: Filter by correlation ID
            sender: Filter by sender
            recipient: Filter by recipient
            message_type: Filter by message type
            limit: Maximum number of messages to return

        Returns:
            List of messages matching the filters
        """
        filtered = self.message_history

        if correlation_id:
            filtered = [m for m in filtered if m.correlation_id == correlation_id]
        if sender:
            filtered = [m for m in filtered if m.sender == sender]
        if recipient:
            filtered = [m for m in filtered if m.recipient == recipient]
        if message_type:
            filtered = [m for m in filtered if m.message_type == message_type]

        return filtered[-limit:]

    def clear_history(self) -> None:
        """Clear the message history."""
        self.message_history.clear()
        logger.info("Message history cleared")

    async def wait_for_message(self,
                              recipient: str,
                              message_type: Optional[MessageType] = None,
                              correlation_id: Optional[str] = None,
                              timeout: float = 30.0) -> Optional[AgentMessage]:
        """Wait for a specific message.

        Args:
            recipient: The intended recipient
            message_type: Optional message type to wait for
            correlation_id: Optional correlation ID to match
            timeout: Maximum time to wait in seconds

        Returns:
            The matching message or None if timeout
        """
        future = asyncio.Future()

        def check_message(message: AgentMessage):
            """Check if message matches criteria."""
            if message.recipient != recipient:
                return
            if message_type and message.message_type != message_type:
                return
            if correlation_id and message.correlation_id != correlation_id:
                return

            # Message matches
            if not future.done():
                future.set_result(message)

        # Subscribe temporarily
        self.subscribe(recipient, check_message)

        try:
            message = await asyncio.wait_for(future, timeout=timeout)
            return message
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for message to {recipient}")
            return None
        finally:
            # Unsubscribe
            if recipient in self.subscribers:
                self.subscribers[recipient] = [
                    cb for cb in self.subscribers[recipient]
                    if cb != check_message
                ]