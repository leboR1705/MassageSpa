from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail

# AJAX: Update Booking Status (Accept/Cancel/Completed)
@csrf_exempt
def update_booking_status(request, booking_id):
	from .models import Booking
	
	# Only handle POST requests, ignore GET requests (from page reloads)
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
	
	try:
		booking = get_object_or_404(Booking, id=booking_id)
	except Exception as e:
		print(f'Booking not found: {e}')
		return JsonResponse({'success': False, 'error': 'Booking not found'}, status=404)
	
	try:
		import json
		data = json.loads(request.body.decode('utf-8'))
		new_status = data.get('status')
		
		if new_status not in ['Accepted', 'Cancelled', 'Completed']:
			return JsonResponse({'success': False, 'error': 'Invalid status.'}, status=400)
			
		booking.status = new_status
		booking.save()
		
		# Send email if accepted
		if new_status == 'Accepted':
			subject = 'Your Massage Spa Booking is Accepted'
			message = f"Hello {booking.customer_name},\n\nYour booking for {booking.service.name} on {booking.date} at {booking.time} has been accepted!\n\nThank you for choosing our spa."
			from django.conf import settings as _settings
			from_email = getattr(_settings, 'DEFAULT_FROM_EMAIL', 'rodelcabanos737@gmail.com')
			recipient_list = [booking.customer_email]
			try:
				send_mail(subject, message, from_email, recipient_list, fail_silently=False)
				print(f"Email sent to {booking.customer_email} for booking {booking.id}")
			except Exception as e:
				import traceback
				print('Email send error:', e)
				traceback.print_exc()

		# Send email if cancelled
		if new_status == 'Cancelled':
			subject = 'Your Massage Spa Booking is Cancelled'
			message = f"Hello {booking.customer_name},\n\nWe're sorry to let you know your booking for {booking.service.name} on {booking.date} at {booking.time} has been cancelled. If you have questions, please contact us.\n\nRegards,\nSatori Spa"
			from django.conf import settings as _settings
			from_email = getattr(_settings, 'DEFAULT_FROM_EMAIL', 'rodelcabanos737@gmail.com')
			recipient_list = [booking.customer_email]
			try:
				send_mail(subject, message, from_email, recipient_list, fail_silently=False)
				print(f"Cancellation email sent to {booking.customer_email} for booking {booking.id}")
			except Exception as e:
				import traceback
				print('Cancellation email send error:', e)
				traceback.print_exc()
				
		return JsonResponse({'success': True})
		
	except json.JSONDecodeError as e:
		print(f'JSON decode error: {e}')
		return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
	except Exception as e:
		print(f'Status update error: {e}')
		import traceback
		traceback.print_exc()
		return JsonResponse({'success': False, 'error': str(e)}, status=400)

# Accept Booking and notify customer
@csrf_exempt
def accept_booking(request, booking_id):
	from .models import Booking
	booking = get_object_or_404(Booking, id=booking_id)
	if request.method == 'POST':
		booking.status = 'Accepted'
		booking.save()
		# Send email notification
		subject = 'Your Massage Spa Booking is Accepted'
		message = f"Hello {booking.customer_name},\n\nYour booking for {booking.service.name} on {booking.date} at {booking.time} has been accepted!\n\nThank you for choosing our spa."
		from_email = 'noreply@yourspa.com'  # Change to your sender email
		recipient_list = [booking.customer_email]
		try:
			send_mail(subject, message, from_email, recipient_list, fail_silently=False)
		except Exception as e:
			print('Email send error:', e)
		return JsonResponse({'success': True, 'message': 'Booking accepted and customer notified.'})
	return JsonResponse({'success': False, 'error': 'POST required'}, status=400)

from django.contrib.auth import authenticate, login

