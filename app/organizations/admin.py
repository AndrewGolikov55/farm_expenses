from django.contrib import admin
from .models import Organization, Membership, Invitation

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'organization__name')

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('organization', 'email', 'accepted', 'created_at')
    list_filter = ('accepted', 'organization')
    search_fields = ('email', 'organization__name')
