#!/usr/bin/env python3
"""
Send the same chat message multiple times with a configurable delay.
"""

import argparse
import os
import sys
import time
from playwright.sync_api import sync_playwright

URL = "https://bonfire-ho38.onrender.com/chat"


def main():
    parser = argparse.ArgumentParser(description="Spam a message via Playwright")

    # 🔹 Single message
    parser.add_argument(
        "--message",
        default="Wsg my blud",
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
    parser.add_argument(
        "--token",
        default=os.environ.get("SESSION_TOKEN"),
        help="Session token to use for x-session-token authentication"
    )
    parser.add_argument("--headless", action="store_true", help="Run headless")

    args = parser.parse_args()

    if not args.token:
        print("Error: --token is required or set SESSION_TOKEN", file=sys.stderr)
        sys.exit(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=args.headless)
            context = browser.new_context()

            # Inject localStorage values before page loads
            context.add_init_script(f"""
                localStorage.setItem('chat_username', '{args.username}');
                localStorage.setItem('chat_token', '{args.token}');
                localStorage.setItem('chat_isAdmin', 'no');
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

                page.evaluate(
                    """async ({ msg, token }) => {
                        await fetch('/api/messages/global', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'x-session-token': token,
                                'Accept': '*/*',
                                'Accept-Language': 'en,en-US;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                                'Referer': 'https://bonfire-ho38.onrender.com/chat'
                            },
                            body: JSON.stringify({ message: msg })
                        });
                    }""",
                    { "msg": args.message, "token": args.token }
                )

                time.sleep(args.delay)

            print("Done. Check the chat.")
            browser.close()

    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()