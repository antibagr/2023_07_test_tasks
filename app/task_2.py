from datetime import datetime

from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    fn,
)

db = SqliteDatabase("task_2.db")


class User(Model):
    id = IntegerField(primary_key=True)
    name = CharField()
    balance = IntegerField()
    registered = DateTimeField()

    class Meta:
        database = db


class Transaction(Model):
    id = IntegerField(primary_key=True)
    owner_id = ForeignKeyField(User, backref="transactions")
    direction = CharField(choices=["in", "out"])
    amount = IntegerField()
    created = DateTimeField(default=datetime.now)

    class Meta:
        database = db


def get_user_transcations_in_period(
    user_id: int, since: datetime, till: datetime
) -> list[Transaction]:
    transactions = Transaction.select().where(
        Transaction.owner_id == user_id, Transaction.created.between(since, till)
    )
    return list(transactions)


def get_users_with_total_transactions_in_period(
    since: datetime, till: datetime
) -> list[User]:
    users = (
        User.select(
            User.id,
            User.name,
            fn.Count(Transaction.id)
            .filter(Transaction.direction == "in")
            .alias("sum_of_input_trns"),
            fn.Count(Transaction.id)
            .filter(Transaction.direction == "out")
            .alias("sum_of_output_trns"),
        )
        .join(Transaction)
        .where(Transaction.created.between(since, till))
        .tuples()
    )
    return list(users)


if __name__ == "__main__":
    db.connect()
    db.create_tables([User, Transaction])
    user = User.create(id=1, name="John", balance=100, registered=datetime.now())
    Transaction.create(
        id=1, owner_id=user.id, direction="in", amount=100, created=datetime(2023, 7, 4)
    )
    Transaction.create(
        id=2,
        owner_id=user.id,
        direction="out",
        amount=50,
        created=datetime(2023, 7, 10),
    )
    Transaction.create(
        id=3,
        owner_id=user.id,
        direction="in",
        amount=50,
        created=datetime(2023, 7, 10),
    )
    Transaction.create(
        id=4,
        owner_id=user.id,
        direction="in",
        amount=100,
        created=datetime(2023, 7, 21),
    )
    print(
        get_users_with_total_transactions_in_period(
            since=datetime(2023, 7, 5), till=datetime(2023, 7, 20)
        )
    )
