from django.contrib import admin

from .models import Block


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('height', 'hash', 'timestamp' ,'miner', 'transaction_count')
    search_fields = ('height', 'hash')
    list_filter = ('miner', 'transaction_count')

