#!/usr/bin/env python3
"""
Send the same chat message multiple times with a configurable delay.
"""

import argparse
import sys
import time
from playwright.sync_api import sync_playwright

URL = "https://chat-4ff4.onrender.com/chat.html"


def main():
    parser = argparse.ArgumentParser(description="Spam a message via Playwright")

    # 🔹 Single message
    parser.add_argument(
        "--message",
        default="Hello from bot",
        help="Message to send"
    )

    # 🔹 How many times to send it
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of times to send the message"
    )

    # 🔹 Delay between sends
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay between messages (seconds)"
    )

    parser.add_argument("--username", default="gabinator", help="Chat username")
    parser.add_argument("--gate", default="yes", help="Gate value")
    parser.add_argument("--headless", action="store_true", help="Run headless")

    args = parser.parse_args()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=args.headless)
            context = browser.new_context()

            # Inject sessionStorage BEFORE page loads
            context.add_init_script(f"""
                sessionStorage.setItem('gate_passed', '{args.gate}');
                sessionStorage.setItem('chat_username', '{args.username}');
            """)

            page = context.new_page()

            print("Opening page...")
            page.goto(URL, wait_until="networkidle")

            page.wait_for_selector("#msg-input", timeout=15000)

            print(f"Sending '{args.message}' {args.count} times...")

            for i in range(args.count):
                print(f"[{i+1}/{args.count}] Sending...")

                # Send via UI
                page.fill("#msg-input", args.message)
                page.keyboard.press("Enter")

                # API fallback
                page.evaluate(
                    """async (msg) => {
                        await fetch('/api/messages', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                username: sessionStorage.getItem('chat_username'),
                                message: msg
                            })
                        });
                    }""",
                    args.message
                )

                time.sleep(args.delay)

            print("Done. Check the chat.")
            browser.close()

    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()