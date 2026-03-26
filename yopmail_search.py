import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

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
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "login")))

        print(f"  Вводим логин: {inbox}")
        login_field = driver.find_element(By.ID, "login")
        login_field.clear()
        login_field.send_keys(inbox)

        driver.find_element(By.ID, "refreshbut").click()

        print(f"  Загружаем inbox...")
        WebDriverWait(driver, 15).until(EC.frame_to_be_available_and_switch_to_it("ifinbox"))
        WebDriverWait(driver, 15).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, "div.m") or
                      d.find_elements(By.CSS_SELECTOR, "div.ellipsis")
        )

        found = 0
        page = 0
        total_emails = 0
        global_position = 0
        results = []

        while True:
            page += 1
            emails = driver.find_elements(By.CSS_SELECTOR, "div.m")
            count = len(emails)
            print(f"  Страница {page}: писем {count}")

            for pos_on_page, em in enumerate(emails, 1):
                global_position += 1
                text = em.text
                mail_id = em.get_attribute("id")
                if any(kw.lower() in text.lower() for kw in keywords):
                    found += 1
                    link = f"https://yopmail.com/?b={inbox}&id={mail_id}&lang=en" if mail_id else ""
                    results.append((found, text, link, page, pos_on_page, global_position))

            total_emails += count

            # Пагинация — кнопка #pagnxt внутри фрейма ifinbox
            next_btns = driver.find_elements(By.ID, "pagnxt")
            if not next_btns:
                break
            next_btn = next_btns[0]
            classes = next_btn.get_attribute("class") or ""
            if "pagination-off" in classes:
                break
            next_btn.click()
            WebDriverWait(driver, 10).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "div.m") or
                          d.find_elements(By.CSS_SELECTOR, "div.ellipsis")
            )

        print(f"  Всего просмотрено: {total_emails} писем на {page} страницах")
        print("=" * 50)

        if not results:
            print(f"\n  Писем с ключевыми словами {keywords} не найдено.")
        else:
            for num, text, link, pg, pos, glob in results:
                print(f"\n  Письмо #{num} (найдено)")
                print(f"  Местонахождение: вкладка {pg}, позиция {pos} на странице (письмо №{glob} в общем списке)")
                print(f"  {text[:200]}")
                if link:
                    print(f"  Ссылка: {link}")
                print("-" * 50)
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