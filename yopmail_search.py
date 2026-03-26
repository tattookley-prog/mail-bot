import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-sync")
    options.add_argument("--no-first-run")
    options.add_argument("--blink-settings=imagesEnabled=false")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver

def search_yopmail(inbox, keywords):
    print(f"\n  Запускаем браузер...")
    driver = create_driver()

    try:
        print(f"  Открываем YOPmail...")
        driver.get("https://yopmail.com/")
        time.sleep(3)

        print(f"  Вводим логин: {inbox}")
        login_field = driver.find_element(By.ID, "login")
        login_field.clear()
        login_field.send_keys(inbox)

        btn = driver.find_element(By.CSS_SELECTOR, "button.md")
        btn.click()
        time.sleep(3)

        print(f"  Загружаем inbox...")
        driver.switch_to.frame("ifinbox")
        time.sleep(2)

        emails = driver.find_elements(By.CSS_SELECTOR, "div.m")
        print(f"  Писем найдено: {len(emails)}")

        if not emails:
            print("  Ящик пуст.")
            return

        print("=" * 50)
        found = 0

        for i, em in enumerate(emails, 1):
            text = em.text
            if any(kw.lower() in text.lower() for kw in keywords):
                found += 1
                print(f"\n  Письмо #{found}")
                print(f"  {text[:200]}")
                print("-" * 50)

        if found == 0:
            print(f"\n  Писем с ключевыми словами {keywords} не найдено.")
        else:
            print(f"\n  Итого найдено: {found}")

    except Exception as e:
        print(f"  Ошибка: {e}")
    finally:
        driver.quit()
        print("\n  Браузер закрыт.")

def main():
    print("=" * 50)
    print("   YOPmail Selenium Search Tool")
    print("=" * 50)

    if len(sys.argv) >= 3:
        inbox = sys.argv[1].strip()
        raw = sys.argv[2].strip()
    else:
        inbox = input("\n  Имя ящика (без @yopmail.com): ").strip()
        raw = input("  Ключевые слова (через запятую): ").strip()

    if not inbox:
        print("  Ошибка: введи имя ящика")
        sys.exit(1)

    keywords = [kw.strip() for kw in raw.split(",") if kw.strip()]
    if not keywords:
        print("  Ошибка: введи хотя бы одно слово")
        sys.exit(1)

    search_yopmail(inbox, keywords)

if __name__ == "__main__":
    main()