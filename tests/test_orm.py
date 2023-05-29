from datetime import datetime

from spolottery.domain import models
from tests.conftest import make_pool, make_lottery, insert_pool, insert_pool_owners


def test_retrieve_pool(session):
    insert_pool(session)

    expected = [make_pool()]

    assert session.query(models.Pool).all() == expected


def test_saving_pool(session):
    pool = models.Pool(
        pool_id="pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g",
        hex="718f15efee599d498a7582c4f56a940cfebffc14e850656db8d529e1",
        url="https://hippo-pool.com/",
        ticker="HIPPO",
        name="Hippo Pool",
        description="Come in, Relax and Earn a max",
        updated_at=datetime.strptime(
            "2022-01-24 13:55:47", "%Y-%m-%d %H:%M:%S"),
    )
    session.add(pool)
    session.commit()
    rows = session.execute('SELECT pool_id, name, url  FROM "pools"')
    assert list(rows) == [
        ("pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g",
         "Hippo Pool", "https://hippo-pool.com/")
    ]


def test_saving_pool_owners(session):

    pool = make_pool()

    session.add(pool)
    session.commit()
    rows = session.execute('SELECT address_id, pool_id  FROM "pool_owners"')

    expected = {
        (
            "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4",
            "pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g",
        ),
        (
            "stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c",
            "pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g",
        ),
    }

    assert set(rows) == expected


def test_retrieving_pool_owners(session):

    insert_pool(session)

    insert_pool_owners(session)

    pool = session.query(models.Pool).one()

    expected_owners = {
        models.PoolOwner(
            "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4", pool_id=pool.pool_id),
        models.PoolOwner(
            "stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c", pool_id=pool.pool_id),
    }

    assert pool.owners == expected_owners


def test_saving_lottery(session):

    lottery = make_lottery()

    session.add(lottery)
    session.commit()
    rows = session.execute('SELECT uuid, pool_id  FROM "lotteries"')

    expected = [("abd1acef-c472-4444-bb17-e356a41a560b",
                 "pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g")]

    assert list(rows) == expected


def test_saving_lottery_with_raffle(session):

    lottery = make_lottery()

    lottery.raffle_draw()

    session.add(lottery)
    session.commit()

    rows = session.execute(
        'SELECT delegator_address_id, rank  FROM "lottery_winners"')

    expected = {
        ("stake1u9yrn7z2g0ynx4wtpqfuv7fj3uuasavtzg6ulfv2f647jhcluzuur", 2),
        ("stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4", 1),
        ("stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c", 0),
    }

    assert set(rows) == expected


def test_retrieve_lottery(session):

    lottery = make_lottery()

    lottery.raffle_draw()

    session.add(lottery)
    session.commit()

    lottery_db = session.query(models.Lottery).one()

    expected_winners = lottery.winners
    expected_lottery_tickets = lottery.lottery_tickets

    assert lottery_db.winners == expected_winners
    assert lottery_db.lottery_tickets == expected_lottery_tickets
