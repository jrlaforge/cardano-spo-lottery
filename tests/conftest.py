import time
from datetime import datetime
from pathlib import Path
from typing import List

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, clear_mappers

import spolottery.config as config
from spolottery.domain.models import Delegation, Delegator, Pool, PoolOwner, LotteryStrategyFactory, Lottery, LotteryTicket
from spolottery.adapters.orm import start_mappers, metadata


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


def make_delegator_with_delegation_history(pool, stake_address, stake_amount=0):

    delegation1 = Delegation(
        pool_id=pool.pool_id,
        amount=(stake_amount + 100000),
        epoch_no=300,
    )
    delegation2 = Delegation(
        pool_id=pool.pool_id,
        amount=(stake_amount + 200000),
        epoch_no=305,
    )

    another_pool_id = "ea90b56d9c4d04c583ec728c8b415948b310d4653d12bd281aaff9df"
    delegation3 = Delegation(
        pool_id=another_pool_id,
        amount=(stake_amount + 300000),
        epoch_no=307,
    )

    delegation4 = Delegation(
        pool_id=pool.pool_id,
        amount=(1000),
        epoch_no=308,
    )

    delegator = Delegator(
        address_id=stake_address,
        delegation_history=[delegation1,
                            delegation2, delegation3, delegation4],
        live_stake=1000
    )

    return delegator


def make_pool():
    pool = Pool(
        pool_id="pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g",
        hex="718f15efee599d498a7582c4f56a940cfebffc14e850656db8d529e1",
        url="https://hippo-pool.com/",
        ticker="HIPPO",
        name="Hippo Pool",
        description="Come in, Relax and Earn a max",
        updated_at=datetime.strptime(
            "2022-01-24 13:55:47", "%Y-%m-%d %H:%M:%S"),
    )

    pool.add_pool_owner(PoolOwner(
        address_id="stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4", pool_id=pool.pool_id))
    pool.add_pool_owner(PoolOwner(
        address_id="stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c", pool_id=pool.pool_id))

    return pool


def make_fake_duplicate_hippo_pool():

    pool = make_pool()
    pool.pool_id = "pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r787"
    pool.ticker = "HIPPO fake"

    return pool


def make_pool_block():
    pool = Pool(
        pool_id="pool1cc76kmtcpf6vht32ya5ke9er74dnpy4jh5qpy4klqwp87ygdsu6",
        hex="c63dab6d780a74cbae2a27696c9723f55b3092b2bd001256df03827f",
        url="https://kblocks.net/",
        ticker="BLOCK",
        name="kBlocks",
        description="We want to change the world #WomenInBlockchain",
        updated_at=datetime.strptime(
            "2022-01-24 13:55:47", "%Y-%m-%d %H:%M:%S"),
    )

    pool.add_pool_owner(PoolOwner(
        address_id="stake1uyqkpllunxtg98w0em0l2pgyp4etf6mnh2h9qzzr8laucdsehed4k", pool_id=pool.pool_id))

    return pool


def make_delegators() -> List[Delegator]:
    pool = make_pool()
    different_live_stakes = True
    live_stake = 0 if not different_live_stakes else 500000
    stake_address_delegator1 = "stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c"
    delegator1 = make_delegator_with_delegation_history(
        pool, stake_address_delegator1, live_stake)
    stake_address_delegator2 = "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"
    live_stake = 0 if not different_live_stakes else 1000000
    delegator2 = make_delegator_with_delegation_history(
        pool, stake_address_delegator2, live_stake)
    stake_address_delegator3 = "stake1u9yrn7z2g0ynx4wtpqfuv7fj3uuasavtzg6ulfv2f647jhcluzuur"
    live_stake = 0 if not different_live_stakes else 10000
    delegator3 = make_delegator_with_delegation_history(
        pool, stake_address_delegator3, live_stake)

    return [delegator1, delegator2, delegator3]


