from pytest import fixture

from colmena.thinker.resources import ResourceCounter


@fixture
def rec() -> ResourceCounter:
    return ResourceCounter(8, ['ml', 'sim'])


def test_initialize(rec):
    assert rec.unallocated_nodes == 8
    assert rec.available_nodes(None) == 8


def test_allocations(rec):
    # Move 8 nodes to the "ml" pool
    assert rec.reallocate(None, "ml", 8)
    assert rec.unallocated_nodes == 0
    assert rec.available_nodes("ml") == 8

    # Checkout all of them
    assert rec.acquire("ml", 8, timeout=1)
    assert rec.available_nodes("ml") == 0
    assert rec.allocated_nodes("ml") == 8

    # Request unavailable nodes to test a timeout
    assert not rec.acquire("ml", 1, timeout=0.02)

    # Release nodes
    assert rec.release("ml", 4, rerequest=False) is None
    assert rec.available_nodes("ml") == 4

    # Release and re-request
    assert rec.release("ml", 4, rerequest=True, timeout=1)
    assert rec.available_nodes("ml") == 4
    assert rec.available_nodes("ml") == 4

    # Attempt a transfer that times out
    assert not rec.reallocate("ml", "sim", n_nodes=5, timeout=0.01)
    assert rec.available_nodes("ml") == 4

    # Attempt a transfer that completes
    assert rec.reallocate("ml", "sim", n_nodes=4, timeout=4)
    assert rec.available_nodes("sim") == 4
    assert rec.available_nodes("ml") == 0
    assert rec.allocated_nodes("sim") == 4
    assert rec.unallocated_nodes == 0
