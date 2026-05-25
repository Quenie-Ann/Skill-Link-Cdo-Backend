#  workers/management/commands/enforce_rate_bands.py

from django.core.management.base import BaseCommand
from workers.models import WorkerProfile, SkillCategory, RateBand
 
 
class Command(BaseCommand):
    help = (
        'Check all verified/pending workers against the current rate band '
        'for their skill category and flag any whose declared_rate falls outside it.'
    )
 
    def add_arguments(self, parser):
        parser.add_argument(
            '--category',
            type=str,
            default=None,
            help='Limit check to a single category name (exact match).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Print what would be flagged without saving changes.',
        )
 
    def handle(self, *args, **options):
        target_name = options['category']
        dry_run     = options['dry_run']
 
        categories = SkillCategory.objects.filter(is_active=True)
        if target_name:
            categories = categories.filter(category_name__iexact=target_name)
            if not categories.exists():
                self.stderr.write(f'Category "{target_name}" not found.')
                return
 
        total_flagged   = 0
        total_cleared   = 0
        total_no_band   = 0
 
        for cat in categories:
            band = RateBand.objects.filter(
                category=cat
            ).order_by('-effective_date').first()
 
            if not band:
                self.stdout.write(
                    self.style.WARNING(
                        f'  [SKIP] {cat.category_name} — no rate band set.'
                    )
                )
                total_no_band += 1
                continue
 
            self.stdout.write(
                f'\n[{cat.category_name}]  band: ₱{band.min_rate} – ₱{band.max_rate}'
            )
 
            workers = WorkerProfile.objects.filter(
                skill_category=cat,
                verification_status__in=['pending', 'verified'],
                is_suspended=False,
            )
 
            for w in workers:
                out_of_band = (
                    w.declared_rate < band.min_rate or
                    w.declared_rate > band.max_rate
                )
 
                if out_of_band:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  FLAG  {w.full_name}  '
                            f'(₱{w.declared_rate})  '
                            f'→ outside [₱{band.min_rate}, ₱{band.max_rate}]'
                        )
                    )
                    if not dry_run:
                        w.verification_status = 'flagged'
                        w.save(update_fields=['verification_status'])
                    total_flagged += 1
 
                elif w.verification_status == 'flagged':
                    # Rate was previously out-of-band but is now within the
                    # new band — auto-clear the flag back to pending so the
                    # admin can re-verify.
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  CLEAR {w.full_name}  '
                            f'(₱{w.declared_rate})  '
                            f'→ now within band, reset to pending'
                        )
                    )
                    if not dry_run:
                        w.verification_status = 'pending'
                        w.save(update_fields=['verification_status'])
                    total_cleared += 1
 
        self.stdout.write('\n' + '─' * 50)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no changes saved.'))
 
        self.stdout.write(
            f'Workers flagged : {total_flagged}\n'
            f'Flags cleared   : {total_cleared}\n'
            f'No band set     : {total_no_band} categories skipped'
        )