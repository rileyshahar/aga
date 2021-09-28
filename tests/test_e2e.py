"""End-to-end tests for gradescope."""

import json
from pathlib import Path
from typing import Any, TypeVar

import docker  # type: ignore
import pytest

from aga.core import Problem

# from aga.cli import app
from aga.gradescope import into_gradescope_zip

# from typer.testing import CliRunner


Output = TypeVar("Output")

# runner = CliRunner(mix_stderr=False)


@pytest.fixture(name="docker_container")
def fixture_docker_container() -> docker.DockerClient:
    """Generate a basic docker client."""
    return docker.from_env()


# Simulates the work done by Gradescope's docker harness
BASH_COMMAND = """
set -e

apt-get update &> /dev/null

apt-get install -y curl unzip dos2unix &> /dev/null

mkdir -p /autograder/source /autograder/results &> /dev/null

unzip -n -d /autograder/source /tmp/autograder.zip &> /dev/null

cp /autograder/source/run_autograder /autograder/run_autograder &> /dev/null

dos2unix /autograder/run_autograder /autograder/source/setup.sh &> /dev/null

chmod +x /autograder/run_autograder &> /dev/null

apt-get update &> /dev/null

bash /autograder/source/setup.sh &> /dev/null
apt-get clean &> /dev/null
rm -rf /var/lib/apt/lists/* /var/tmp/* &> /dev/null

/autograder/run_autograder &> /dev/null
cat /autograder/results/results.json
"""


# it would be _awesome_ if we could module-scope this fixture so we don't have to rerun
# the docker container (which involves a lot of network usage to download dependencides)
# for each test. Right now, this isn't possible, because it depends on tmp_path which is
# function-scoped (our custom fixtures could easily be module-scoped or session-scoped).
# We could fix this by writing our own tmp_path.


@pytest.fixture(name="gs_json")
def fixture_gs_json(
    docker_container: docker.DockerClient,
    square: Problem[int],
    source_square: str,
    tmp_path: Path,
) -> Any:
    """Test the gradescope functionality."""
    problem = square.name()

    # run the cli, putting the problem at a temporary path
    # result =
    #   runner.invoke(app, ["gen", problem, "--dest", f"{tmp_path}/{problem}.zip"])
    # zip_loc = result.stdout
    zip_loc = into_gradescope_zip(square, f"{tmp_path}/{problem}.zip")

    container = docker_container.containers.run(
        "gradescope/auto-builds",
        f"bash -c '{BASH_COMMAND}'",
        volumes=[
            f"{zip_loc}:/tmp/autograder.zip",
            f"{source_square}:/autograder/submission/{problem}.py",
        ],
        detach=True,
    )
    container.wait()
    return json.loads(container.logs())


@pytest.mark.slow
def test_json_test_name(gs_json: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct test names."""
    assert set(map(lambda x: x["name"], gs_json["tests"])) == {
        "Test 4",
        "Test 2",
        "Test -2",
    }


@pytest.mark.slow
def test_json_test_score(gs_json: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct score."""
    assert gs_json["score"] == 3
