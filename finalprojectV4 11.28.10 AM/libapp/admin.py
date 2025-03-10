from django.contrib import admin
from .models import Book, User
from django.utils.translation import gettext_lazy as _  # For translations

# Custom action to set all selected books as borrowed
def mark_all_books_as_borrowed(modeladmin, request, queryset):
    updated_count = queryset.update(status='borrowed')
    modeladmin.message_user(request, f'{updated_count} books have been set to borrowed.')

mark_all_books_as_borrowed.short_description = _("Mark all selected books as borrowed")

# Custom action to set all selected books as available
def mark_all_books_as_available(modeladmin, request, queryset):
    updated_count = queryset.update(status='available')
    modeladmin.message_user(request, f'{updated_count} books have been set to available.')

mark_all_books_as_available.short_description = _("Mark all selected books as available")

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'status')  # Display book details
    actions = [mark_all_books_as_borrowed, mark_all_books_as_available]  # Add both actions

# Register the Book model with the custom admin class
admin.site.register(Book, BookAdmin)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id_number', 'name', 'user_type')  # Customize what fields to display in the list
    search_fields = ('id_number', 'name')  # Add search functionality
    list_filter = ('user_type',)  # Add filter functionality for user type
