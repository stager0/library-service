from celery import shared_task
from celery.utils.time import timezone
from django.contrib.auth import get_user_model

from borrowings.models import Borrowing
from telegram_bot.models import UserProfile
from telegram_bot.views import send_message


@shared_task
def every_day_notification():
    user_profiles = UserProfile.objects.all()
    borrowings = Borrowing.objects.filter(actual_return_date__isnull=True).filter(expected_return_date__lte=timezone.now())

    users_list = []
    for borrowing in borrowings:
        user_profile = user_profiles.get(email=borrowing.user.email)
        book = borrowing.book
        data = \
            "You had to return book: \n " \
            f"Title: {book.title} \n" \
            f"Author: {book.author} \n" \
            f"To: {borrowing.expected_return_date}\n" \
            "Please, return the book as soon as possible!\n"
        users_list.append(int(borrowing.user.id))

        send_message(user_profile.telegram_chat_id, text=data)

    users_without_borrowings = get_user_model().objects.filter(id__in=users_list)
    for user in users_without_borrowings:
        if user.id not in users_list:
            user_profile = user_profiles.get(email=user.email)
            send_message(
                chat_id=user_profile.telegram_chat_id,
                text="No borrowings overdue today!"
            )
