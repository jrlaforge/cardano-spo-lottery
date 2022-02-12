from datetime import datetime

import models
from conftest import make_pool


def insert_pool(session):
    session.execute(
        "INSERT INTO pools (pool_id, hex, url, ticker, name, description, updated_at)"
        ' VALUES ("pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g",'
        '"718f15efee599d498a7582c4f56a940cfebffc14e850656db8d529e1",'
        '"https://hippo-pool.com/",'
        '"HIPPO",'
        '"Hippo Pool",'
        '"Come in, Relax and Earn a max",'
        '"2022-01-24 13:55:47")'
    )


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
        updated_at=datetime.strptime("2022-01-24 13:55:47", "%Y-%m-%d %H:%M:%S"),
    )
    session.add(pool)
    session.commit()
    rows = session.execute('SELECT pool_id, name, url  FROM "pools"')
    assert list(rows) == [
        ("pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g", "Hippo Pool", "https://hippo-pool.com/")
    ]


def test_saving_pool_owners(session):
    pool = models.Pool(
        pool_id="pool1wx83tmlwtxw5nzn4stz02655pnltllq5apgx2mdc6557zw0r78g",
        hex="718f15efee599d498a7582c4f56a940cfebffc14e850656db8d529e1",
        url="https://hippo-pool.com/",
        ticker="HIPPO",
        name="Hippo Pool",
        description="Come in, Relax and Earn a max",
        updated_at=datetime.strptime("2022-01-24 13:55:47", "%Y-%m-%d %H:%M:%S"),
    )

    pool.add_pool_owner(models.PoolOwner("stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"))
    pool.add_pool_owner(models.PoolOwner("stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c"))

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
        models.PoolOwner("stake1uyfy0mj0n57wl87tj6anj2mhge40n3tjhwx0exj9r7k97egvjq0z4"),
        models.PoolOwner("stake1ux393u69v33gl9pumdaxdu9kpmresdnjc76gjnfphmj8uqq5jvh6c"),
    }

    assert pool.owners == expected_owners
