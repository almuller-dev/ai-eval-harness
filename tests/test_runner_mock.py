from eval_harness.runner import run_eval


class MockClient:
    def __init__(self, mapping: dict[str, str]):
        self.mapping = mapping

    def generate(self, *, prompt: str, model: str) -> str:
        # super simple: pick response by a substring key
        for key, val in self.mapping.items():
            if key in prompt:
                return val
        return "other"


def test_run_eval_with_mock(tmp_path) -> None:
    ds = tmp_path / "ds.jsonl"
    ds.write_text(
        "\n".join(
            [
                '{"id":"1","task":"label","input":"VPN login broken","expected":{"label":"auth"}}',
                '{"id":"2","task":"json","input":"Reset password for user bob","expected":'
                '{"schema":{"type":"object","required":["action","user"],"properties":'
                '{"action":{"const":"reset_password"},"user":{"type":"string"}}}}}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    mock = MockClient(
        mapping={
            "VPN login broken": "auth",
            "Reset password for user bob": '{"action":"reset_password","user":"bob"}',
        }
    )

    summary = run_eval(dataset_path=str(ds), model="dummy", client=mock)
    assert summary.total == 2
    assert summary.passed == 2
    assert summary.pass_rate == 1.0
