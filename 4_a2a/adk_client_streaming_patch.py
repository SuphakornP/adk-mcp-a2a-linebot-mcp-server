"""
ADK Client Streaming Patch Module

This module patches RemoteA2aAgent to properly handle partial/streaming events
from A2A servers and propagate the partial flag to parent agents.

Import this module BEFORE importing agent.py to ensure patches are applied.
"""

import logging

logger = logging.getLogger(__name__)


def apply_remote_agent_streaming_patch():
    """Patch RemoteA2aAgent to handle partial streaming events."""
    try:
        from google.adk.agents import remote_a2a_agent
        from google.adk.events import Event
        from google.genai import types as genai_types
        from a2a.types import TaskArtifactUpdateEvent
        
        # Store original _handle_a2a_response method
        original_handle_response = remote_a2a_agent.RemoteA2aAgent._handle_a2a_response
        
        async def patched_handle_a2a_response(self, a2a_response, ctx):
            """Patched version that handles streaming artifact updates with partial flag."""
            # Check if this is a streaming artifact update (tuple with TaskArtifactUpdateEvent)
            if isinstance(a2a_response, tuple) and len(a2a_response) >= 2:
                task, last_update = a2a_response[0], a2a_response[1]
                
                # Handle TaskArtifactUpdateEvent with append=True (partial streaming)
                if isinstance(last_update, TaskArtifactUpdateEvent):
                    is_partial = last_update.append and not last_update.last_chunk
                    
                    if is_partial:
                        # Create event directly from the artifact update
                        parts = []
                        if last_update.artifact and last_update.artifact.parts:
                            for part in last_update.artifact.parts:
                                # Handle Part(root=TextPart(...)) structure from A2A
                                text_content = None
                                
                                # Try direct text attribute
                                if hasattr(part, 'text') and part.text:
                                    text_content = part.text
                                # Try root.text (Part wrapping TextPart)
                                elif hasattr(part, 'root') and hasattr(part.root, 'text'):
                                    text_content = part.root.text
                                
                                if text_content:
                                    parts.append(genai_types.Part.from_text(text=text_content))
                        
                        if parts:
                            event = Event(
                                invocation_id=ctx.invocation_id,
                                author=self.name,
                                branch=ctx.branch,
                                content=genai_types.Content(role="model", parts=parts),
                                partial=True,  # Mark as partial!
                            )
                            return event
            
            # Fall back to original handler for non-partial events
            event = await original_handle_response(self, a2a_response, ctx)
            return event
        
        # Apply the patch
        remote_a2a_agent.RemoteA2aAgent._handle_a2a_response = patched_handle_a2a_response
        logger.info("✅ Applied RemoteA2aAgent streaming patch")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to apply RemoteA2aAgent streaming patch: {e}")
        import traceback
        traceback.print_exc()
        return False


def apply_all_patches():
    """Apply all client-side streaming patches."""
    success = apply_remote_agent_streaming_patch()
    
    if success:
        logger.info("🚀 ADK client streaming patches applied successfully!")
    else:
        logger.warning("⚠️ Some ADK client streaming patches failed to apply")
    
    return success


# Auto-apply patches when this module is imported
_patches_applied = False

def ensure_patches_applied():
    """Ensure patches are applied (idempotent)."""
    global _patches_applied
    if not _patches_applied:
        apply_all_patches()
        _patches_applied = True


# Apply patches on import
ensure_patches_applied()
