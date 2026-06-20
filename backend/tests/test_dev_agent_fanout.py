from app.agents.dev_agent import (
    _FileSpec,
    _build_developer_lanes,
    _parse_developer_instances,
)


def test_parse_developer_instances_from_technical_design_markdown():
    markdown = "**Recommended Developer Agent instances:** 3"
    assert _parse_developer_instances(markdown) == 3


def test_parse_developer_instances_clamps_to_supported_range():
    markdown = "**Recommended Developer Agent instances:** 99"
    assert _parse_developer_instances(markdown) == 3


def test_build_developer_lanes_splits_backend_frontend_and_platform():
    files = [
        _FileSpec(path="backend/app/models/expense.py", context_hint="backend_model"),
        _FileSpec(path="frontend/src/pages/ExpensePage.tsx", context_hint="frontend_page"),
        _FileSpec(path="README.md", context_hint="readme"),
    ]

    lanes = _build_developer_lanes(files, 3)
    lane_names = {lane.name for lane in lanes}

    assert lane_names == {
        "developer-agent-backend",
        "developer-agent-frontend",
        "developer-agent-platform",
    }
    assert {lane.name: len(lane.files) for lane in lanes} == {
        "developer-agent-backend": 1,
        "developer-agent-frontend": 1,
        "developer-agent-platform": 1,
    }
