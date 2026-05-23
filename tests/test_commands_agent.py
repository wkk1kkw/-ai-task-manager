from click.testing import CliRunner
from commands.project import project_group
from commands.task import task_group
from commands.agent import agent_group


class TestAgentCommands:
    def setup(self, runner, tmp_path):
        runner.invoke(project_group, [
            "create", "test-proj", "--title", "Test", "--path", str(tmp_path / "t")
        ])
        runner.invoke(task_group, [
            "add", "test-proj", "--title", "导航栏", "--priority", "high"
        ])

    def test_assign_agent(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        self.setup(runner, tmp_path)
        result = runner.invoke(agent_group, [
            "assign", "test-proj", "0",
            "--agent", "agent-1"
        ])
        assert result.exit_code == 0
        assert "agent-1" in result.output

    def test_agent_status(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        self.setup(runner, tmp_path)
        runner.invoke(agent_group, [
            "assign", "test-proj", "0", "--agent", "agent-1"
        ])
        result = runner.invoke(agent_group, ["status", "test-proj"])
        assert result.exit_code == 0
        assert "agent-1" in result.output

    def test_assign_to_nonexistent_task(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        self.setup(runner, tmp_path)
        result = runner.invoke(agent_group, [
            "assign", "test-proj", "99", "--agent", "agent-1"
        ])
        assert "不存在" in result.output