def make_lottery(strategy_type=None, different_live_stakes=False, min_live_stake=0, with_tickets=False):

    uuid = "abd1acef-c472-4444-bb17-e356a41a560b"
    pool = make_pool()
    name = "Test lottery 1"
    now = datetime.now()
    lottery_strategy_factory = LotteryStrategyFactory()
    lottery_strategy = lottery_strategy_factory.createLotteryStrategy(
        strategy_type, min_live_stake)

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
        lottery_strategy_type=strategy_type,
        lottery_strategy=lottery_strategy,
        owners_allowed=True,
        min_live_stake=min_live_stake,
    )

    live_stake = 0 if not different_live_stakes else 500000
    stake_address_delegator1 = "stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c"
    delegator1 = make_delegator_with_delegation_history(
        pool, stake_address_delegator1, live_stake)
    stake_address_delegator2 = "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"
    live_stake = 0 if not different_live_stakes else 1000000
    delegator2 = make_delegator_with_delegation_history(
        pool, stake_address_delegator2, live_stake)
    stake_address_delegator3 = "stake1u9yrn7z2g0ynx4wtpqfuv7fj3uuasavtzg6ulfv2f647jhcluzuur"
    live_stake = 0 if not different_live_stakes else 10000
    delegator3 = make_delegator_with_delegation_history(
        pool, stake_address_delegator3, live_stake)
    delegators = [(delegator1, 0.5), (delegator2, 0.25), (delegator3, 0.25)]

    lottery_tickets = []
    for delegator in delegators:
        lottery_tickets.append(
            LotteryTicket(
                delegator_id=delegator[0].address_id,
                winning_likelyhood=delegator[1],
                pool_owner=True,
                lottery_id=lottery.uuid,
                delegator_lottery_stake=None
            )
        )
    if with_tickets:
        lottery.lottery_tickets = lottery_tickets

    return lottery


def insert_strategy_types(session):
    session.execute(
        "INSERT INTO lottery_strategy_types (name)" ' VALUES ("Fixed"), ("Stake")')


def insert_pool(session, pool_id=""):
    if not pool_id:
        pool_id = "pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g"

    session.execute(
        "INSERT INTO pools (pool_id, hex, url, ticker, name, description, updated_at)"
        " VALUES (:pool_id,"
        '"718f15efee599d498a7582c4f56a940cfebffc14e850656db8d529e1",'
        '"https://hippo-pool.com/",'
        '"HIPPO",'
        '"Hippo Pool",'
        '"Come in, Relax and Earn a max",'
        '"2022-01-24 13:55:47")',
        dict(pool_id=pool_id),
    )

    [[pool_id]] = session.execute(
        "SELECT pool_id FROM pools WHERE pool_id=:pool_id",
        dict(pool_id=pool_id),
    )

    return pool_id


def insert_pool_owners(session):
    session.execute(
        "INSERT INTO pool_owners (address_id, pool_id)"
        ' VALUES ("stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4",'
        '"pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g")'
    )
    session.execute(
        "INSERT INTO pool_owners (address_id, pool_id)"
        ' VALUES ("stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c",'
        '"pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g")'
    )


def insert_delegator(session):
    address_id = "stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"

    session.execute("INSERT INTO delegators (address_id)" " VALUES (:address_id)", dict(
        address_id=address_id))

    [[delegator_id]] = session.execute(
        "SELECT address_id FROM delegators WHERE address_id=:address_id",
        dict(address_id=address_id),
    )

    return delegator_id


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


@pytest.fixture(scope="session")
def postgres_db():
    engine = create_engine(config.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db):
    start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture
def add_pools(postgres_session):
    pools_added = set()

    def _add_pool(lines):
        for pool_id, hex, url, ticker, name, description, updated_at in lines:
            postgres_session.execute(
                "INSERT INTO pools (pool_id, hex, url, ticker, name, description, updated_at)"
                " VALUES (:pool_id, :hex, :url, :ticker, :name, :description, :updated_at)",
                dict(pool_id=pool_id, hex=hex, url=url, ticker=ticker,
                     name=name, description=description, updated_at=updated_at),
            )
            [[pool_id]] = postgres_session.execute(
                "SELECT pool_id FROM pools WHERE pool_id=:pool_id",
                dict(pool_id=pool_id),
            )
            pools_added.add(pool_id)
        postgres_session.commit()

    yield _add_pool

    for pool_id in pools_added:
        postgres_session.execute(
            "DELETE FROM pools WHERE pool_id=:pool_id",
            dict(pool_id=pool_id),
        )

        postgres_session.commit()


@pytest.fixture
def add_pool_owners(postgres_session):
    pool_owners_added = set()

    def _add_pool_owner(lines):
        for address_id, pool_id in lines:
            postgres_session.execute(
                "INSERT INTO pool_owners (address_id, pool_id)"
                " VALUES (:address_id, :pool_id)",
                dict(address_id=address_id, pool_id=pool_id),
            )
            [[pool_owner_id]] = postgres_session.execute(
                "SELECT address_id FROM pool_owners WHERE address_id=:address_id",
                dict(address_id=address_id),
            )
            pool_owners_added.add(pool_owner_id)
        postgres_session.commit()

    yield _add_pool_owner

    for pool_id in pool_owners_added:
        postgres_session.execute(
            "DELETE FROM pools WHERE pool_id=:pool_id",
            dict(pool_id=pool_id),
        )

        postgres_session.commit()
