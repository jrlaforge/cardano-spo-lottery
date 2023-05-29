from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from tests.conftest import make_pool, make_delegator_with_delegation_history, make_lottery
from spolottery.domain.models import (
    Lottery,
    LotteryTicket,
    LotteryStrategyFactory,
    prepare_lottery_tickets_list,
    OutOfDelegator,
    LotteryWinner,
)


def test_run_lottery_draw():
    # Arrange
    lottery = make_lottery(with_tickets=True)
    # Act
    lottery.raffle_draw()
    # Assert

    assert lottery.winners == {
        LotteryWinner(
            "stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c", 0),
        LotteryWinner(
            "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4", 1),
        LotteryWinner(
            "stake1u9yrn7z2g0ynx4wtpqfuv7fj3uuasavtzg6ulfv2f647jhcluzuur", 2),
    }


def test_lottery_lottery_result_not_available():
    # Arrange/ Act
    lottery = make_lottery(with_tickets=True)

    lottery.draw_date = datetime.now(
        timezone.utc) + timedelta(days=7)

    # Assert
    assert lottery.is_lottery_result_available() == False


def test_lottery_lottery_result_available():
    # Arrange/ Act
    lottery = make_lottery(with_tickets=True)

    lottery.draw_date = datetime.now(timezone.utc) - timedelta(minutes=1)

    # Assert
    assert lottery.is_lottery_result_available() == True


def create_lottery_tickets_no_delegator(lottery_strategy_name: str):
    pool = make_pool()
    uuid = "abd1acef-c472-4444-bb17-e356a41a560b"
    name = "Test lottery 1"
    now = datetime.now()

    delegators = []

    lottery_strategy_factory = LotteryStrategyFactory()
    lottery_strategy = lottery_strategy_factory.createLotteryStrategy(
        lottery_strategy_name, min_live_stake=0)

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
        lottery_strategy_type=lottery_strategy_name,
        lottery_strategy=lottery_strategy,
        owners_allowed=True,
        min_live_stake=0
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


def create_lottery_tickets_x_delegator(count_delegators: int, lottery_strategy_name: str, min_live_stake: int = 0):
    pool = make_pool()
    uuid = "abd1acef-c472-4444-bb17-e356a41a560b"
    name = "Test lottery 1"
    now = datetime.now()

    stake_address = "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"
    delegator1 = make_delegator_with_delegation_history(
        pool, stake_address, stake_amount=100000)

    if count_delegators > 1:
        stake_address2 = "stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c"
        delegator2 = make_delegator_with_delegation_history(
            pool, stake_address2, stake_amount=500000)
        delegators = [delegator1, delegator2]
    else:
        delegators = [delegator1]

    lottery_strategy_factory = LotteryStrategyFactory()
    lottery_strategy = lottery_strategy_factory.createLotteryStrategy(
        lottery_strategy_name, min_live_stake=min_live_stake)

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
        lottery_strategy_type=lottery_strategy_name,
        lottery_strategy=lottery_strategy,
        owners_allowed=True,
        min_live_stake=min_live_stake
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


def test_prepare_fixed_lottery_tickets_list_2_delegators_high_min_live_stake():
    # Arrange
    delegators, lottery, pool = create_lottery_tickets_x_delegator(
        2, "Fixed", min_live_stake=5000)

    # Act/Assert
    with pytest.raises(OutOfDelegator, match="Out of Delegator for lottery"):
        lottery_tickets = prepare_lottery_tickets_list(
            delegators, lottery, pool)


def test_prepare_fixed_lottery_tickets_list_2_delegators_low_min_live_stake():
    # Arrange
    delegators, lottery, pool = create_lottery_tickets_x_delegator(
        2, "Fixed", min_live_stake=500)

    expected_probabilitlies = 1 / len(delegators)

    # Act
    lottery_tickets = prepare_lottery_tickets_list(delegators, lottery, pool)

    # Assert
    for lottery_ticket in lottery_tickets:
        assert lottery_ticket.winning_likelyhood == expected_probabilitlies


def test_prepare_stake_lottery_tickets_2_delegators():
    # Arrange
    delegators, lottery, pool = create_lottery_tickets_x_delegator(2, "Stake")

    expected_probabilitlies = [0.3003992015968064, 0.6996007984031936]

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


def test_is_pool_a_match():
    pool = make_pool()

    assert pool.is_pool_a_match("Hippo") == True
    assert pool.is_pool_a_match("Hippo1") == False
    assert pool.is_pool_a_match("HIPPO") == True
    assert pool.is_pool_a_match(
        "pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g") == True
    assert pool.is_pool_a_match(
        "pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r781") == False
