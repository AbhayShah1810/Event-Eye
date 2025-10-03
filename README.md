# EventEye Certificates

## Quickstart

1. Python 3.10+:

```bash
pip install -r requirements.txt
```

2. Configure email provider (Gmail SMTP (App Password)):
- Copy `.env.example` to `.env` and fill app password.

3. Prepare assets:
- Put your certificate image at `assets/base_certificate.png` (replace placeholder).

4. Run the app:

```bash
streamlit run app.py
```

5. Upload CSV with `name,email`. Example provided: `participants.sample.csv`.

## Notes
- Certificates saved to `certs/`.
- Name verification is a basic length/digit check.
- Adjust positions and font in `certificate_generator.py`.

Environment:
- SENDER_EMAIL (your Gmail)
- SENDER_NAME
- GMAIL_APP_PASSWORD (16-char app password)

Generate an App Password: Google Account → Security → 2-Step Verification → App Passwords.
# Event-Eye
