# admin.py
from django.contrib import admin
from .models import Offers
# Определяем действие
def mark_as_not_interesting(modeladmin, request, queryset):
    queryset.update(status='not_interesting')  # Предполагаем, что у вас есть поле status в модели
    modeladmin.message_user(request, "Выбранные элементы отмечены как не интересные.")
mark_as_not_interesting.short_description = "Не интересно"

def mark_as_interesting(modeladmin, request, queryset):
    queryset.update(status='interesting')  # Предполагаем, что у вас есть поле status в модели
    modeladmin.message_user(request, "Выбранные элементы отмечены как не интересные.")
mark_as_interesting.short_description = "Интересно"


class OffersAdmin(admin.ModelAdmin):
    list_display = ('title', 'kwork_id', 'status', 'wanted_cost', 'url', 'created_at')  # Убедитесь, что поле status есть в вашем списке
    actions = [mark_as_not_interesting, mark_as_interesting]
    list_filter = ('status',)  # Фильтр по статусу
    search_fields = ('title', 'description', 'kwork_id')
    sortable_by = ('created_at')
    # Регистрируем действие
admin.site.register(Offers, OffersAdmin)