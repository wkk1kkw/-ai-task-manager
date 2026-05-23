from click.testing import CliRunner
from commands.project import project_group


class TestProjectInit:
    def test_create_with_init(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path / "data"))
        runner = CliRunner()
        base = tmp_path / "workspace"
        result = runner.invoke(project_group, [
            "create", "new-project",
            "--title", "New Project",
            "--path", str(base / "new-project"),
            "--init"
        ])
        assert result.exit_code == 0
        assert (base / "new-project").exists()
        assert (base / "new-project" / "README.md").exists()

    def test_create_without_init_no_dir_created(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path / "data"))
        runner = CliRunner()
        base = tmp_path / "workspace"
        result = runner.invoke(project_group, [
            "create", "virt-project",
            "--title", "Virtual",
            "--path", str(base / "virt-project")
        ])
        assert result.exit_code == 0
        assert not (base / "virt-project").exists()
