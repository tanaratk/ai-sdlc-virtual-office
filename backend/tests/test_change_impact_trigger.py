from app.api.routes.change_impact import _normalise_requirement_ids


def test_normalise_requirement_ids_deduplicates_and_uppercases():
    assert _normalise_requirement_ids([" fr-001 ", "FR-001", "nfr-002"]) == [
        "FR-001",
        "NFR-002",
    ]


def test_normalise_requirement_ids_removes_empty_values():
    assert _normalise_requirement_ids(["", "  ", "BR-001"]) == ["BR-001"]
