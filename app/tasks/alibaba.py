import json

from bs4 import BeautifulSoup
from sqlmodel import Session, select

from app.core.crawler import Driver
from app.core.db import engine
from app.models.product import Product
from app.utils import predict, save_image


def extract_attributes(html):
    soup = BeautifulSoup(html, "html.parser")
    attribute_data = {}
    for heading in soup.find_all("h3"):
        category = heading.text.strip()
        attribute_data[category] = {}
        attribute_list = heading.find_next_sibling("div", class_="attribute-list")

        if attribute_list:
            for item in attribute_list.find_all("div", class_="attribute-item"):
                left_div = item.find("div", class_="left")
                right_div = item.find("div", class_="right")

                if left_div and right_div:
                    key = left_div.text.strip()
                    value = right_div.find("span").text.strip()
                    attribute_data[category][key] = value

    return json.dumps(attribute_data)


def get_product(driver: Driver, num: int) -> None:
    base_selector = f".hugo4-pc-grid-item.top-ranking-card:nth-child({num + 1})"
    url = driver.get_attribute(f"{base_selector} > a", "href")
    if not url:
        raise Exception("Error to find product URL.")

    name = driver.get_text(f"{base_selector} > a > div > div.subject > span")
    price = driver.get_text(
        f"{base_selector} > a > div > div.hugo4-product-price-area > div > div"
    )

    # Get product image and predict category
    image = driver.get_attribute(f"{base_selector} > a > div > div > img", "src")
    filename = save_image(image)
    category, probs = predict(filename)
    print(f"[AI] Predicted category: {category} with probability: {probs}")

    try:
        driver.open_link(url)
        description_html = driver.get_html(
            ".module_attribute > .attribute-layout > .attribute-info"
        )
        description = str(extract_attributes(description_html))
        with Session(engine) as session:
            stmt = select(Product).where(Product.name == name)
            if session.exec(stmt).first():
                return

            product = Product(
                name=name,
                price=price,
                category=category.lower(),
                image=filename,
                base_url=url,
                description=description,
            )
            session.add(product)
            session.commit()
    except Exception:
        raise Exception("Something went wrong while getting product details.")
    finally:
        driver.close_current_tab()


def alibaba():
    driver = Driver(remote=True)
    try:
        driver.get("https://www.alibaba.com")
        driver.scroll_to_bottom()

        driver.click_link(".ranking-title > a")
        driver.click_button(".tab-wrapper.level-2 > div > div:nth-child(2) > div")
        driver.scroll_to_bottom()

        elements = driver.find_elements(".hugo4-pc-grid-item > div > div")
        for i in range(len(elements)):
            driver.click_link(
                f".hugo4-pc-grid-item:nth-child({i + 1}) > div > div > div > a"
            )
            driver.scroll_to_bottom()

            for num in range(5):
                try:
                    get_product(driver, num)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)
    finally:
        driver.quit()
