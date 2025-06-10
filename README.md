# Library-service API

**A full-fledged system for a city library**, where users can borrow books online and pay for them. The system integrates with **Stripe API** for payment processing and **Telegram API** for sending notifications to users through a bot.

## Key Features:
1. **JWT Authentication** - Users can log in through the web app and the Telegram bot.
2. **Book Borrowing System** - Users can create book borrowings, pay for them via Stripe, and receive notifications about the borrowing status.
3. **Telegram Bot** - The bot sends notifications to users:
   - About successful payments.
   - About payment cancellations.
   - About new borrowings, including book title, author, return date, etc.
4. **Daily Notifications via Celery and Celery Beat** - Users who are logged into the Telegram bot receive daily updates about their borrowings.
5. **Admin Rights**:
   - Admins can return books and check the status of borrowings, create new books, and manage user transactions.
6. **Automatic Data Fixtures** - The system automatically loads a fixture with sample data, so you can start using the system right away without needing to manually populate the database.

## Technologies:
- **Python**
- **Django**
- **Django REST Framework**
- **Stripe API** for payment processing
- **Telegram API** for the bot
- **JWT Authentication**
- **Celery and Celery Beat** for scheduling tasks
- **Redis** for Celery task queues
- **Docker Compose** for environment isolation and deployment
- **Ngrok** for testing Telegram API locally
- **Django TestCase** for unit testing

## Screenshots:
1. **Book-list** - Example of the available books list output.
![book-list.png](screenshots%20%28README%29/book-list.png)
2. **Borrowing Create** - Example output when creating a borrowing. A payment link is provided immediately upon creation.
![borrowing-create.png](screenshots%20%28README%29/borrowing-create.png)
3. **Borrowing Return** - Admin-only functionality. When returning a book, admins check payment status and generate a payment link through Stripe if necessary.
![borrowing_pk_return-book.png](screenshots%20%28README%29/borrowing_pk_return-book.png)
4. **Payment Cancellation** - If the payment is canceled, the system outputs a cancellation message, sends a Telegram notification, and deletes the borrowing and payment records from the database.
![cancel_pay.png](screenshots%20%28README%29/cancel_pay.png)
5. **Example Telegram message during authorization**.

![telegram_start_and_login.jpg](screenshots%20%28README%29/telegram_start_and_login.jpg)

6. **Example Telegram message when a new borrowing is created**.

![create_new_borrowing_sms.jpg](screenshots%20%28README%29/create_new_borrowing_sms.jpg)

7. **Example Telegram message on payment cancellation**.

![telegram_cancel_payment.jpg](screenshots%20%28README%29/telegram_cancel_payment.jpg)

8. **Example Telegram message for successful payment**.

![telegram_success_payment_sms.jpg](screenshots%20%28README%29/telegram_success_payment_sms.jpg)

9. **Library Service URL Schema** - Visual representation of the API endpoints and routes.
![paths.png](screenshots%20%28README%29/paths.png)
10. **Payment-list** - Example of a list of payments associated with a user. Admins can view all payments.
![payment-list.png](screenshots%20%28README%29/payment-list.png)
11. **Stripe Payment Page** - Example of a Stripe payment page for completing transactions.
![payment_stripe.png](screenshots%20%28README%29/payment_stripe.png)
12. **Success Payment Page** - Example of a successful payment page. After this, the borrowing and fine statuses are updated in the database.
![success_pay.png](screenshots%20%28README%29/success_pay.png)
13. **Swagger** - Example of the Swagger UI for testing the API endpoints.
![swagger1.png](screenshots%20%28README%29/swagger1.png)
![swagger2.png](screenshots%20%28README%29/swagger2.png)

## Installation on Your Machine:

1. Fill in the `.env` file following the example in `.env.sample`.
2. Run the following command to build and start the Docker containers:
   ```bash
   docker-compose up --build
3. Log in using the following credentials:

   Email: `alice_admin@example.com`

   Password: `1qazcde3`

4. Once the system is set up, it will be ready to use. You can create borrowings, make payments, and test the functionality with the Telegram bot.
