"""Agent contract registry loader.

Sprint 38 centralizes agent contracts in docs/contracts/agent-contracts.v2.json
so the backend, UI, and documentation can refer to one machine-readable source.
"""
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import HTTPException


_ROOT = Path(__file__).resolve().parents[3]
_REGISTRY_PATH = _ROOT / "docs" / "contracts" / "agent-contracts.v2.json"


@lru_cache(maxsize=1)
def load_agent_contract_registry() -> dict[str, Any]:
    if not _REGISTRY_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "CONTRACT_REGISTRY_MISSING",
                "message": f"Agent contract registry not found: {_REGISTRY_PATH}",
            },
        )
    try:
        data = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "CONTRACT_REGISTRY_INVALID",
                "message": f"Agent contract registry is invalid JSON: {exc}",
            },
        ) from exc
    _validate_registry(data)
    return data


def list_agent_contracts() -> list[dict[str, Any]]:
    registry = load_agent_contract_registry()
    return [
        {
            "id": contract["id"],
            "name": contract["name"],
            "role": contract["role"],
            "layer": contract["layer"],
            "step": contract["step"],
            "outputs": contract["outputs"],
            "handoff": contract["handoff"],
        }
        for contract in registry["agents"]
    ]


def get_agent_contract(agent_name: str) -> dict[str, Any]:
    registry = load_agent_contract_registry()
    for contract in registry["agents"]:
        if contract["id"] == agent_name:
            return contract
    raise HTTPException(
        status_code=404,
        detail={
            "error_code": "CONTRACT_NOT_FOUND",
            "message": f"Agent contract {agent_name!r} not found",
        },
    )


def _validate_registry(data: dict[str, Any]) -> None:
    if not isinstance(data, dict) or not isinstance(data.get("agents"), list):
        raise HTTPException(
            status_code=500,
            detail={"error_code": "CONTRACT_REGISTRY_INVALID", "message": "Registry must contain an agents array."},
        )
    seen: set[str] = set()
    required = {"id", "name", "role", "layer", "step", "model", "inputs", "outputs", "responsibilities", "handoff", "workspace"}
    for contract in data["agents"]:
        if not isinstance(contract, dict):
            raise HTTPException(status_code=500, detail={"error_code": "CONTRACT_REGISTRY_INVALID", "message": "Each contract must be an object."})
        missing = sorted(required - set(contract))
        if missing:
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "CONTRACT_REGISTRY_INVALID",
                    "message": f"Contract {contract.get('id', '<unknown>')} missing fields: {', '.join(missing)}",
                },
            )
        agent_id = contract["id"]
        if agent_id in seen:
            raise HTTPException(
                status_code=500,
                detail={"error_code": "CONTRACT_REGISTRY_INVALID", "message": f"Duplicate contract id: {agent_id}"},
            )
        seen.add(agent_id)
