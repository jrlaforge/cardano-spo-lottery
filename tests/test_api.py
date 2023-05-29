from datetime import datetime

import pytest
import requests

import spolottery.config as config
from tests.conftest import make_pool, make_pool_block, make_fake_duplicate_hippo_pool
from spolottery.domain.models import Delegator


@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_200_and_a_pool(postgres_session):
    postgres_session.execute(
        "DELETE FROM pool_owners"
    )

    postgres_session.execute(
        "DELETE FROM delegators"
    )

    postgres_session.execute(
        "DELETE FROM pools"
    )
    postgres_session.commit()

    hippo_pool = make_pool()

    block_pool = make_pool_block()

    hippo_fake_pool = make_fake_duplicate_hippo_pool()

    all_pools = [hippo_pool, block_pool, hippo_fake_pool]

    delegators = set()
    for pool in all_pools:
        for owner in pool.owners:
            delegators.add(Delegator(owner.address_id))

    for delegator in delegators:
        postgres_session.add(delegator)

    postgres_session.add(hippo_pool)
    postgres_session.add(block_pool)
    postgres_session.add(hippo_fake_pool)
    postgres_session.commit()

    # add_pools(
    #     [
    #         ("pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g","718f15efee599d498a7582c4f56a940cfebffc14e850656db8d529e1","https://hippo-pool.com/","HIPPO","Hippo Pool","Come in, Relax and Earn a max",datetime.strptime("2022-01-24 13:55:47", "%Y-%m-%d %H:%M:%S")),
    #         ("pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r77g","718f15efee599d498a7582c4f56a940cfebffc14e850656db8d529e1","https://hippo-pool.com/","HIPPO 2","Hippo 2 Pool","Come in, Relax and Earn a max",datetime.strptime("2022-01-24 13:55:47", "%Y-%m-%d %H:%M:%S")),
    #         ("pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r79g","718f15efee599d498a7582c4f56a940cfebffc14e850656db8d529e1","https://hippo-pool.com/","FAKE HIPPO","Hippo Pool","Come in, Relax and Earn a max",datetime.strptime("2022-01-24 13:55:47", "%Y-%m-%d %H:%M:%S")),
    #         ("pool1cc76kmtcpf6vht32ya5ke9er74dnpy4jh5qpy4klqwp87ygdsu6","c63dab6d780a74cbae2a27696c9723f55b3092b2bd001256df03827f", "https://kblocks.net/", "BLOCK", "kBlocks", "We want to change the world #WomenInBlockchain",datetime.strptime("2022-01-24 13:55:47","%Y-%m-%d %H:%M:%S"))
    #     ]
    # )
    #
    # add_pool_owners([("stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4", "pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g"),
    #                  ("stake1Syfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z5", "pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r77g"),
    #                  ("stake1Ryfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z6", "pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r79g"),
    #                  ("stake18yfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z7", "pool1cc76kmtcpf6vht32ya5ke9er74dnpy4jh5qpy4klqwp87ygdsu6"),])

    data = {"pool_filter": "HIPPO"}
    url = config.get_api_url()

    res = requests.post(f"{url}/pool/filter", json=data)

    assert res.status_code == 200

    pool_results = res.json()["pools"]

    assert set([pool['pool_id'] for pool in pool_results]) == set(
        [hippo_pool.pool_id, hippo_fake_pool.pool_id])
