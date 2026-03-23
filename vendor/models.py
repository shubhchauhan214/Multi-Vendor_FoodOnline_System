from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification
from datetime import time, date, datetime


class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=100)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    def is_open(self):
        # Check current day's opening hours
        today_date_weekday = date.today().isoweekday()
        current_opening_hours = OpeningHour.objects.filter(vendor=self, day=today_date_weekday)
        present_time = datetime.now().strftime('%H:%M:%S')

        is_open = None
        for i in current_opening_hours:
            if not i.is_closed:
                start_time = str(datetime.strptime(i.from_hour, '%I:%M %p').time())
                end_time = str(datetime.strptime(i.to_hour, '%I:%M %p').time())

                if start_time < present_time < end_time:
                    is_open = True
                else:
                    is_open = False

        return is_open

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # means it is updated for this vendor
            # at the time of creation, self.pk will be None.

            # get the current i.e. original details of the vendor here using the pk
            orig = Vendor.objects.get(pk=self.pk)

            # if there is difference in the is_approved status of vendor in the original and
            # updated version
            if orig.is_approved != self.is_approved:

                mail_template = 'accounts/email/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                    'to_email': self.user.email,
                }

                if self.is_approved:
                    # send notification mail
                    mail_subject = 'Congratulation! Your restaurant has been approved.'
                    send_notification(mail_subject, mail_template, context)
                else:
                    # send rejection mail
                    mail_subject = 'We are sorry! You are not eligible for publishing your food menu ' \
                                   'on our marketplace.'
                    send_notification(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args, **kwargs)


DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday"))
]

HOUR_OF_DAY_24 = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0, 24) for m in (0, 30)]


class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()