#!/usr/bin/env python

import re
import os
import sys
import smtplib
import getpass
import argparse
import mimetypes

from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import time
time.sleep(1)
print("[+] Initializing modules...")
time.sleep(1)

try:
    import smtplib
except Exception as e:
    print("[!] Missing module:", e)
    sys.exit()

# =========================
# BANNER
# =========================
def banner():
    print(r"""
    ____         ____  __    _        __
   / __ \__ __/ __ \/ /_  (_)____/ /_  ___  _____
  / /_/ / / / / /_/ / __ \/ / ___/ __ \/ _ \/ ___/
 / ____/ /_/ / ____/ / / / (__  ) / / /  __/ /
/_/    \__, /_/   /_/ /_/_/____/_/ /_/\___/_/
      /____/

Created By: Andrew Cadiz 
""")



def phish(args):
    message_html = open_html_file(args.html)
    html_output = replace_links(args.url_replace, message_html)

    attachment = None
    if args.attachment and os.path.isfile(args.attachment):
        attachment = add_attachment(args.attachment)

    message = mime_message(
        args.subject,
        args.sendto,
        args.sender,
        html_output,
        attachment
    )

   
    if args.sendto:
        send_email(
            args.server,
            args.port,
            args.username,
            args.password,
            args.sender,
            args.sendto,
            message,
            args.starttls
        )

    elif args.list_sendto:
        if not os.path.isfile(args.list_sendto):
            print("[!] Invalid file:", args.list_sendto)
            sys.exit()

        with open(args.list_sendto, "r") as handler:
            sendtos = handler.read().splitlines()

        for sendto in sendtos:
            send_email(
                args.server,
                args.port,
                args.username,
                args.password,
                args.sender,
                sendto.strip(),
                message,
                args.starttls
            )
    else:
        print("[!] Provide --sendto or --list-sendto")



def open_html_file(file):
    with open(file, "r", encoding="utf-8") as f:
        return f.read()


def replace_links(url, message):
    if not url:
        return message

    html_regex = re.compile(r'href=[\'"]?([^\'" >]+)')
    return html_regex.sub(f'href="{url}"', message)



def mime_message(subject, sendto, sender, html, attachment):
    msg = MIMEMultipart("alternative")
    msg["To"] = sendto
    msg["From"] = sender
    msg["Subject"] = subject

    msg.attach(MIMEText(html, "html"))

    if attachment:
        msg.attach(attachment)

    return msg.as_string()



def add_attachment(filepath):
    mime_type, _ = mimetypes.guess_type(filepath)

    if mime_type is None:
        mime_type = "application/octet-stream"

    major, minor = mime_type.split("/", 1)

    with open(filepath, "rb") as f:
        part = MIMEBase(major, minor)
        part.set_payload(f.read())

    encoders.encode_base64(part)

    filename = os.path.basename(filepath)
    part.add_header(
        "Content-Disposition",
        f'attachment; filename="{filename}"'
    )

    return part



def send_email(server, port, username, password,
               sender, sendto, message, starttls):

    print("[+] Connecting to server...")
    smtp = smtplib.SMTP(server, port)
    smtp.ehlo()

    if starttls:
        print("[+] Using STARTTLS")
        smtp.starttls()
        smtp.ehlo()

    if username:
        print("[+] Authenticating...")
        if not password:
            password = getpass.getpass(
                f"Password for {username}: "
            )
        smtp.login(username, password)

    print(f"[+] Sending mail to {sendto}")
    smtp.sendmail(sender, sendto, message)

    print("[+] Done!")
    smtp.quit()



def main():
    banner()

    parser = argparse.ArgumentParser()

    parser.add_argument("--server", required=True,
                        help="SMTP server")

    parser.add_argument("--port", required=True, type=int,
                        help="SMTP port")

    parser.add_argument("--username",
                        help="SMTP username")

    parser.add_argument("--password",
                        help="SMTP password")

    parser.add_argument("--html", required=True,
                        help="HTML email file")

    parser.add_argument("--url_replace",
                        help="Replace links with URL")

    parser.add_argument("--subject", required=True,
                        help="Email subject")

    parser.add_argument("--sender", required=True,
                        help="Sender email")

    parser.add_argument("--sendto",
                        help="Destination email")

    parser.add_argument("--start-tls",
                        dest="starttls",
                        action="store_true",
                        help="Enable STARTTLS")

    parser.add_argument("--list-sendto",
                        help="File with email list")

    parser.add_argument("--attachment",
                        help="Attachment file")

    args = parser.parse_args()

    phish(args)


if __name__ == "__main__":
    main()
