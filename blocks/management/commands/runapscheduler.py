"""
Job scheduling for django-apscheduler
"""
import logging
from typing import Optional

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from blocks.models import Block

BCS_INFO_URL = 'https://dabidabida.bcschain.info/api/info'
BCS_BLOCKS_URL = 'https://dabidabida.bcschain.info/api/recent-blocks?count='

logger = logging.getLogger(__name__)


def get_blockchain_height() -> Optional[int]:
    try:
        response = requests.get(BCS_INFO_URL)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_error:
        logger.error(f'HTTP Error: {http_error}')
        return None

    height = response.json().get('height')

    return height


def get_blocks(height: int) -> Optional[dict]:

    try:
        response = requests.get(BCS_BLOCKS_URL + str(height))
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_error:
        logger.error(f'HTTP Error: {http_error}')
        return None

    return response.json()


def sync_blocks():
    """This job synchronize local database with external API (bcschain)"""
    height = get_blockchain_height()

    try:
        db_blockchain_height = Block.objects.latest('height').height

        if height == db_blockchain_height:
            return None
        else:
            height -= db_blockchain_height
    except ObjectDoesNotExist:
        logger.info('First synchronization with BCS API. Please wait.')

    new_blocks = get_blocks(height)

    for block in new_blocks:
        Block.objects.create(
            height=block.get('height'),
            hash=block.get('hash'),
            timestamp=block.get('timestamp'),
            miner=block.get('miner'),
            transaction_count=block.get('transactionCount')
        )


def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = 'Runs apscheduler.'

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        scheduler.add_job(
            sync_blocks,
            trigger=CronTrigger(minute="*/3"),
            id='sync_blocks',
            max_instances=1,
            replace_existing=True,
        )
        logger.info('Added job \'sync_blocks\'.')

        try:
            logger.info('Starting scheduler...')
            scheduler.start()
        except KeyboardInterrupt:
            logger.info('Stopping Scheduler...')
            scheduler.shutdown()
            logger.info('Scheduler shut down successfully.')
