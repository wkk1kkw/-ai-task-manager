from click.testing import CliRunner
from commands.project import project_group


class TestProjectCommands:
    def test_create_project(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        result = runner.invoke(project_group, [
            "create", "test-proj",
            "--title", "Test Project",
            "--path", "/tmp/test"
        ])
        assert result.exit_code == 0
        assert "test-proj" in result.output
        assert "Test Project" in result.output

    def test_create_project_missing_title(self):
        runner = CliRunner()
        result = runner.invoke(project_group, ["create", "no-title"])
        assert result.exit_code != 0

    def test_list_projects_empty(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        result = runner.invoke(project_group, ["list"])
        assert result.exit_code == 0
        assert "没有项目" in result.output

    def test_list_projects_with_data(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        runner.invoke(project_group, [
            "create", "p1", "--title", "P1", "--path", "/a"
        ])
        runner.invoke(project_group, [
            "create", "p2", "--title", "P2", "--path", "/b"
        ])
        result = runner.invoke(project_group, ["list"])
        assert result.exit_code == 0
        assert "P1" in result.output
        assert "P2" in result.output

    def test_update_project_status(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        runner.invoke(project_group, [
            "create", "p1", "--title", "P1", "--path", "/a"
        ])
        result = runner.invoke(project_group, [
            "update", "p1", "--status", "paused"
        ])
        assert result.exit_code == 0
        assert "paused" in result.output or "已更新" in result.output

    def test_delete_project(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()
        runner.invoke(project_group, [
            "create", "p1", "--title", "P1", "--path", "/a"
        ])
        result = runner.invoke(project_group, ["delete", "p1", "--yes"])
        assert result.exit_code == 0
        assert "已删除" in result.output
