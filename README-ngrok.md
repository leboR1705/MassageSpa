# Quick ngrok + Django helper

This project includes `start-ngrok.ps1` which launches Django and ngrok in separate PowerShell windows, waits for ngrok's API, copies the public URL to the clipboard, and performs quick test requests (including the `ngrok-skip-browser-warning` header).

How to use

1. Open PowerShell in the project root (where `manage.py` is).
2. Activate the venv (if not already):

```powershell
& .\.venv\Scripts\Activate.ps1
```

3. Run the helper:

```powershell
.\start-ngrok.ps1
```

What the script does

- Stops any existing `ngrok` process.
- Starts Django dev server in a new window (`127.0.0.1:8000`).
- Starts ngrok in a new window (prefers `./tools/ngrok.exe`, then `OneDrive/Desktop/ngrok.exe`, then `Downloads/ngrok.exe`, then system `ngrok`).
- Waits for the ngrok web API and prints the public URL(s).
- Copies the first public URL to your clipboard.
- Runs two test requests for each public URL:
  - A browser-like request (User-Agent: `Mozilla/5.0`).
  - A request with header `ngrok-skip-browser-warning: 1` to bypass the ngrok interstitial.

Testing webhooks / APIs

- If you need remote systems (webhooks) to reach your local app, provide them the public HTTPS URL printed by the script.
- If the ngrok interstitial appears for automated requests, instruct the provider to include the header `ngrok-skip-browser-warning: 1` or a browser-like `User-Agent`.

Troubleshooting

- If the script cannot find your `ngrok.exe`, copy it into `./tools/ngrok.exe` or add its folder to your PATH.
- If the ngrok public URL still shows a warning page in a browser, clicking "Visit Site" once will allow browser visitors to proceed. Programmatic clients should use the skip header.

Security

- The public URL is publicly accessible while ngrok runs. Use with caution and do not expose production secrets.

If you want, I can also modify the script to automatically open the public URL in your browser after launching (note: that will show the interstitial for the first visit unless the skip header is used).