@csrf_exempt
def login_view(request):
	# Temporarily exempt from CSRF to unblock development testing.
	# SECURITY: revert this change and diagnose CSRF token/cookie issues before production.
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			if user.is_superuser:
				return redirect('massage_app:admin-dashboard')
			else:
				return redirect('massage_app:index')
		else:
			return render(request, 'login.html', {'error': 'Wrong username or password'})
	return render(request, 'login.html')

def logout_view(request):
	from django.contrib.auth import logout
	logout(request)
	return redirect('massage_app:login')

def mark_notifications_seen(request):
    if request.method == 'POST':
        # Mark all unseen pending bookings as notification_seen=True
        from .models import Booking
        Booking.objects.filter(status='Pending', notification_seen=False).update(notification_seen=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

from .models import Service
import re
from decimal import Decimal, InvalidOperation


def _parse_price(value):
	"""Clean a price string and return a Decimal or None.

	Removes currency symbols, commas, and whitespace. Returns None if
	the cleaned value is empty or cannot be parsed.
	"""
	if value is None:
		return None
	s = str(value).strip()
	# remove any non-digit, non-dot, non-minus characters (like ₱ and commas)
	s = re.sub(r"[^0-9.\-]", "", s)
	if s == '' or s == '.' or s == '-' or s == '-.':
		return None
	try:
		# Normalize to Decimal
		return Decimal(s)
	except (InvalidOperation, Exception):
		return None
from django.conf import settings
import time, os


def _bump_service_version():
	"""Write a timestamp to a small file so public listing pages can detect changes."""
	try:
		base = settings.BASE_DIR
		# settings.BASE_DIR may be a Path or string
		if hasattr(base, 'joinpath'):
			path = base / 'service_version.txt'
		else:
			path = os.path.join(base, 'service_version.txt')
		with open(path, 'w', encoding='utf-8') as vf:
			vf.write(str(time.time()))
	except Exception:
		pass

def _bump_booking_version():
	"""Write a timestamp to a small file so admin can detect new bookings."""
	try:
		base = settings.BASE_DIR
		if hasattr(base, 'joinpath'):
			path = base / 'booking_version.txt'
		else:
			path = os.path.join(base, 'booking_version.txt')
		with open(path, 'w', encoding='utf-8') as vf:
			vf.write(str(time.time()))
	except Exception:
		pass

def bookings_version(request):
	"""Return the current booking version (timestamp) as JSON for admin polling."""
	version = ''
	unseen_count = 0
	latest = None
	bookings_today = 0
	try:
		base = settings.BASE_DIR
		if hasattr(base, 'joinpath'):
			path = base / 'booking_version.txt'
		else:
			path = os.path.join(base, 'booking_version.txt')
		if os.path.isfile(path):
			with open(path, 'r', encoding='utf-8') as vf:
				version = vf.read().strip()
		# include unseen pending bookings count and a minimal latest booking payload
		from .models import Booking
		from datetime import date as date_cls
		unseen_count = Booking.objects.filter(status='Pending', notification_seen=False).count()
		latest_booking = Booking.objects.filter(status='Pending', notification_seen=False).order_by('-created_at').first()
		# include today's scheduled bookings so the admin stat can update live
		try:
			bookings_today = Booking.objects.filter(date=date_cls.today()).count()
		except Exception:
			bookings_today = 0
		# also include number of bookings created today (helps distinguish scheduled vs newly submitted)
		try:
			# Use localdate() to match how we record submission-day stats (timezone-aware)
			from django.utils import timezone as dj_tz
			bookings_created_today = Booking.objects.filter(created_at__date=dj_tz.localdate()).count()
		except Exception:
			bookings_created_today = 0
		if latest_booking:
			# include helpful fields for the admin popup
			try:
				service_name = ''
				if latest_booking.service:
					# service may be FK or string; prefer name attribute
					service_name = getattr(latest_booking.service, 'name', str(latest_booking.service))
			except Exception:
				service_name = ''
			latest = {
				'id': latest_booking.id,
				'customer_name': latest_booking.customer_name,
				'customer_email': getattr(latest_booking, 'customer_email', ''),
				'customer_phone': getattr(latest_booking, 'customer_phone', ''),
				'service': service_name,
				'therapist': getattr(latest_booking, 'therapist', ''),
				'price': float(latest_booking.price) if getattr(latest_booking, 'price', None) is not None else 0,
				'status': getattr(latest_booking, 'status', ''),
				'date': str(latest_booking.date),
				'time': str(latest_booking.time) if getattr(latest_booking, 'time', None) else ''
			}
	except Exception:
		version = ''
		unseen_count = 0
		latest = None
	return JsonResponse({
		'version': version,
		'unseen_count': unseen_count,
		'latest': latest,
		'bookings_today': bookings_today,
		'bookings_created_today': bookings_created_today
	})

def services_version(request):
	"""Return the current service version (timestamp) as JSON."""
	version = ''
	try:
		base = settings.BASE_DIR
		if hasattr(base, 'joinpath'):
			path = base / 'service_version.txt'
		else:
			path = os.path.join(base, 'service_version.txt')
		if os.path.isfile(path):
			with open(path, 'r', encoding='utf-8') as vf:
				version = vf.read().strip()
	except Exception:
		version = ''
	return JsonResponse({'version': version})

# Add Service
def add_service(request):
	from .models import Booking
	if request.method == 'POST':
		# Debugging: log CSRF inputs to help diagnose token failures
		try:
			print('--- add_service: incoming POST ---')
			try:
				print('Headers:', dict(request.headers))
			except Exception:
				pass
			try:
				print('POST csrfmiddlewaretoken:', request.POST.get('csrfmiddlewaretoken'))
			except Exception:
				pass
			try:
				print('Cookie csrftoken:', request.COOKIES.get('csrftoken'))
			except Exception:
				pass
			try:
				print('Is AJAX (X-Requested-With):', request.headers.get('x-requested-with'))
			except Exception:
				pass
		except Exception:
			pass
		# Support both creating a new service and updating an existing one
		service_id = request.POST.get('service_id')
		name = request.POST.get('name')
		description = request.POST.get('description')
		price = request.POST.get('price')
		duration = request.POST.get('duration')
		image = request.FILES.get('image')
		# Basic validation
		if not name or not price:
			return redirect('massage_app:admin-dashboard')
		# Update existing service if service_id provided
		if service_id:
			try:
				svc = Service.objects.get(id=service_id)
				# update fields if provided
				svc.name = name or svc.name
				svc.description = description or svc.description
				# Parse price robustly (allow ₱, commas, etc.)
				price_val = _parse_price(price)
				if price_val is not None:
					svc.price = price_val
				svc.duration = duration or svc.duration
				if image:
					# remove old image file if present
					try:
						if svc.image and hasattr(svc.image, 'path'):
							import os
							if os.path.isfile(svc.image.path):
								os.remove(svc.image.path)
					except Exception:
						pass
					svc.image = image
				svc.save()
				# notify public listing of change
				_bump_service_version()
			except Service.DoesNotExist:
				# fallback to create if not found
				Service.objects.create(name=name, description=description or '', price=price, duration=duration or '', image=image)
				_bump_service_version()
		else:
			# create with parsed price if possible
			price_val = _parse_price(price)
			if price_val is not None:
				Service.objects.create(name=name, description=description or '', price=price_val, duration=duration or '', image=image)
			else:
				Service.objects.create(name=name, description=description or '', price=price, duration=duration or '', image=image)
			_bump_service_version()
		return redirect('massage_app:admin-dashboard')
	# For non-POST fallback render (should be handled by admin_dashboard view)
	bookings = Booking.objects.all().order_by('-created_at')
	# Completed bookings for the Overview table should be a separate list
	completed_bookings = Booking.objects.filter(status='Completed').order_by('-date', '-time', '-created_at')
	services = Service.objects.all().order_by('name')
	return render(request, 'admin-dashboard.html', {'bookings': bookings, 'services': services})

# Edit Service
def edit_service(request, service_id):
	service = get_object_or_404(Service, id=service_id)
	if request.method == 'POST':
		# Debugging: print incoming headers and CSRF token info to help diagnose AJAX failures
		try:
			print('--- edit_service: incoming request ---')
			print('Headers:', dict(request.headers))
			print('POST csrfmiddlewaretoken:', request.POST.get('csrfmiddlewaretoken'))
			print('Cookie csrftoken:', request.COOKIES.get('csrftoken'))
		except Exception as _:
			pass
		try:
			print('Edit Service POST data:', dict(request.POST))
			# Update only fields that are present and non-empty
			name = request.POST.get('name')
			description = request.POST.get('description')
			price = request.POST.get('price')
			duration = request.POST.get('duration')
			image = request.FILES.get('image')
			remove_image = request.POST.get('remove_image')

			if name is not None and name.strip() != '':
				service.name = name
			if description is not None and description.strip() != '':
				service.description = description
			if price is not None and price.strip() != '':
				price_val = _parse_price(price)
				if price_val is not None:
					service.price = price_val
			if duration is not None and duration.strip() != '':
				service.duration = duration
			if image:
				# Delete old image if exists and file is present
				if service.image and hasattr(service.image, 'path'):
					try:
						import os
						if os.path.isfile(service.image.path):
							os.remove(service.image.path)
					except Exception as ex:
						print('Image delete warning:', ex)
				service.image = image
			elif remove_image == '1':
				# Remove image if requested
				if service.image and hasattr(service.image, 'path'):
					try:
						import os
						if os.path.isfile(service.image.path):
							os.remove(service.image.path)
					except Exception as ex:
						print('Image delete warning:', ex)
				service.image = None
			service.save()
			# notify public listing of change
			_bump_service_version()
			print(f"Service updated: id={service.id}, name={service.name}, price={service.price}, duration={service.duration}")
			return JsonResponse({'success': True})
		except Exception as e:
			import sys, traceback
			print('Service update error:', e)
			traceback.print_exc(file=sys.stdout)
			return JsonResponse({'success': False, 'error': str(e)})
	# Only handle POST (AJAX) for service edit; do not render template
	return JsonResponse({'error': 'GET not supported for service edit'}, status=405)

# Delete Service
from django.conf import settings
import os

def delete_service(request, service_id):
	service = get_object_or_404(Service, id=service_id)
	if request.method == 'POST':
		# Delete image file if exists
		if service.image:
			image_path = service.image.path
			if os.path.isfile(image_path):
				os.remove(image_path)

		service.delete()
		# notify public listing of change
		_bump_service_version()

		# If this was an AJAX request, return JSON so client can update UI without redirect
		is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
		if is_ajax:
			return JsonResponse({'success': True})
		return redirect('massage_app:admin-dashboard')

	return render(request, 'delete-service.html', {'service': service})
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


@csrf_exempt
def register_view(request):
	# Temporarily exempt from CSRF to unblock development testing.
	# SECURITY: remove this exemption and ensure CSRF tokens are working before production.
	if request.method == 'POST':
		username = (request.POST.get('username') or '').strip()
		email = (request.POST.get('email') or '').strip()
		password = request.POST.get('password')
		confirm = request.POST.get('confirm-password')
		# Basic validation
		if not username or not email or not password:
			return render(request, 'login.html', {'register_error': 'Username, email, and password are required.'})
		if password != confirm:
			return render(request, 'login.html', {'register_error': 'Passwords do not match.'})
		if User.objects.filter(username=username).exists():
			return render(request, 'login.html', {'register_error': 'Username already exists.'})
		if User.objects.filter(email=email).exists():
			return render(request, 'login.html', {'register_error': 'Email already exists.'})
		try:
			user = User.objects.create_user(username=username, email=email, password=password)
		except Exception as e:
			# log and show a friendly error
			print('Registration error:', e)
			return render(request, 'login.html', {'register_error': 'Could not create account; try a different username/email.'})
		# On success show register form with success message so user sees it
		return render(request, 'login.html', {'register_success': 'Registration successful! Please log in.', 'show_register': True})
def admin_dashboard(request):
	from .models import Booking, Service, DailyBookingStat, MonthlyRevenue
	from django.db.models import Sum
	from datetime import date as date_cls
	bookings = Booking.objects.all().order_by('-created_at')
	# Completed bookings separately so the Overview table can number them from 1
	completed_bookings = Booking.objects.filter(status='Completed').order_by('-date', '-time', '-created_at')
	services = Service.objects.all()  # Remove ordering to force refresh
	from .models import Employee
	employees = Employee.objects.all()  # Remove ordering to force refresh
	active_therapists = employees.filter(status='Active')
	# Always count today's bookings directly if stat is missing
	# appointment-date (scheduled) uses the database date
	today = date_cls.today()
	# Use timezone-aware local date for submission-day counts to match how we record stats
	from django.utils import timezone as dj_tz
	bookings_created_today = Booking.objects.filter(created_at__date=dj_tz.localdate()).count()
	bookings_scheduled_today = Booking.objects.filter(date=today).count()
	# Ensure DailyBookingStat for today matches live bookings (keeps per-day stat accurate)
	try:
		from .models import DailyBookingStat
		# Use bookings_created_today so the dashboard shows bookings submitted on each day
		# Persist the stat keyed by the local submission date
		DailyBookingStat.objects.update_or_create(date=dj_tz.localdate(), defaults={'total_bookings': bookings_created_today})
	except Exception:
		pass
	# Unseen pending bookings (for notification badge/popup)
	unseen_count = Booking.objects.filter(status='Pending', notification_seen=False).count()
	# Always sum revenue for this month based on Completed bookings
	year = today.year
	month = today.month
	# Always recalculate to ensure it only counts Completed bookings
	revenue_agg = Booking.objects.filter(date__year=year, date__month=month, status='Completed').aggregate(total=Sum('price'))
	revenue_this_month = revenue_agg.get('total') or 0
	
	# Update the cached MonthlyRevenue record to match
	try:
		MonthlyRevenue.objects.update_or_create(
			year=year, 
			month=month, 
			defaults={'total_revenue': revenue_this_month}
		)
	except Exception:
		pass
	
	# Show only the latest unseen booking in the notification popup
	latest_booking = bookings.filter(status='Pending', notification_seen=False).order_by('-created_at').first()
	print('Services sent to dashboard:')
	for s in services:
		print(f"id={s.id}, name={s.name}, price={s.price}, duration={s.duration}")
	# Monthly revenue for last 12 months
	from django.db.models.functions import TruncMonth
	from django.db import models
	monthly_revenue_qs = Booking.objects.values('date').annotate(month=TruncMonth('date')).values('month').annotate(total=models.Sum('price')).order_by('month')
	monthly_revenue_data = []
	for entry in monthly_revenue_qs:
		if entry['month']:
			monthly_revenue_data.append({
				'month': entry['month'].strftime('%b %Y'),
				'total': float(entry['total']) if entry['total'] else 0
			})

	# Top services by volume (count)
	service_volume_qs = Booking.objects.values('service').annotate(count=models.Count('service')).order_by('-count')
	service_volume_data = []
	for entry in service_volume_qs:
		service_volume_data.append({
			'service': entry['service'],
			'count': entry['count']
		})

	# For the dashboard we want a single concise stat: bookings submitted (created) today.
	new_booking_count = bookings_created_today
	return render(request, 'admin-dashboard.html', {
		'bookings': bookings,
		'completed_bookings': completed_bookings,
		'services': services,
		'employees': employees,
		'active_therapists': active_therapists,
		'new_booking_count': new_booking_count,
		'unseen_count': unseen_count,
		'latest_booking': latest_booking,
		'revenue_this_month': revenue_this_month,
		'monthly_revenue_data': monthly_revenue_data,
		'service_volume_data': service_volume_data,
	})
from django.shortcuts import render


def index(request):
	"""Render the project index template."""
	return render(request, 'index.html')


def services(request):
	from .models import Service
	services = Service.objects.all().order_by('name')
	return render(request, 'services.html', {'services': services})


def about(request):
	"""Render the about page."""
	from .models import Employee
	employees = Employee.objects.all().order_by('name')
	return render(request, 'about.html', {'employees': employees})

def contact(request):
	"""Render the contact page."""
	return render(request, 'contact.html')

def booknow(request):
	from .models import Service, Employee, Booking
	services = Service.objects.all().order_by('name')
	employees = Employee.objects.all().order_by('name')
	selected_service = None
	service_id = request.GET.get('service')
	if service_id:
		try:
			selected_service = Service.objects.filter(id=service_id).first()
		except Exception:
			selected_service = None

	if request.method == 'POST':
		print('Booking form POST data:', dict(request.POST))
		therapist_name = request.POST.get('therapistPref')
		therapist_code = None
		# Support therapist dropdown values with titles (e.g., 'Melson Morta — Junior Therapist')
		if therapist_name:
			therapist_name_clean = therapist_name.split('—')[0].strip().lower()
			for code, label in Booking.THERAPIST_CHOICES:
				if label.lower().startswith(therapist_name_clean):
					therapist_code = code
					break
		date = request.POST.get('dateSelection')
		time = request.POST.get('timeSelection')
		# Normalize/parse incoming date and time strings into proper date/time objects
		from datetime import datetime, date as date_cls, time as time_cls
		parsed_date = None
		parsed_time = None
		date_raw = date
		if date_raw:
			# Try common formats
			for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y'):
				try:
					parsed_date = datetime.strptime(date_raw, fmt).date()
					break
				except Exception:
					pass
			# If parsing failed but value looks like an ISO date, let Django handle it later
			if not parsed_date:
				try:
					# last-resort: if it's already a date-like object string, try ISO parse
					parsed_date = datetime.fromisoformat(date_raw).date()
				except Exception:
					parsed_date = None
		# parse time
		time_raw = time
		if time_raw:
			for tfmt in ('%H:%M', '%I:%M %p', '%I:%M%p'):
				try:
					parsed_time = datetime.strptime(time_raw, tfmt).time()
					break
				except Exception:
					pass
		# Use parsed values if available; otherwise keep original strings (Django will try to coerce)
		if parsed_date:
			date = parsed_date
		if parsed_time:
			time = parsed_time

		customer_name = request.POST.get('customerName')
		customer_phone = request.POST.get('customerPhone')
		customer_email = request.POST.get('customerEmail')
		customer_address = request.POST.get('customerAddress')
		service_id = request.POST.get('serviceSelection')
		service_obj = None
		service_code = ''
		if service_id:
			service_obj = Service.objects.filter(id=service_id).first()
			# service is stored as a ForeignKey to Service; we don't need the
			# old Booking.SERVICE_CHOICES mapping here. Keep service_code empty
			# for backward compatibility (unused in current model).
			service_code = ''
		price = service_obj.price if service_obj else 0
		duration = service_obj.duration if service_obj else ''
		is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
		try:
			# If we couldn't map a therapist code, store the provided therapist name (or blank for 'none')
			therapist_value = ''
			if therapist_code:
				therapist_value = therapist_code
			else:
				# therapistPref may be 'none' or an employee name; prefer empty string for 'none'
				if therapist_name and str(therapist_name).strip().lower() != 'none':
					therapist_value = therapist_name
				else:
					therapist_value = ''
			# Ensure notification flag is explicitly unset on creation
			booking = Booking.objects.create(
				customer_name=customer_name,
				customer_phone=customer_phone,
				customer_email=customer_email,
				customer_address=customer_address,
				therapist=therapist_value,
				service=service_obj,
				date=date,
				time=time,
				price=price,
				status='Pending',
				notification_seen=False
			)
			print('Booking created:', booking)
			# Notify admin pages that a booking was created
			try:
				_bump_booking_version()
			except Exception:
				pass
			# Ensure booking notification flag is unset (so admin sees it as unseen)
			try:
				if hasattr(booking, 'notification_seen'):
					booking.notification_seen = False
					booking.save(update_fields=['notification_seen'])
			except Exception:
				pass
			# Send an email notification to site admins so they are alerted of the new booking
			try:
				admin_emails = []
				# settings.ADMINS is a list of (name, email) tuples
				if getattr(settings, 'ADMINS', None):
					admin_emails = [e[1] for e in settings.ADMINS if len(e) > 1 and e[1]]
				# Fallback to DEFAULT_FROM_EMAIL if no ADMINS configured
				if not admin_emails:
					fallback = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
					if fallback:
						admin_emails = [fallback]
				if admin_emails:
					subject = f"New booking: {booking.customer_name} — {booking.service}"
					message = (
						f"New booking submitted:\n\n"
						f"Customer: {booking.customer_name}\n"
						f"Email: {booking.customer_email}\n"
						f"Phone: {booking.customer_phone}\n"
						f"Service: {booking.service}\n"
						f"Date: {booking.date}\n"
						f"Time: {booking.time}\n"
						f"Status: {booking.status}\n"
					)
					from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@yourspa.com')
					try:
						send_mail(subject, message, from_email, admin_emails, fail_silently=False)
						print('Admin notified of new booking via email:', admin_emails)
					except Exception as e:
						print('Admin email notification failed:', e)
			except Exception:
				# non-fatal
				pass
			# Update daily booking stat so the Admin "New Bookings Today" is tracked server-side
			# Track stats by booking submission date (created_at) instead of appointment date.
			try:
				from .models import DailyBookingStat
				from django.db.models import F
				from django.utils import timezone as dj_tz
				# Determine the booking's submission day in local date
				try:
					created_day = dj_tz.localtime(booking.created_at).date()
				except Exception:
					# fallback to naive date if timezone conversion fails
					created_day = getattr(booking, 'created_at', None).date() if getattr(booking, 'created_at', None) else dj_tz.localdate()
				print(f"Updating DailyBookingStat for booking id={booking.id} created_day={created_day}")
				stat, created = DailyBookingStat.objects.get_or_create(date=created_day, defaults={'total_bookings': 0})
				DailyBookingStat.objects.filter(pk=stat.pk).update(total_bookings=F('total_bookings') + 1)
				stat.refresh_from_db()
				print(f"DailyBookingStat updated: date={stat.date} total_bookings={stat.total_bookings}")
				try:
					_bump_booking_version()
				except Exception:
					pass
			except Exception as ex:
				# don't block booking creation on stat bookkeeping
				print('Warning: could not update DailyBookingStat', ex)
			if is_ajax:
				return JsonResponse({'success': True})
			else:
				# Redirect to booking page with success flag
				return redirect('/book-now/?success=1')
		except Exception as e:
			print('Booking creation error:', e)
			if is_ajax:
				return JsonResponse({'success': False, 'error': str(e)}, status=400)
			else:
				return render(request, 'booknow.html', {
					'services': services,
					'employees': employees,
					'selected_service': selected_service,
					'error': 'Could not submit booking — please try again.'
				})

	# Show success message only if ?success=1 in URL
	success_msg = None
	if request.GET.get('success') == '1':
		success_msg = 'Booking submitted successfully!'
	return render(request, 'booknow.html', {
		'services': services,
		'employees': employees,
		'selected_service': selected_service,
		'success': success_msg
	})
# Delete Booking
from .models import Booking

def delete_booking(request, booking_id):
	from django.http import HttpResponse
	booking = get_object_or_404(Booking, id=booking_id)
	if request.method == 'POST':
		# Capture booking creation date so we can decrement the per-day stat after deletion
		from django.utils import timezone as dj_tz
		try:
			booking_date = dj_tz.localtime(booking.created_at).date()
		except Exception:
			booking_date = getattr(booking, 'created_at', None).date() if getattr(booking, 'created_at', None) else booking.date
		booking.delete()
		print(f"Booking {booking_id} deleted permanently.")  # Debug log
		# Notify admin pages that a booking was removed
		try:
			_bump_booking_version()
		except Exception:
			pass
		# Try to decrement DailyBookingStat for that date (clamp at zero)
		try:
			from .models import DailyBookingStat
			from django.db.models import F, Case, When, Value
			stat, created = DailyBookingStat.objects.get_or_create(date=booking_date, defaults={'total_bookings': 0})
			DailyBookingStat.objects.filter(pk=stat.pk).update(
				total_bookings=Case(
					When(total_bookings__gt=0, then=F('total_bookings') - 1),
					default=Value(0)
				)
			)
		except Exception:
			# non-fatal: do not block deletion on stat update errors
			pass
		is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
		if is_ajax:
			return JsonResponse({'success': True})
		return redirect('/admin-dashboard/#bookings')
	return render(request, 'delete-booking.html', {'booking': booking})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Employee

@csrf_exempt
def add_employee(request):
	if request.method == 'POST':
		name = request.POST.get('name')
		title = request.POST.get('title')
		bio = request.POST.get('bio', '')
		status = request.POST.get('status', 'Active')
		if status not in ['Active', 'On Leave']:
			status = 'Active'
		emp = Employee.objects.create(name=name, title=title, bio=bio, status=status)
		return JsonResponse({'success': True, 'id': emp.id, 'name': emp.name, 'title': emp.title, 'bio': emp.bio})
	return JsonResponse({'success': False, 'error': 'POST required'}, status=400)

@csrf_exempt
def edit_employee(request, emp_id):
	emp = Employee.objects.filter(id=emp_id).first()
	if not emp:
		return JsonResponse({'success': False, 'error': 'Employee not found'}, status=404)
	if request.method == 'POST':
		emp.name = request.POST.get('name', emp.name)
		emp.title = request.POST.get('title', emp.title)
		emp.bio = request.POST.get('bio', emp.bio)
		status = request.POST.get('status')
		if status in ['Active', 'On Leave']:
			emp.status = status
		emp.save()
		return JsonResponse({'success': True, 'id': emp.id, 'name': emp.name, 'title': emp.title, 'bio': emp.bio, 'status': emp.status})
	return JsonResponse({'success': False, 'error': 'POST required'}, status=400)

@csrf_exempt
def delete_employee(request, emp_id):
	emp = Employee.objects.filter(id=emp_id).first()
	if not emp:
		return JsonResponse({'success': False, 'error': 'Employee not found'}, status=404)
	if request.method == 'POST':
		try:
			# Debug logging to help trace browser requests
			try:
				print('delete_employee: headers=', dict(request.headers))
				print('delete_employee: POST=', dict(request.POST))
			except Exception:
				pass
			emp.delete()
			print(f"Employee {emp_id} deleted via admin-dashboard request.")
			is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
			if is_ajax:
				return JsonResponse({'success': True})
			# Non-AJAX fallback: redirect back to admin dashboard so hidden-form submission works
			return redirect('massage_app:admin-dashboard')
		except Exception as e:
			print('delete_employee error:', e)
			return JsonResponse({'success': False, 'error': str(e)}, status=500)
	# For non-POST requests, redirect to admin dashboard
	return redirect('massage_app:admin-dashboard')

