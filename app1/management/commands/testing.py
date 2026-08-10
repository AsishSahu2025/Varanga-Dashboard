# from django.core.management.base import BaseCommand
# from time import sleep
# from app1.views import remote_sensing_data  # Adjust the import according to your app structure
# from django.core.mail import send_mail
# from ...models import Pond
# from django.conf import settings

# class Command(BaseCommand):
#     help = 'Run remote sensing data processing every 5 days'

#     def handle(self, *args, **options):
#         while True:
#             try:
#                 ponds = Pond.objects.all()
#                 for pond in ponds:
#                     user_email = pond.user.Email
#                     email_subject = 'Remote Sensing Data Processing Started'
#                     email_message = f"""
#                     Dear User,
#                         The remote sensing data processing for pond '{pond.latlong}' has started. We will notify you once it is complete.

#                         Regards,
#                         Bariflolabs
#                     """
#                     send_mail(
#                         email_subject,
#                         email_message,
#                         settings.EMAIL_HOST_USER, 
#                         [user_email], 
#                         fail_silently=False,
#                     )
#                     print("Email sent to", user_email)

#                 remote_sensing_data()
#                 self.stdout.write(self.style.SUCCESS("Remote sensing data processed."))

#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
            
#             sleep(5 * 24 * 60 * 60)  # Wait 5 days before next run
#             # sleep(60)  # Use this for testing instead


from django.core.management.base import BaseCommand
from time import sleep
from app1.views import remote_sensing_data
from django.core.mail import send_mail
from ...models import Pond
from django.conf import settings
import traceback

class Command(BaseCommand):
    help = 'Run remote sensing data processing every 5 days'

    def handle(self, *args, **options):
        while True:
            try:
                # ponds = Pond.objects.all()
                # for pond in ponds:
                #     user_email = pond.user.Email
                #     try:
                #         send_mail(
                #             'Remote Sensing Data Processing Started',
                #             f"Dear User,\n\nThe remote sensing data processing for pond '{pond.latlong}' has started.\n\nRegards,\nBariflolabs",
                #             settings.EMAIL_HOST_USER, 
                #             [user_email], 
                #             fail_silently=False,
                #         )
                #         print("Email sent to", user_email)
                #     except Exception as email_err:
                #         print(f"Email failed to {user_email}: {email_err}")

                remote_sensing_data()
                self.stdout.write(self.style.SUCCESS("Remote sensing data processed."))

            except Exception as e:
                traceback.print_exc()
                self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))

            # sleep(60)  # 1 minute for testing
            # sleep(5 * 24 * 60 * 60)  # 5 days in production
            sleep(24*60*60)