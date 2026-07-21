from django.core.management.base import BaseCommand
from datetime import date, timedelta
from massage_app.models import Booking, DailyBookingStat

class Command(BaseCommand):
    help = 'Rebuild DailyBookingStat rows starting from today for N days (default 30)'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Number of days from today to create stats for')
        parser.add_argument('--wipe-old', action='store_true', help='Delete DailyBookingStat rows outside the generated range')

    def handle(self, *args, **options):
        days = options['days']
        wipe_old = options.get('wipe_old', False)
        today = date.today()
        start = today
        end = today + timedelta(days=days - 1)
        self.stdout.write(f'Rebuilding DailyBookingStat for {days} days: {start} .. {end}')

        created_or_updated = 0
        for i in range(days):
            d = start + timedelta(days=i)
            # Count bookings by creation date (created_at) so stats reflect when bookings were submitted
            cnt = Booking.objects.filter(created_at__date=d).count()
            stat, created = DailyBookingStat.objects.update_or_create(date=d, defaults={'total_bookings': cnt})
            created_or_updated += 1
            self.stdout.write(f'  {d}: {cnt} bookings -> stat id={stat.pk}')

        if wipe_old:
            # remove stats outside the new window (keep only dates in [start, end])
            removed = DailyBookingStat.objects.exclude(date__range=(start, end)).delete()
            # .delete() returns a tuple (num_deleted, {<model>: num}) — print the summary
            self.stdout.write(f'Removed old stats: {removed}')

        self.stdout.write(self.style.SUCCESS(f'Done. Created/updated {created_or_updated} rows.'))
