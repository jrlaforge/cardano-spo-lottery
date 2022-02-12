from datetime import datetime

import pytest

from conftest import make_pool, make_delegator_with_delegation_history
from models import Lottery, LotteryTicket, LotteryStrategyFactory, prepare_lottery_tickets_list, OutOfDelegator


def make_lottery():

    uuid = "abd1acef-c472-4444-bb17-e356a41a560b"
    pool = make_pool()
    name = "Test lottery 1"
    now = datetime.now()

    lottery_strategy_factory = LotteryStrategyFactory()
    lottery_strategy = lottery_strategy_factory.createLotteryStrategy(lottery_strategy_name="Fixed")

    lottery = Lottery(
        uuid=uuid,
        pool_id=pool.pool_id,
        name=name,
        lottery_tickets=[],
        start_epoch=306,
        end_epoch=308,
        count_epochs=2,
        draw_date=now,
        created_at=now,
        lottery_strategy=lottery_strategy,
        owners_allowed=True,
    )
    stake_address_delegator1 = "stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c"
    delegator1 = make_delegator_with_delegation_history(pool, stake_address_delegator1)
    stake_address_delegator2 = "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"
    delegator2 = make_delegator_with_delegation_history(pool, stake_address_delegator2)
    stake_address_delegator3 = "stake1u9yrn7z2g0ynx4wtpqfuv7fj3uuasavtzg6ulfv2f647jhcluzuur"
    delegator3 = make_delegator_with_delegation_history(pool, stake_address_delegator3)
    delegators = [(delegator1, 0.5), (delegator2, 0.25), (delegator3, 0.25)]

    lottery_tickets = []
    for delegator in delegators:
        lottery_tickets.append(
            LotteryTicket(
                delegator=delegator[0], winning_likelyhood=delegator[1], pool_owner=True, lottery_id=lottery.uuid
            )
        )

    lottery.lottery_tickets = lottery_tickets

    return lottery


def test_run_lottery():
    # Arrange
    lottery = make_lottery()
    # Act
    lottery.raffle_draw()
    # Assert
    assert lottery.winners == [
        "stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c",
        "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4",
        "stake1u9yrn7z2g0ynx4wtpqfuv7fj3uuasavtzg6ulfv2f647jhcluzuur",
    ]


def create_lottery_tickets_no_delegator(lottery_strategy_name: str):
    pool = make_pool()
    uuid = "abd1acef-c472-4444-bb17-e356a41a560b"
    name = "Test lottery 1"
    now = datetime.now()

    delegators = []

    lottery_strategy_factory = LotteryStrategyFactory()
    lottery_strategy = lottery_strategy_factory.createLotteryStrategy(lottery_strategy_name=lottery_strategy_name)

    lottery = Lottery(
        uuid=uuid,
        pool_id=pool.pool_id,
        name=name,
        lottery_tickets=[],
        start_epoch=306,
        end_epoch=308,
        count_epochs=2,
        draw_date=now,
        created_at=now,
        lottery_strategy=lottery_strategy,
        owners_allowed=True,
    )

    return delegators, lottery, pool


def test_prepare_fixed_lottery_tickets_no_delegator():
    # Arrange
    delegators, lottery, pool = create_lottery_tickets_no_delegator("Fixed")

    # Act/Assert
    with pytest.raises(OutOfDelegator, match="Out of Delegator for lottery"):
        prepare_lottery_tickets_list(delegators, lottery, pool)


def test_prepare_stake_lottery_tickets_no_delegator():
    # Arrange
    delegators, lottery, pool = create_lottery_tickets_no_delegator("Stake")

    # Act/Assert
    with pytest.raises(OutOfDelegator, match="Out of Delegator for lottery"):
        prepare_lottery_tickets_list(delegators, lottery, pool)


def create_lottery_tickets_x_delegator(count_delegators: int, lottery_strategy_name: str):

    pool = make_pool()
    uuid = "abd1acef-c472-4444-bb17-e356a41a560b"
    name = "Test lottery 1"
    now = datetime.now()

    stake_address = "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"
    delegator1 = make_delegator_with_delegation_history(pool, stake_address, stake_amount=100000)

    if count_delegators > 1:
        stake_address2 = "stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c"
        delegator2 = make_delegator_with_delegation_history(pool, stake_address2, stake_amount=500000)
        delegators = [delegator1, delegator2]
    else:
        delegators = [delegator1]

    lottery_strategy_factory = LotteryStrategyFactory()
    lottery_strategy = lottery_strategy_factory.createLotteryStrategy(lottery_strategy_name=lottery_strategy_name)

    lottery = Lottery(
        uuid=uuid,
        pool_id=pool.pool_id,
        name=name,
        lottery_tickets=[],
        start_epoch=306,
        end_epoch=308,
        count_epochs=2,
        draw_date=now,
        created_at=now,
        lottery_strategy=lottery_strategy,
        owners_allowed=True,
    )

    return delegators, lottery, pool


def test_prepare_fixed_lottery_tickets_1_delegator():
    # Arrange
    delegators, lottery, pool = create_lottery_tickets_x_delegator(1, "Fixed")

    expected_probabilitlies = 1 / len(delegators)

    # Act
    lottery_tickets = prepare_lottery_tickets_list(delegators, lottery, pool)

    # Assert
    for lottery_ticket in lottery_tickets:
        assert lottery_ticket.winning_likelyhood == expected_probabilitlies


def test_prepare_fixed_lottery_tickets_list_2_delegators():
    # Arrange
    delegators, lottery, pool = create_lottery_tickets_x_delegator(2, "Fixed")

    expected_probabilitlies = 1 / len(delegators)

    # Act
    lottery_tickets = prepare_lottery_tickets_list(delegators, lottery, pool)

    # Assert
    for lottery_ticket in lottery_tickets:
        assert lottery_ticket.winning_likelyhood == expected_probabilitlies


def test_prepare_stake_lottery_tickets_2_delegators():
    # Arrange
    delegators, lottery, pool = create_lottery_tickets_x_delegator(2, "Stake")

    expected_probabilitlies = [0.2777777777777778, 0.7222222222222222]

    # Act
    lottery_tickets = prepare_lottery_tickets_list(delegators, lottery, pool)

    # Assert
    for i, lottery_ticket in enumerate(lottery_tickets):
        assert lottery_ticket.winning_likelyhood == expected_probabilitlies[i]


def test_prepare_stake_lottery_tickets_1_delegator():
    # Arrange
    delegators, lottery, pool = create_lottery_tickets_x_delegator(1, "Stake")

    expected_probabilitlies = 1

    # Act
    lottery_tickets = prepare_lottery_tickets_list(delegators, lottery, pool)

    # Assert
    for lottery_ticket in lottery_tickets:
        assert lottery_ticket.winning_likelyhood == expected_probabilitlies

