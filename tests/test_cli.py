import re
from click.testing import CliRunner
from taskman import cli


class TestCLI:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "project" in result.output
        assert "task" in result.output
        assert "agent" in result.output
        assert "report" in result.output

    def test_full_workflow(self, tmp_path, monkeypatch):
        """Complete workflow integration test"""
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", str(tmp_path))
        runner = CliRunner()

        # 1. Create project
        r = runner.invoke(cli, ["project", "create", "demo", "--title", "Demo", "--path", str(tmp_path / "demo")])
        assert r.exit_code == 0

        # 2. Add tasks
        r = runner.invoke(cli, ["task", "add", "demo", "--title", "Task 1", "--priority", "high"])
        assert r.exit_code == 0
        match1 = re.search(r'ID: (\w+)', r.output)
        assert match1
        task1_id = match1.group(1)

        r = runner.invoke(cli, ["task", "add", "demo", "--title", "Task 2", "--priority", "low"])
        assert r.exit_code == 0
        match2 = re.search(r'ID: (\w+)', r.output)
        assert match2
        task2_id = match2.group(1)

        # 3. Assign agent to task 1
        r = runner.invoke(cli, ["agent", "assign", "demo", task1_id, "--agent", "agent-1"])
        assert r.exit_code == 0

        # 4. Update task 2 to done
        r = runner.invoke(cli, ["task", "update", "demo", task2_id, "--status", "done"])
        assert r.exit_code == 0

        # 5. List projects
        r = runner.invoke(cli, ["project", "list"])
        assert r.exit_code == 0

        # 6. List tasks
        r = runner.invoke(cli, ["task", "list", "demo"])
        assert r.exit_code == 0
