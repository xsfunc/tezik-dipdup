from decimal import Decimal
from typing import cast

from dipdup.context import HandlerContext
from dipdup.models import Transaction

from quipuswap import models
from quipuswap.types.quipu_fa12.storage import QuipuFa12Storage
from quipuswap.types.fa12_token.parameter.transfer import TransferParameter
from quipuswap.types.fa12_token.storage import Fa12TokenStorage
from quipuswap.types.quipu_fa12.parameter.tez_to_token_payment import (
    TezToTokenPaymentParameter,
)


async def on_fa12_tez_to_token(
    ctx: HandlerContext,
    tez_to_token_payment: Transaction[TezToTokenPaymentParameter, QuipuFa12Storage],
    transfer: Transaction[TransferParameter, Fa12TokenStorage],
) -> None:
    decimals = int(ctx.template_values["decimals"])
    symbol = cast(str, ctx.template_values["symbol"])
    trader = tez_to_token_payment.data.sender_address
    token_id = 0

    min_token = Decimal(tez_to_token_payment.parameter.min_out) / (10**decimals)
    token_amount = Decimal(transfer.parameter.value) / (10**decimals)
    tez_amount = Decimal(tez_to_token_payment.data.amount) / (10**6)

    slippage = 1 - (min_token / token_amount)
    price = tez_amount / token_amount

    trade = models.Trade(
        symbol=symbol,
        trader=trader,
        side=models.TradeSide.BUY,
        quantity=token_amount,
        price=price,
        slippage=slippage,
        token_address=f'{transfer.data.target_address}_{token_id}',
        level=transfer.data.level,
        timestamp=transfer.data.timestamp,
    )

    await trade.save()
