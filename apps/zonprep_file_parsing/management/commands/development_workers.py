import subprocess
import threading

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '''Sets up all of the workers for local development.'''
    commands = [
        'celery -A zon_prep_ocr_project beat -l INFO',  # Replace with long-running commands
        'celery -A zon_prep_ocr_project worker --loglevel=INFO --concurrency=1 -Q email_queue -P gevent',
        'celery -A zon_prep_ocr_project worker --loglevel=INFO --concurrency=1 -Q parsing_queue -P gevent'
    ]

    # Define arguments here
    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument(
            '--status',
            action='store_true',
            help='Get the status of the workers',
            default=False
        )
        parser.add_argument(
            '--start',
            action='store_true',
            help='start all of the workers',
            default=False
        )

    def handle(self, *args, **kwargs):

        status = kwargs.get("status", False)
        start_workers = kwargs.get("start", False)
        # Create a thread for each command
        threads = []

        if status:
            self.stdout.write("Getting status of all celery workers...")

            command = "celery -A zon_prep_ocr_project inspect active_queues"
            self.stdout.write("-----------------------------------")
            self.stdout.write(F"Running: {command}")
            self.stdout.write("-----------------------------------")
            thread = threading.Thread(target=run_command, args=(command,))
            threads.append(thread)
            thread.start()
            return

        if start_workers:
            self.stdout.write("Starting all celery workers...")
            for command in self.commands:
                self.stdout.write("-----------------------------------")

                self.stdout.write(F"Running: {command}")

                self.stdout.write("-----------------------------------")

                thread = threading.Thread(target=run_command, args=(command,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            self.stdout.write("All commands completed.")

            self.stdout.write("Complete!")

def run_command( command):
    """Run a single command in a subprocess."""
    process = subprocess.Popen(command, shell=True)
    process.wait()
