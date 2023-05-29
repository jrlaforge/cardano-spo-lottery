from spolottery.adapters import repository
from tests.conftest import make_pool, insert_pool, make_delegator_with_delegation_history, insert_delegator


# POOL
def test_repository_can_save_a_pool(session):

    pool = make_pool()

    pool_repo = repository.SqlAlchemyPoolRepository(session)

    pool_repo.add(pool)

    session.commit()

    rows = session.execute('SELECT pool_id, hex, ticker, name from "pools"')

    assert list(rows) == [(pool.pool_id, pool.hex, pool.ticker, pool.name)]


def test_repository_retreive_a_pool(session):

    pool_id = insert_pool(session)

    pool_repo = repository.SqlAlchemyPoolRepository(session)

    pool = pool_repo.get(pool_id)

    assert pool_id == pool.pool_id


# Delegator


def test_repository_can_save_a_delegator(session):

    pool = make_pool()

    stake_address_delegator1 = "stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c"
    delegator1 = make_delegator_with_delegation_history(
        pool, stake_address_delegator1)

    delegator_repo = repository.SqlAlchemyDelegatorRepository(session)

    delegator_repo.add(delegator1)

    session.commit()

    rows = session.execute('SELECT address_id from "delegators"')

    assert list(rows) == [(stake_address_delegator1,)]


def test_repository_retrieve_a_delegator(session):

    delegator_id = insert_delegator(session)

    delegator_repo = repository.SqlAlchemyDelegatorRepository(session)

    delegator = delegator_repo.get(delegator_id)

    assert delegator_id == delegator.address_id
