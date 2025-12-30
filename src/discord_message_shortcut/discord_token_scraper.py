from selenium import webdriver
import time


def get_discord_token():
    driver = webdriver.Edge()
    token = ""

    try:
        driver.get("https://discord.com/login")

        # Wait until the user is no longer on the login page
        while "login" in driver.current_url:
            time.sleep(1)

        # Small buffer to ensure storage is populated
        time.sleep(2)

        script_js = """
        try {
            const iframe = document.createElement('iframe');
            document.body.appendChild(iframe);
            const token = JSON.parse(iframe.contentWindow.localStorage.token);
            iframe.remove();
            return token;
        } catch (e) {
            return null;
        }
        """

        token = driver.execute_script(script_js)
    finally:
        driver.quit()

    return str(token) if token else ""

if __name__ == "__main__":
    token = get_discord_token()
    if token:
        print(f"Discord Token: {token}")
    else:
        print("Failed to retrieve Discord token.")