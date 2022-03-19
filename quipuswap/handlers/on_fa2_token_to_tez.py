from decimal import Decimal
from typing import cast

from dipdup.context import HandlerContext
from dipdup.models import OperationData
from dipdup.models import Transaction

from quipuswap import models
from quipuswap.types.fa2_token.storage import Fa2TokenStorage
from quipuswap.types.quipu_fa2.storage import QuipuFa2Storage
from quipuswap.types.fa2_token.parameter.transfer import TransferParameter
from quipuswap.types.quipu_fa2.parameter.token_to_tez_payment import (
    TokenToTezPaymentParameter,
)


async def on_fa2_token_to_tez(
    ctx: HandlerContext,
    token_to_tez_payment: Transaction[TokenToTezPaymentParameter, QuipuFa2Storage],
    transfer: Transaction[TransferParameter, Fa2TokenStorage],
    transaction_0: OperationData,
) -> None:
    symbol = cast(str, ctx.template_values["symbol"])
    decimals = int(ctx.template_values["decimals"])
    trader = token_to_tez_payment.data.sender_address

    transfer_params = transfer.parameter.__root__[0].txs[0]
    token_id = int(transfer_params.token_id)
    token_amount = Decimal(transfer_params.amount) / (10**decimals)

    min_tez = Decimal(token_to_tez_payment.parameter.min_out) / (10**6)
    tez_amount = Decimal(transaction_0.amount) / (10**6)

    price = tez_amount / token_amount
    slippage = (1 - (min_tez / tez_amount)).quantize(Decimal("0.000001"))

    trade = models.Trade(
        symbol=symbol,
        trader=trader,
        side=models.TradeSide.SELL,
        quantity=token_amount,
        price=price,
        slippage=slippage,
        level=transfer.data.level,
        token_address=f'{transfer.data.target_address}_{token_id}',
        timestamp=transfer.data.timestamp,
    )
    await trade.save()
