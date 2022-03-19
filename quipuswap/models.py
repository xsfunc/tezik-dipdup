from enum import IntEnum

from tortoise.models import Model
from tortoise import fields


class TradeSide(IntEnum):
    BUY = 1
    SELL = 0


class Trade(Model):
    id = fields.IntField(pk=True)
    # token_id = fields.IntField(index=True)
    token_address = fields.CharField(max_length=60, index=True)
    trader = fields.CharField(36)
    side = fields.IntEnumField(enum_type=TradeSide)
    quantity = fields.DecimalField(decimal_places=0, max_digits=30)
    price = fields.DecimalField(decimal_places=6, max_digits=30)
    slippage = fields.DecimalField(decimal_places=6, max_digits=30)
    level = fields.BigIntField()
    timestamp = fields.DatetimeField(index=True)


class Position(Model):
    id = fields.IntField(pk=True)
    symbol = fields.CharField(max_length=10)
    trader = fields.CharField(36)
    shares_qty = fields.BigIntField(default=0)
    avg_share_px = fields.DecimalField(decimal_places=6, max_digits=20, default=0)
    realized_pl = fields.DecimalField(decimal_places=6, max_digits=20, default=0)
