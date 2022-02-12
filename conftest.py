from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from models import Delegation, Delegator, Pool, PoolOwner
from orm import start_mappers, metadata


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
        address_id=stake_address,
        pool_id=pool.pool_id,
        amount=(stake_amount + 100000),
        epoch_no=300,
    )
    delegation2 = Delegation(
        address_id=stake_address,
        pool_id=pool.pool_id,
        amount=(stake_amount + 200000),
        epoch_no=305,
    )

    another_pool_id = "ea90b56d9c4d04c583ec728c8b415948b310d4653d12bd281aaff9df"
    delegation3 = Delegation(
        address_id=stake_address,
        pool_id=another_pool_id,
        amount=(stake_amount + 300000),
        epoch_no=307,
    )

    delegator = Delegator(
        address_id=stake_address,
        delegation_history=[delegation1, delegation2, delegation3],
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
        updated_at=datetime.strptime("2022-01-24 13:55:47", "%Y-%m-%d %H:%M:%S"),
    )

    pool.add_pool_owner(PoolOwner("stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"))
    pool.add_pool_owner(PoolOwner("stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c"))

    return pool
