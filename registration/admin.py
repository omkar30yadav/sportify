from django.contrib import admin
from .models import Event, Registration, Payment, SportsVenue, Coaching, Society, Sport, Contact

class SocietyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name',)
    filter_horizontal = ('coaches',)  # For selecting multiple coaches

class SportsVenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name',)
    filter_horizontal = ('societies',)  # For selecting multiple societies
    
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'mobile_number']
    search_fields = ['name', 'email']


# Register your models here
admin.site.register(Event)
admin.site.register(Registration)
admin.site.register(Payment)
admin.site.register(SportsVenue, SportsVenueAdmin)  # Using the custom admin for SportsVenue
admin.site.register(Coaching)
admin.site.register(Society, SocietyAdmin)  # Using the custom admin for Society
admin.site.register(Sport)
admin.site.register(Contact, ContactAdmin)  # Using the custom admin for Contact
