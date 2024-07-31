from django.contrib import admin
from .models import User, Profile, FuelingStation, Dashboard

class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active']
    list_editable = ['is_active']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user_full_name', 'premium', 'user_bio', 'profile_image']
    list_editable = ['premium']

    def user_full_name(self, obj):
        return obj.get_user_full_name()
    user_full_name.short_description = 'Full Name'

class FuelingStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'address', 'cooking_gas_price_per_kg', 'diesel_price_per_litre', 'petrol_price_per_litre', 'sell_cooking_gas', 'sell_diesel', 'sell_petrol', 'last_updated')
    search_fields = ('name', 'location')
    list_filter = ('sell_cooking_gas', 'sell_diesel', 'sell_petrol', 'last_updated')

class DashboardAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'get_station_name', 
        'get_location', 
        'get_address', 
        'get_cooking_gas_price', 
        'get_diesel_price', 
        'get_petrol_price', 
        'status'
    )
    search_fields = ('user__email', 'station__name')
    list_filter = ('status', 'station__name')

    def get_station_name(self, obj):
        return obj.station.name
    get_station_name.short_description = 'Station Name'

    def get_location(self, obj):
        return obj.station.location
    get_location.short_description = 'Location'

    def get_address(self, obj):
        return obj.station.address
    get_address.short_description = 'Address'

    def get_cooking_gas_price(self, obj):
        return obj.station.cooking_gas_price_per_kg
    get_cooking_gas_price.short_description = 'Cooking Gas Price'

    def get_diesel_price(self, obj):
        return obj.station.diesel_price_per_litre
    get_diesel_price.short_description = 'Diesel Price'

    def get_petrol_price(self, obj):
        return obj.station.petrol_price_per_litre
    get_petrol_price.short_description = 'Petrol Price'

admin.site.register(FuelingStation, FuelingStationAdmin)
admin.site.register(Dashboard, DashboardAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)