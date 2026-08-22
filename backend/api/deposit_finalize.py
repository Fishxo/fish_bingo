"""Atomic deposit finalization after Telebirr/CBE verification."""
import logging
import re
from decimal import Decimal, InvalidOperation

from django.db import transaction

logger = logging.getLogger(__name__)


def parse_api_amount(value) -> Decimal | None:
    """Parse amount from verify API (plain number, '500 ETB', '1,234.56', etc.)."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    s = re.sub(r'[^0-9.,-]', '', s.replace(',', ''))
    if not s:
        return None
    try:
        amount = Decimal(s)
    except (InvalidOperation, ValueError):
        return None
    return amount if amount > 0 else None


@transaction.atomic
def finalize_telebirr_deposit(user, reference: str, amount: Decimal, deposit_text: str):
    """Save receipt, credit user, and record transaction in one atomic step."""
    from .models import TelebirrReceipt, Transaction, DepositRequest
    from .stats_utils import credit_deposit

    TelebirrReceipt.objects.create(user=user, reference=reference, amount=amount)
    credit_deposit(amount, user)
    user.refresh_from_db()
    Transaction.objects.create(
        user=user,
        transaction_type='deposit',
        amount=amount,
        description=f'Telebirr deposit verified - Ref: {reference}',
    )
    DepositRequest.objects.create(
        user=user,
        amount=amount,
        platform='Telebirr',
        deposit_text=(deposit_text or '')[:2000],
        status='approved',
    )


@transaction.atomic
def finalize_cbe_deposit(
    user,
    reference: str,
    account_suffix: str,
    amount: Decimal,
    deposit_text: str,
):
    """Save receipt, credit user, and record transaction in one atomic step."""
    from .models import CbeReceipt, Transaction, DepositRequest
    from .stats_utils import credit_deposit

    CbeReceipt.objects.create(
        user=user,
        reference=reference,
        account_suffix=account_suffix,
        amount=amount,
    )
    credit_deposit(amount, user)
    user.refresh_from_db()
    Transaction.objects.create(
        user=user,
        transaction_type='deposit',
        amount=amount,
        description=f'CBE deposit verified - Ref: {reference}',
    )
    DepositRequest.objects.create(
        user=user,
        amount=amount,
        platform='CBE',
        deposit_text=(deposit_text or '')[:2000],
        status='approved',
    )
