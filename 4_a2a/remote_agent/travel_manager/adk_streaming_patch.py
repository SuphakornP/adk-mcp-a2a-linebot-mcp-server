"""
ADK Streaming Patch Module

This module applies runtime patches to enable token-level streaming in Google ADK's A2A implementation.
Import this module BEFORE importing any ADK modules to ensure patches are applied.

The patches:
1. Enable StreamingMode.SSE in RunConfig for A2A requests
2. Handle partial events and emit TaskArtifactUpdateEvent with append=True for token streaming

Usage:
    import adk_streaming_patch  # Must be first import!
    from google.adk.agents import Agent
    ...
"""

import logging

logger = logging.getLogger(__name__)


def apply_request_converter_patch():
    """Patch the request converter to use StreamingMode.SSE for A2A requests."""
    try:
        from google.adk.a2a.converters import request_converter
        from google.adk.agents.run_config import RunConfig, StreamingMode
        from google.genai import types as genai_types
        
        # Store original function
        original_convert = request_converter.convert_a2a_request_to_adk_run_args
        
        def patched_convert_a2a_request_to_adk_run_args(request, part_converter=None):
            """Patched version that enables SSE streaming mode."""
            if part_converter is None:
                from google.adk.a2a.converters.part_converter import convert_a2a_part_to_genai_part
                part_converter = convert_a2a_part_to_genai_part
            
            if not request.message:
                raise ValueError('Request message cannot be None')
            
            # Get user from call context if available
            user_id = f'A2A_USER_{request.context_id}'
            if (
                request.call_context
                and request.call_context.user
                and request.call_context.user.user_name
            ):
                user_id = request.call_context.user.user_name
            
            return {
                'user_id': user_id,
                'session_id': request.context_id,
                'new_message': genai_types.Content(
                    role='user',
                    parts=[part_converter(part) for part in request.message.parts],
                ),
                'run_config': RunConfig(streaming_mode=StreamingMode.SSE),  # Enable SSE streaming!
            }
        
        # Apply the patch
        request_converter.convert_a2a_request_to_adk_run_args = patched_convert_a2a_request_to_adk_run_args
        logger.info("✅ Applied request_converter patch for SSE streaming")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to apply request_converter patch: {e}")
        return False


def apply_event_converter_patch():
    """Patch the event converter to handle partial events for token streaming."""
    try:
        from google.adk.a2a.converters import event_converter
        from a2a.types import TaskArtifactUpdateEvent, Artifact
        
        # Store original function
        original_convert = event_converter.convert_event_to_a2a_events
        
        def patched_convert_event_to_a2a_events(
            event,
            invocation_context,
            task_id=None,
            context_id=None,
            part_converter=None,
        ):
            """Patched version that handles partial events for token streaming."""
            if part_converter is None:
                from google.adk.a2a.converters.part_converter import convert_genai_part_to_a2a_part
                part_converter = convert_genai_part_to_a2a_part
            
            if not event:
                raise ValueError("Event cannot be None")
            if not invocation_context:
                raise ValueError("Invocation context cannot be None")
            
            a2a_events = []
            
            try:
                # Handle error scenarios
                if event.error_code:
                    error_event = event_converter._create_error_status_event(
                        event, invocation_context, task_id, context_id
                    )
                    a2a_events.append(error_event)
                
                # Handle partial/streaming events - emit TaskArtifactUpdateEvent with append=true
                if hasattr(event, 'partial') and event.partial:
                    message = event_converter.convert_event_to_a2a_message(
                        event, invocation_context, part_converter=part_converter
                    )
                    if message and message.parts:
                        artifact_event = TaskArtifactUpdateEvent(
                            task_id=task_id,
                            context_id=context_id,
                            artifact=Artifact(
                                artifact_id=f"partial-{task_id}",
                                parts=message.parts,
                            ),
                            append=True,  # This is a partial/incremental update
                            last_chunk=False,
                        )
                        a2a_events.append(artifact_event)
                    return a2a_events
                
                # Handle regular message content
                message = event_converter.convert_event_to_a2a_message(
                    event, invocation_context, part_converter=part_converter
                )
                if message:
                    running_event = event_converter._create_status_update_event(
                        message, invocation_context, event, task_id, context_id
                    )
                    a2a_events.append(running_event)
                    
            except Exception as e:
                logger.error("Failed to convert event to A2A events: %s", e)
                raise
            
            return a2a_events
        
        # Apply the patch
        event_converter.convert_event_to_a2a_events = patched_convert_event_to_a2a_events
        logger.info("✅ Applied event_converter patch for partial token streaming")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to apply event_converter patch: {e}")
        return False


def apply_all_patches():
    """Apply all streaming patches. Call this before using ADK A2A."""
    success = True
    success &= apply_request_converter_patch()
    success &= apply_event_converter_patch()
    
    if success:
        logger.info("🚀 All ADK streaming patches applied successfully!")
    else:
        logger.warning("⚠️ Some ADK streaming patches failed to apply")
    
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
