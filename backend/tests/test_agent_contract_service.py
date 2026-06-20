from app.services.agent_contract_service import (
    get_agent_contract,
    list_agent_contracts,
    load_agent_contract_registry,
)


def test_agent_contract_registry_loads_all_phase3_agents():
    registry = load_agent_contract_registry()
    ids = {contract["id"] for contract in registry["agents"]}

    assert "technical-design-agent" in ids
    assert "developer-agent" in ids
    assert "developer-agent-backend" in ids
    assert "code-review-agent" in ids
    assert "devops-agent" in ids
    assert "monitoring-agent" in ids


def test_agent_contract_summaries_are_api_safe():
    summaries = list_agent_contracts()

    assert summaries
    assert all("responsibilities" not in item for item in summaries)
    assert all(item["id"] and item["step"]["name"] for item in summaries)


def test_get_agent_contract_returns_full_contract():
    contract = get_agent_contract("monitoring-agent")

    assert contract["outputs"]["documents"] == ["monitoring_report"]
    assert contract["handoff"]["next_agent"] is None
