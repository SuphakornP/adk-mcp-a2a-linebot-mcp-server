from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from a2a.client.client import ClientConfig as A2AClientConfig
from a2a.client.client_factory import ClientFactory as A2AClientFactory
from a2a.types import TransportProtocol as A2ATransport

# Enable streaming for A2A client to get SSE streaming responses
a2a_client_config = A2AClientConfig(
    streaming=True,  # Enable streaming for real-time text output
    polling=False,
    supported_transports=[A2ATransport.jsonrpc],
)
a2a_client_factory = A2AClientFactory(config=a2a_client_config)

root_agent = RemoteA2aAgent(
    name="travel_agent",
    description=(
        "คุณคือผู้ช่วยการท่องเที่ยวที่เชี่ยวชาญด้านการวางแผนการเดินทางและที่พัก Airbnb"
    ),
    agent_card=f"http://localhost:8001/{AGENT_CARD_WELL_KNOWN_PATH}",
    a2a_client_factory=a2a_client_factory,
)