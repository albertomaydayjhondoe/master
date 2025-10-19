from orchestration.scripts.workflow_validator import load_and_validate


def test_main_orchestrator_valid(tmp_path):
    p = tmp_path / "wf.json"
    p.write_text('''{"name": "test", "nodes": [{"id": "1", "type": "trigger"}]}''')
    assert load_and_validate(str(p)) is True


def test_invalid_workflow(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text('[]')
    assert load_and_validate(str(p)) is False
