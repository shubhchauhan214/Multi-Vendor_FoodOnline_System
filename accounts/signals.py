from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from accounts.models import UserProfile, User


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            UserProfile.objects.create(user=instance)

# Here the sender is the User class, where we are creating the user
# receiver is the post_save function that will get triggered after the run of sender
# There are two ways to connect sender to the receiver
# 1st way is using the post_save.connect method as shown below
# post_save.connect(receiver=post_save_create_profile_receiver, sender=User)
# second is to use decorator to connect sender to receiver


# example of pre_save()
@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    # this will be triggered just before the user is created. that's why it does not take
    # created parameter as post_save
    print(instance.username, "this user is being saved.")
