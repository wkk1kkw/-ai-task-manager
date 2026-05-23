from click.testing import CliRunner
from commands.project import project_group
from commands.task import task_group


class TestTaskCommands:
    def setup_project(self, runner, tmp_path):
        """Helper to create a test project using tmp_path isolation"""
        runner.invoke(project_group, [
            "create", "test-proj", "--title", "Test", "--path", str(tmp_path / "test")
        ])

    def test_add_task(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        self.setup_project(runner, tmp_path)
        result = runner.invoke(task_group, [
            "add", "test-proj",
            "--title", "实现导航栏",
            "--priority", "high"
        ])
        assert result.exit_code == 0
        assert "实现导航栏" in result.output

    def test_list_tasks(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        self.setup_project(runner, tmp_path)
        runner.invoke(task_group, ["add", "test-proj", "--title", "Task A"])
        runner.invoke(task_group, ["add", "test-proj", "--title", "Task B"])
        result = runner.invoke(task_group, ["list", "test-proj"])
        assert result.exit_code == 0
        assert "Task A" in result.output
        assert "Task B" in result.output

    def test_list_tasks_empty(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        self.setup_project(runner, tmp_path)
        result = runner.invoke(task_group, ["list", "test-proj"])
        assert result.exit_code == 0

    def test_update_task_status(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        self.setup_project(runner, tmp_path)
        runner.invoke(task_group, ["add", "test-proj", "--title", "Task X"])
        result = runner.invoke(task_group, [
            "update", "test-proj", "0", "--status", "done"
        ])
        assert result.exit_code == 0

    def test_delete_task(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        self.setup_project(runner, tmp_path)
        runner.invoke(task_group, ["add", "test-proj", "--title", "Delete Me"])
        result = runner.invoke(task_group, ["delete", "test-proj", "0", "--yes"])
        assert result.exit_code == 0

    def test_add_note(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        self.setup_project(runner, tmp_path)
        runner.invoke(task_group, ["add", "test-proj", "--title", "Task N"])
        result = runner.invoke(task_group, [
            "note", "test-proj", "0",
            "--text", "这是一条笔记"
        ])
        assert result.exit_code == 0
        assert "笔记" in result.output or "note" in result.output.lower()

    def test_add_task_non_existent_project(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        result = runner.invoke(task_group, [
            "add", "no-project", "--title", "Orphan"
        ])
        assert "不存在" in result.output
