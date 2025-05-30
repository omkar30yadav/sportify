from django.shortcuts import render, get_object_or_404
from .models import Event, Registration
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth import logout  # Add this line
from django.contrib.auth.forms import AuthenticationForm  # Add this line
from django.contrib.auth import authenticate
from .models import SportsVenue, Coaching, Event, Society
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import Event, Registration, Payment
from .forms import RegistrationForm
import razorpay  # Add this import
from .models import Society
from .forms import ContactForm
from django.core.mail import send_mail 
from django.contrib import messages
from .models import Contact  # Import the Contact model
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)


# View for displaying all events
def event_list(request):
    events = Event.objects.all()
    return render(request, 'registration/event_list.html', {'events': events})

@login_required
# def register_event(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#     Registration.objects.create(user=request.user, event=event, payment_status='Pending')
#     return HttpResponseRedirect(reverse('event_list'))
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == "POST":
        # Redirect to the payment page when the button is clicked
        return HttpResponseRedirect(reverse('process_payment', args=[event_id]))
    
    return render(request, 'registration/register_event.html', {'event': event})

def home(request):
    # Fetch upcoming events to show in the carousel
    events = Event.objects.all()  # Fetch all events
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile')
        message = request.POST.get('message')

        # Save the contact details to the database
        contact = Contact(
            name=name,
            email=email,
            mobile_number=mobile_number,
            message=message
        )
        contact.save()

        messages.success(request, "Your message has been sent successfully.")
        return redirect('home')

    return render(request, 'registration/home.html', {'events': events})


# View for displaying all sports venues
def sports_venues(request):
    venues = SportsVenue.objects.all()  # Fetch all venues
    return render(request, 'registration/sports_venues.html', {'venues': venues})

# View for displaying all coaching sessions
def coaching(request):
    coachings = Coaching.objects.all()
    return render(request, 'registration/coaching.html', {'coachings': coachings})

# Register View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('home')  # Redirect to home after registration
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")

                # Check if the user is an admin
                if user.is_staff or user.is_superuser:
                    return redirect('/admin/')  # Redirect to admin page if user is staff or superuser
                else:
                    return redirect('home')  # Redirect normal users to the home page
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

# View to display all societies and their available coaches and sports
def society_list(request):
    societies = Society.objects.all()
    return render(request, 'registration/society_list.html', {'societies': societies})

# Razorpay client setup
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def process_payment(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        amount = int(event.registration_fee * 100)  # Convert registration fee to paise
        
        # Create Razorpay order
        order_data = {
            'amount': amount,  # Amount in paise
            'currency': 'INR',
            'payment_capture': '1',  # Automatically capture payment
        }
        order = razorpay_client.order.create(data=order_data)
        
        # Create Registration entry with payment status as 'Pending'
        registration = Registration.objects.create(
            user=request.user,
            event=event,
            payment_status='Pending'
        )

        # Save payment record
        payment = Payment.objects.create(
            order_id=order['id'],
            amount=amount / 100,  # Convert paise to rupees
            status='Pending',
            event=event,
            user=request.user
        )
        
        return render(request, 'registration/payment.html', {
            'order_id': order['id'],
            'event': event,
            'amount': amount,
            'razorpay_key': settings.RAZORPAY_KEY_ID
        })
    
    return HttpResponse("Invalid request method.", status=405)




@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        # Assuming you're posting payment details from Razorpay
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Verify payment and update payment status
        try:
            # Get the payment object first
            payment = Payment.objects.get(order_id=razorpay_order_id)
            
            # Filter for the corresponding registration
            registrations = Registration.objects.filter(event=payment.event, user=payment.user)

            # If multiple registrations found, take appropriate action
            if registrations.exists():
                # Option 1: If you expect only one valid registration, pick the first one
                registration = registrations.first()

                # Option 2: Or, if you want to handle multiple registrations differently, loop through them
                # for registration in registrations:
                #     # Do something for each registration
                
                # Mark the payment as completed
                payment.status = 'Completed'
                payment.save()

                # Update registration payment status
                registration.payment_status = 'Completed'
                registration.save()

                return render(request, 'registration/payment_success.html')
            else:
                return HttpResponse("No matching registration found.", status=404)

        except Payment.DoesNotExist:
            return HttpResponse("Payment record not found.", status=404)

    return HttpResponse("Invalid request method.", status=405)






def about(request):
    company_info = {
        'name': 'Sportify',
        'description': """
            Sportify is a dynamic platform designed to bring sports enthusiasts together. We specialize in organizing
            sports events, providing coaching sessions, and offering top-tier sports venues for both casual players and
            professionals. Whether you're looking to participate in an upcoming tournament, find a venue for a friendly 
            match, or enroll in a coaching session to hone your skills, Sportify has got you covered.
        """,
        'mission': 'Our mission is to promote active and healthy lifestyles through sports and community engagement.',
        'vision': 'To become the world’s leading sports platform where athletes, coaches, and venues are seamlessly connected.',
        'team': [
            {'name': 'Omkar', 'position': 'CEO', 'bio': 'Omkar is passionate about sports and has over 10 years of experience in sports event management.'},
            {'name': 'Atul', 'position': 'Head Coach', 'bio': 'Atul is a former professional athlete and now leads our coaching division.'},
            {'name': 'Sameer', 'position': 'Operations Manager', 'bio': 'Sameer ensures everything runs smoothly, from venue management to event organization.'}
        ]
    }
    return render(request, 'registration/about.html', {'company_info': company_info})

def contact(request):
    company_info = {
        'name': 'Sportify',
        'email': 'omkary357@gmail.com',
        'phone': '+91 7715078272',
        'address': 'MIDC, Andheri East, Mumbai, Maharashtra 400093, India',
        'website': 'www.sportify.com'
    }
    return render(request, 'registration/contact.html', {'company_info': company_info})