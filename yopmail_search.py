import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def find_next_button(driver):
    """ Ищет кнопку 'следующая страница' по всем известным селекторам yopmail.
    Возвращает элемент если найден и активен, иначе None.
    """
    selectors = [
        (By.ID, "napb"),       # <input id="napb" value="Next" onclick="mnext()">
        (By.ID, "pagnxt"),     # старый вариант
        (By.CSS_SELECTOR, "input[onclick='mnext()']"),
        (By.CSS_SELECTOR, "input[value='Next']"),
        (By.CSS_SELECTOR, "a[onclick*='next']"),
        (By.XPATH, "//input[@value='Next' or @value='next' or @id='napb']"),
        (By.XPATH, "//a[contains(@onclick,'next') or contains(@title,'Next')]")
    ]
    for by, selector in selectors:
        try:
            elements = driver.find_elements(by, selector)
            for el in elements:
                if el.is_displayed() and el.is_enabled():
                    classes = el.get_attribute("class") or ""
                    if "pagination-off" in classes or "disabled" in classes:
                        continue
                    return el
        except Exception:
            continue
    return None

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

            next_btn = find_next_button(driver)
            if next_btn is None:
                print(f"  Следующей страницы нет, завершаем на странице {page}.")
                break

            print(f"  Переходим на страницу {page + 1}...")
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