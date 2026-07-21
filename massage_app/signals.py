from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking, DailyBookingStat, MonthlyRevenue

@receiver(pre_save, sender=Booking)
def store_previous_status(sender, instance, **kwargs):
    """Store previous status on the instance before save so post_save can compare."""
    if instance.pk:
        try:
            prev = Booking.objects.get(pk=instance.pk)
            instance._previous_status = prev.status
            instance._previous_date = prev.date
            instance._previous_price = prev.price
        except Booking.DoesNotExist:
            instance._previous_status = None
            instance._previous_date = None
            instance._previous_price = None
    else:
        instance._previous_status = None
        instance._previous_date = None
        instance._previous_price = None


def _adjust_daily_count(target_date, delta):
    if not target_date:
        return
    stat, created = DailyBookingStat.objects.get_or_create(date=target_date)
    # use F() to avoid race conditions
    DailyBookingStat.objects.filter(pk=stat.pk).update(total_bookings=F('total_bookings') + delta)


def _adjust_monthly_revenue(target_date, amount_delta):
    if not target_date or amount_delta == 0:
        return
    year = target_date.year
    month = target_date.month
    rev, created = MonthlyRevenue.objects.get_or_create(year=year, month=month, defaults={'total_revenue': 0})
    MonthlyRevenue.objects.filter(pk=rev.pk).update(total_revenue=F('total_revenue') + amount_delta)


@receiver(post_save, sender=Booking)
def booking_post_save(sender, instance, created, **kwargs):
    """Adjust stats when bookings are updated or deleted. Do NOT add counts/revenue on create here because the booking view already updates stats.

    Signals handle: status changes (revenue only added when Completed), date changes, and other updates.
    """
    try:
        with transaction.atomic():
            # Skip created events to avoid double-counting (the view performs the initial increment)
            if created:
                return

            prev_status = getattr(instance, '_previous_status', None)
            prev_date = getattr(instance, '_previous_date', None)
            prev_price = getattr(instance, '_previous_price', None) or 0
            curr_status = instance.status

            # Revenue tracking: only add revenue when status changes TO Completed
            if prev_status != 'Completed' and curr_status == 'Completed':
                # Booking just completed - add revenue
                _adjust_monthly_revenue(instance.date, instance.price)
            
            # Revenue tracking: remove revenue if changing FROM Completed to anything else
            if prev_status == 'Completed' and curr_status != 'Completed':
                # Booking was completed but now changed - subtract revenue
                _adjust_monthly_revenue(instance.date, -instance.price)

            # If status changed to Cancelled, subtract daily count (but NOT revenue since we only count Completed)
            if prev_status != 'Cancelled' and curr_status == 'Cancelled':
                _adjust_daily_count(instance.date, -1)

            # If status changed from Cancelled to active, re-add daily count
            if prev_status == 'Cancelled' and curr_status != 'Cancelled':
                _adjust_daily_count(instance.date, 1)

            # If date changed (booking moved to another day), move the counts and revenue if Completed
            if prev_date and prev_date != instance.date:
                # remove from previous date/month
                _adjust_daily_count(prev_date, -1)
                # Only adjust revenue if booking is Completed
                if curr_status == 'Completed':
                    _adjust_monthly_revenue(prev_date, -prev_price)
                    _adjust_monthly_revenue(instance.date, instance.price)
                # add to new date/month
                _adjust_daily_count(instance.date, 1)

        # After handling stats, send acceptance email if status changed to 'Accepted'
        try:
            if instance.status == 'Accepted' and prev_status != 'Accepted':
                subject = 'Your booking has been accepted'
                message = (
                    f"Hi {instance.customer_name},\n\n"
                    f"Good news — your booking for {instance.service.name} on {instance.date} at {instance.time} "
                    f"has been accepted. We will contact you by email if anything changes.\n\n"
                    f"Thank you,\nSatori"
                )
                send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@yourdomain.com'), [instance.customer_email], fail_silently=True)
        except Exception:
            # swallow email errors to avoid breaking the save flow
            pass
    except Exception:
        # Keep booking flow robust — don't raise here
        pass


@receiver(post_delete, sender=Booking)
def booking_post_delete(sender, instance, **kwargs):
    """Adjust stats when bookings are deleted — only subtract revenue if booking was Completed."""
    try:
        with transaction.atomic():
            if instance.status != 'Cancelled':
                _adjust_daily_count(instance.date, -1)
            # Only subtract revenue if the booking was Completed
            if instance.status == 'Completed':
                _adjust_monthly_revenue(instance.date, -instance.price)
    except Exception:
        pass
