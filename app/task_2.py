from datetime import datetime

from peewee import (
    CharField,
    Check,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
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
    direction = CharField(constraints=[Check('direction in ("in", "out")')])
    amount = IntegerField()
    created = DateTimeField()

    class Meta:
        database = db


def get_user_transcations_in_period(
    user_id: int, since: datetime, till: datetime
) -> list[Transaction]:
    transactions = Transaction.select().where(
        Transaction.owner_id == user_id, Transaction.created.between(since, till)
    )
    return list(transactions)


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
        amount=100,
        created=datetime(2023, 7, 21),
    )
    print(
        get_user_transcations_in_period(
            user_id=1, since=datetime(2023, 7, 5), till=datetime(2023, 7, 20)
        )
    )
