from dagster import (
    Definitions,
    FilesystemIOManager,
    graph,
    job,
    op,
    repository,
    schedule,
)
from dagster_docker import docker_executor


@op
def hello():
    return 1


@op
def goodbye(foo):
    if foo != 1:
        raise Exception("Bad io manager")
    return foo * 2


@graph
def my_graph():
    goodbye(hello())


@graph
def test_graph():
    hello()

@graph
def my_graph():
    goodbye(hello())


# Example usage
my_job = my_graph.to_job(name="my_job")
test_job = test_graph.to_job(name="test_job")
wow_job = my_graph.to_job(name="wow_job")


@repository
def deploy_docker_repository():
    return [my_job, test_job, wow_job]
