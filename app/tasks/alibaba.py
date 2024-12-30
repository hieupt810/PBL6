import json
import time

from bs4 import BeautifulSoup
from sqlmodel import Session, select

from app.core.crawler import Driver
from app.core.db import engine
from app.logging import get_logger
from app.models.product import Product
from app.utils import predict, save_image

logger = get_logger(__name__)


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
        raise ValueError("Error to find product URL.")

    try:
        name = driver.get_text(
            f"{base_selector} > a > div > div.subject > span"
        ).strip()
        price = driver.get_text(
            f"{base_selector} > a > div > div.hugo4-product-price-area > div > div"
        ).strip()

        # Get product image and predict category
        image = driver.get_attribute(f"{base_selector} > a > div > div > img", "src")
        filename = save_image(image)
        category, probs = predict(filename)
        logger.info(f"Predicted category {category} with probability is {probs}%")

        # Get product description
        driver.open_link(url)
        description_html = driver.get_html(
            ".module_attribute > .attribute-layout > .attribute-info"
        )
        description = str(extract_attributes(description_html))

        # Save product to database
        with Session(engine) as session:
            stmt = select(Product).where(Product.name == name)
            if session.exec(stmt).first():
                return

            product = Product(
                name=name,
                price=price,
                category=category.lower(),
                image=filename,
                probability=probs,
                base_url=url,
                description=description,
            )
            session.add(product)
            session.commit()
            logger.info(f"Product with id {product.id} has been added.")
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Something went wrong while getting product details.")
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

            for num in range(10):
                try:
                    get_product(driver, num)
                    time.sleep(1)
                except Exception as e:
                    logger.error(e)
    except Exception as e:
        logger.error(e)
    finally:
        driver.quit()
        time.sleep(5)
