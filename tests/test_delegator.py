from spolottery.domain.models import Pool, Delegator, Delegation, first_delegation_amount, is_eligible

from tests.conftest import make_pool, make_delegator_with_delegation_history


def test_delegator_is_eligible_for_lottery():
    # Arrange
    pool = make_pool()
    stake_address = "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"
    delegator = make_delegator_with_delegation_history(pool, stake_address)

    # Act / Assert
    assert (
        is_eligible(
            delegator,
            target_pool_id=pool.pool_id,
            current_epoch=306,
            min_count_active_epochs=6,
        )
        == True
    )


def test_delegator_is_not_eligible_for_lottery():
    # Arrange
    pool = make_pool()
    stake_address = "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"
    delegator = make_delegator_with_delegation_history(pool, stake_address)

    # Act / Assert
    assert (
        is_eligible(
            delegator,
            target_pool_id=pool.pool_id,
            current_epoch=307,
            min_count_active_epochs=6,
        )
        == False
    )


def test_delegator_first_delegation_amount():
    # Arrange
    pool = make_pool()
    stake_address = "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"
    delegator = make_delegator_with_delegation_history(pool, stake_address)

    # Act / Assert
    assert (
        first_delegation_amount(
            delegator,
            target_pool_id=pool.pool_id,
        )
        == 100000
    )


def test_delegator_first_delegation_amount_another_pool_id():
    # Arrange
    pool = make_pool()
    stake_address = "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"
    delegator = make_delegator_with_delegation_history(pool, stake_address)
    another_pool_id = "ea90b56d9c4d04c583ec728c8b415948b310d4653d12bd281aaff9df"

    # Act / Assert
    assert (
        first_delegation_amount(
            delegator,
            target_pool_id=another_pool_id,
        )
        == 300000
    )
