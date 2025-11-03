from django.shortcuts import render


def index(request):
	"""Render the project index template."""
	return render(request, 'index.html')


def services(request):
	"""Render the services page."""
	return render(request, 'services.html')


def about(request):
	"""Render the about page."""
	return render(request, 'about.html')


def contact(request):
	"""Render the contact page."""
	return render(request, 'contact.html')


def booknow(request):
	"""Render the booking page."""
	return render(request, 'booknow.html')


def login_view(request):
	"""Render the login page."""
	return render(request, 'login.html')

