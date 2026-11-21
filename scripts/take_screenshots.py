import os
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = BASE_DIR / "docs" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

PORT = 8009
ENV = os.environ.copy()
ENV["DATABASE_URL"] = "sqlite:///db.sqlite3"
ENV["DEBUG"] = "True"
ENV["ALLOWED_HOSTS"] = "localhost,127.0.0.1"


def run_cmd(cmd):
    return subprocess.run(cmd, env=ENV, cwd=BASE_DIR, check=True)


def take_screenshot(url, output_path, window_size="1280,850"):
    profile_dir = Path("/tmp/ff_screenshots_profile")
    profile_dir.mkdir(parents=True, exist_ok=True)
    firefox_cmd = [
        "firefox",
        "--headless",
        "--profile",
        str(profile_dir),
        f"--window-size={window_size}",
        f"--screenshot={output_path}",
        url,
    ]
    subprocess.run(firefox_cmd, env=ENV, cwd=BASE_DIR, check=True)
    print(f"✓ Screenshot captured: {output_path.name}")


def main():
    print("Preparando banco e seed para captura de screenshots...")
    run_cmd([BASE_DIR / ".venv" / "bin" / "python", "manage.py", "migrate"])
    run_cmd([BASE_DIR / ".venv" / "bin" / "python", "manage.py", "seed_demo"])

    server_cmd = [
        BASE_DIR / ".venv" / "bin" / "python",
        "manage.py",
        "runserver",
        f"127.0.0.1:{PORT}",
        "--noreload",
    ]
    print(f"Iniciando dev server em 127.0.0.1:{PORT}...")
    server = subprocess.Popen(server_cmd, env=ENV, cwd=BASE_DIR)
    time.sleep(2.5)

    try:
        base_url = f"http://127.0.0.1:{PORT}"

        # 1. Home Desktop Dark
        take_screenshot(
            f"{base_url}/",
            SCREENSHOTS_DIR / "01_home_dark.png",
            window_size="1280,900",
        )

        # 2. Post Detail Desktop Dark
        take_screenshot(
            f"{base_url}/posts/arquitetura-resiliente-deploy-custo-zero/",
            SCREENSHOTS_DIR / "02_post_detail_dark.png",
            window_size="1280,1050",
        )

        # 3. About Page Desktop Dark
        take_screenshot(
            f"{base_url}/sobre/",
            SCREENSHOTS_DIR / "03_about_dark.png",
            window_size="1280,850",
        )

        # 4. 404 ASCII Terminal Page
        take_screenshot(
            f"{base_url}/pagina-inexistente-404/",
            SCREENSHOTS_DIR / "04_404_terminal.png",
            window_size="1280,750",
        )

        # 5. Dashboard Login Screen
        admin_path = ENV.get("ADMIN_PATH", "painel-gestao").strip("/")
        take_screenshot(
            f"{base_url}/{admin_path}/login/",
            SCREENSHOTS_DIR / "05_dashboard_login.png",
            window_size="1280,800",
        )

        # 6. Mobile Home Viewport (iPhone 14 size)
        take_screenshot(
            f"{base_url}/",
            SCREENSHOTS_DIR / "06_mobile_home_dark.png",
            window_size="390,844",
        )

        print("\nTodas as capturas foram concluídas com sucesso!")
    finally:
        server.terminate()
        server.wait()
        print("Servidor de desenvolvimento encerrado.")


if __name__ == "__main__":
    main()
