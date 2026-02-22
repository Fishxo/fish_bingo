"""
Prune old records to free disk space.
Keeps only last N records per model.
NEVER touches users or financial transactions.
"""

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = (
        "Prune old records (games, transfers, withdraws, deposits, broadcasts). "
        "Keeps last N records. Never touches users or transactions."
    )

    def add_arguments(self, parser):
        parser.add_argument('--keep', type=int, default=20)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        keep = max(1, options['keep'])
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no data will be deleted"))

        from api.models import (
            Game,
            Transfer,
            WithdrawRequest,
            DepositRequest,
            BroadcastMessage,
        )

        total_deleted = 0

        with transaction.atomic():

            # ---------- Games ----------
            keep_ids = set(
                Game.objects.order_by('-created_at')
                .values_list('id', flat=True)[:keep]
            )
            active_ids = set(
                Game.objects.filter(status__in=['waiting', 'active'])
                .values_list('id', flat=True)
            )

            keep_ids |= active_ids
            qs = Game.objects.exclude(id__in=keep_ids)
            count = qs.count()
            if count and not dry_run:
                qs.delete()
            total_deleted += count
            self.stdout.write(f"Games deleted: {count}")

            # ---------- Transfers ----------
            qs = Transfer.objects.exclude(
                id__in=Transfer.objects.order_by('-created_at')
                .values_list('id', flat=True)[:keep]
            )
            count = qs.count()
            if count and not dry_run:
                qs.delete()
            total_deleted += count
            self.stdout.write(f"Transfers deleted: {count}")

            # ---------- Withdraw Requests ----------
            qs = WithdrawRequest.objects.exclude(
                id__in=WithdrawRequest.objects.order_by('-created_at')
                .values_list('id', flat=True)[:keep]
            )
            count = qs.count()
            if count and not dry_run:
                qs.delete()
            total_deleted += count
            self.stdout.write(f"WithdrawRequests deleted: {count}")

            # ---------- Deposit Requests ----------
            qs = DepositRequest.objects.exclude(
                id__in=DepositRequest.objects.order_by('-created_at')
                .values_list('id', flat=True)[:keep]
            )
            count = qs.count()
            if count and not dry_run:
                qs.delete()
            total_deleted += count
            self.stdout.write(f"DepositRequests deleted: {count}")

            # ---------- Broadcast Messages ----------
            qs = BroadcastMessage.objects.exclude(
                id__in=BroadcastMessage.objects.order_by('-created_at')
                .values_list('id', flat=True)[:keep]
            )
            count = qs.count()
            if count and not dry_run:
                qs.delete()
            total_deleted += count
            self.stdout.write(f"BroadcastMessages deleted: {count}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Total rows {'to be deleted' if dry_run else 'deleted'}: {total_deleted}"
            )
        )
