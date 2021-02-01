from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Block

from blocks.management.commands.runapscheduler import sync_blocks


def index(request):
    """Displays blocks from blockchain with pagination."""
    sync_blocks()
    blocks = Block.objects.all()
    paginator = Paginator(blocks, 50)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'index.html', {'page_obj': page_obj})


def block(request, block_height):
    """Displays information about some block."""
    current_block = get_object_or_404(Block, height=block_height)

    return render(request, 'block.html', {'current_block': current_block})
