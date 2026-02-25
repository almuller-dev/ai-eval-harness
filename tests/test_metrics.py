from eval_harness.metrics import exact_label, json_schema_match


def test_exact_label() -> None:
    out = exact_label("Auth", "auth")
    assert out.passed is True
    assert out.score == 1.0


def test_json_schema_match_ok() -> None:
    schema = {
        "type": "object",
        "required": ["action", "user"],
        "properties": {
            "action": {"const": "reset_password"},
            "user": {"type": "string"},
        },
    }
    out = json_schema_match('{"action":"reset_password","user":"asmith"}', schema)
    assert out.passed is True
    assert out.score == 1.0


def test_json_schema_match_bad_json() -> None:
    schema = {"type": "object"}
    out = json_schema_match("not json", schema)
    assert out.passed is False
    assert out.score <= 0.2
