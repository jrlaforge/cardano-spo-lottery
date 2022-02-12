import repository
from conftest import make_pool


# def test_repository_can_save_a_pool(session):
#
#     pool = make_pool()
#     repo = repository.AbstractRepository(session)
#
#     repo.add(pool)
#
#     rows = session.execute('SELECT pool_id, hex, ticker, name from "pools"')
#
#     assert list(rows) == [(pool.pool_id, pool.hex, pool.ticker, pool.name)]
#
