# Aji Fashion Marketplace — Python/Flet Coursework Application

## Updated: PC + Phone Browser Access

This project can run in two ways:

1. **Desktop mode:** the Flet application opens as a native desktop application on the PC.
2. **Web/phone mode:** the same Python application runs as a local Flet web server on the PC and can be opened from a phone browser when the phone and PC are on the same Wi-Fi/network.

Flet 0.28.3 is pinned because it is the last 0.x release and the existing application uses the 0.28 API. Flet's documentation confirms that 0.28.3 is the last 0.x release and that the 0.28 `ft.app(target=..., view=ft.AppView.WEB_BROWSER)` style differs from Flet 1.0. citeturn0search0

## Requirements

- Windows 10 or Windows 11, 64-bit
- Python 3.10 or newer
- Internet connection for the first dependency installation
- Chrome/Edge/Firefox for browser mode
- Same Wi-Fi/local network for PC-to-phone testing

Flet currently requires Python 3.10 or later and supports 64-bit Windows 10/11. citeturn1search4

## Easiest way to run on the PC

Double-click:

```text
run_desktop.bat
```

The script creates a local `.venv`, installs the pinned dependencies, and starts `app.py`.

Manual commands are also supported:

```text
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

## Easiest way to access it from a phone

1. Connect the PC and phone to the same Wi-Fi.
2. Double-click `run_phone.bat` on the PC.
3. The script displays the PC's IPv4 addresses.
4. Keep the command window open.
5. On the phone, open Chrome.
6. Enter:

```text
http://YOUR-PC-IP:8550
```

Example:

```text
http://192.168.1.5:8550
```

The phone is only the browser client; the Python/Flet application and SQLite database remain running on the PC.

Flet's CLI supports web mode with `--web`, a fixed port with `--port`, and a host value of `*` to listen on all IP addresses. citeturn1search0turn1search2

## Troubleshooting phone access

### Phone says the page cannot be reached

- Confirm PC and phone are on the same Wi-Fi.
- Use the PC's Wi-Fi adapter IPv4 address, not `127.0.0.1`.
- Keep `run_phone.bat` running.
- Confirm the URL ends with `:8550`.
- Run `check_connection.bat` to list the PC's IPv4 addresses.
- If Windows Firewall asks for permission, allow the Python/Flet process on a trusted **Private** network.
- Some school, office, hotel, and public networks block device-to-device traffic. Try a home Wi-Fi network or a personal hotspot.

## Demo accounts

- Buyer: `buyer@example.com` / `buyer123`
- Seller: `seller@example.com` / `seller123`
- Admin: `admin@example.com` / `admin123`

## Implemented modules

- Authentication
- Buyer marketplace and search
- Shopping cart
- Checkout with stock validation and stock deduction
- Order viewing
- Seller product creation
- Administrator dashboard
- SQLite database

## Important academic-prototype note

This remains an academic prototype. For real deployment, replace the demonstration password hashing with a modern password-hashing scheme, add authorization checks to every protected database operation, implement real payment integration, stronger input validation, logging, backups, HTTPS, and applicable privacy/e-commerce compliance.

Do not expose the local development server directly to the public internet.
