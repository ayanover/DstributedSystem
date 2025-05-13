from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from ...models import Device


class Command(BaseCommand):
    help = 'Mark inactive devices that have not sent a heartbeat recently'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Timeout in seconds before marking a device as inactive (default: 60)'
        )

    def handle(self, *args, **options):
        timeout_seconds = options['timeout']
        timeout_threshold = timezone.now() - timedelta(seconds=timeout_seconds)

        # Find devices that haven't sent a heartbeat
        inactive_devices = Device.objects.filter(
            is_active=True,
            last_seen__lt=timeout_threshold
        )

        # Mark them as inactive
        count = inactive_devices.count()
        inactive_devices.update(is_active=False)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully marked {count} devices as inactive')
        )