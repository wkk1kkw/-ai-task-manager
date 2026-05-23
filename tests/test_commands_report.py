from click.testing import CliRunner
from commands.project import project_group
from commands.task import task_group
from commands.report import report_group


class TestReportCommands:
    def setup(self, runner, tmp_path):
        runner.invoke(project_group, [
            "create", "test-proj", "--title", "Test Project",
            "--path", str(tmp_path / "code")
        ])
        runner.invoke(task_group, [
            "add", "test-proj", "--title", "Task 1", "--priority", "high"
        ])
        runner.invoke(task_group, [
            "add", "test-proj", "--title", "Task 2", "--priority", "low"
        ])

    def test_generate_project_report(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        self.setup(runner, tmp_path)
        result = runner.invoke(report_group, ["generate", "test-proj"])
        assert result.exit_code == 0

    def test_generate_global_report(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        self.setup(runner, tmp_path)
        result = runner.invoke(report_group, ["generate"])
        assert result.exit_code == 0
