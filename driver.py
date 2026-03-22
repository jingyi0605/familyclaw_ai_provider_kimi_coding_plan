from __future__ import annotations

from collections.abc import Mapping

from app.modules.ai_gateway.schemas import AiCapability
from app.modules.plugin.schemas import PluginRegistryItem
from app.plugins._ai_provider_runtime_helpers import (
    WrappedAiProviderDriver,
    clone_provider_profile_with_extra_config,
    read_int_value,
    read_provider_extra_config,
)
from app.plugins._sdk.ai_provider_drivers import build_anthropic_messages_driver

_FAST_TASK_TYPES = {
    "butler_bootstrap_extract",
    "config_dialogue",
    "config_extraction",
    "conversation_device_control_planner",
    "conversation_intent_detection",
    "memory_extraction",
    "proposal_batch_extraction",
    "qa_polish",
    "reminder_copywriting",
    "reminder_extraction",
    "scene_explanation",
}
_SHORT_OUTPUT_TASK_TYPES = {
    "config_dialogue",
    "qa_polish",
    "reminder_copywriting",
    "scene_explanation",
}
_FAST_TASK_MAX_TOKENS = 256
_SHORT_OUTPUT_MAX_TOKENS = 160
_FAST_HISTORY_MESSAGE_LIMIT = 4


def build_driver(plugin: PluginRegistryItem | None = None):
    return WrappedAiProviderDriver(
        base_driver=build_anthropic_messages_driver(plugin),
        prepare_request=_prepare_request,
    )


def _prepare_request(provider_profile, capability: AiCapability, payload: Mapping[str, object]):
    if capability != "text":
        return provider_profile, payload

    task_type = str(payload.get("task_type") or "").strip()
    if task_type not in _FAST_TASK_TYPES:
        return provider_profile, payload

    extra_config = read_provider_extra_config(provider_profile)
    next_extra_config = dict(extra_config)
    next_payload = dict(payload)
    changed = False

    payload_temperature = _read_optional_float(payload.get("temperature"))
    if payload_temperature is not None:
        next_extra_config["temperature"] = payload_temperature
        changed = True

    max_tokens_ceiling = _resolve_max_tokens_ceiling(task_type)
    current_max_tokens = read_int_value(extra_config.get("max_tokens"), max_tokens_ceiling)
    next_max_tokens = min(read_int_value(payload.get("max_tokens"), current_max_tokens), max_tokens_ceiling)
    if next_max_tokens != current_max_tokens:
        next_extra_config["max_tokens"] = next_max_tokens
        changed = True
    if payload.get("max_tokens") != next_max_tokens:
        next_payload["max_tokens"] = next_max_tokens
        changed = True

    trimmed_messages = _trim_messages(payload.get("messages"), keep_last_non_system=_FAST_HISTORY_MESSAGE_LIMIT)
    if trimmed_messages is not None:
        next_payload["messages"] = trimmed_messages
        changed = True

    if not changed:
        return provider_profile, payload
    return clone_provider_profile_with_extra_config(provider_profile, next_extra_config), next_payload


def _resolve_max_tokens_ceiling(task_type: str) -> int:
    if task_type in _SHORT_OUTPUT_TASK_TYPES:
        return _SHORT_OUTPUT_MAX_TOKENS
    return _FAST_TASK_MAX_TOKENS


def _trim_messages(raw_messages: object, *, keep_last_non_system: int) -> list[dict[str, str]] | None:
    if not isinstance(raw_messages, list):
        return None

    system_messages: list[dict[str, str]] = []
    non_system_messages: list[dict[str, str]] = []
    for item in raw_messages:
        if not isinstance(item, Mapping):
            continue
        role = str(item.get("role") or "").strip()
        content = str(item.get("content") or "").strip()
        if role not in {"system", "user", "assistant"} or not content:
            continue
        normalized = {"role": role, "content": content}
        if role == "system" and not system_messages and not non_system_messages:
            system_messages.append(normalized)
            continue
        non_system_messages.append(normalized)

    if len(non_system_messages) <= keep_last_non_system:
        return None

    return [*system_messages, *non_system_messages[-keep_last_non_system:]]


def _read_optional_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None
