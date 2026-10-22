# Ziyokoruz

Update the exam app based on these exact rules:

1. AUTH & ADMIN:

- Remove public Sign-Up completely.

- Admin enters Student Full Name -> system auto-generates unique Login & Password.

- Students log in ONLY using Admin-provided credentials.

2. SELECTIVE DATA DELETION (SETTINGS):

- In the Admin Settings panel, add a "Clear Data" option, BUT ensure it EXCLUDES and KEEPS all student login/password credentials safe. It should only clear test results or history, leaving student accounts intact so they can always log in.

3. RESILIENT MOCK EXAM SYSTEM:

- Real-time Auto-Save: Selected answers are instantly saved to the database.

- Logout/Refresh Resilience: If a student accidentally exits or logs out, re-logging in restores their saved answers immediately.

- Unstoppable Timer: Exam timer runs based on server timestamps, so time does not stop or reset even if the student logs out and logs back in.

4. PDF EXPORT & UI:

- Admin can export the results table as a formatted PDF.

- Match clean, distraction-free mock exam styling.    va shu shablonga oxshab chiqishi kerak natijalarni tekshirib bolgandan keyin va keyin dizayni ziyokor logosiga oxhsatib rang qilib chiqroyli dizayn qil va keyin natijalardagi grafikni togirlab ber aniq ishlasin bolla koproq qaysi savolarda xato qilyapti shuni xam taxlil qilsin va yubor kod ni iltimos zip dagi dasturni shularni qoshsang boladi qolgan narsalariga tegma va yana iltimos tokenni tejab ishlat

This project was built with [Lovable](https://lovable.dev).

**Live app**: https://ziyokoruz.lovable.app

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/9ffc226a-f09d-4838-9531-1da603605751).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
