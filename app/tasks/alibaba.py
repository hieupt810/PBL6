from pathlib import Path
from uuid import uuid4

import requests
from sqlmodel import Session, select

from app.core.crawler import Driver
from app.core.db import engine
from app.logger import get_logger
from app.models.product import Product

logger = get_logger(__name__)


def crawl_product(driver: Driver, index: int) -> None:
    url = driver.get_attribute(f".hugo4-pc-grid-item:nth-child({index + 1}) a", "href")
    if not url:
        raise Exception("Error to find product URL")

    try:
        driver.open_link(url)
        name = driver.get_text(".product-title-container > h1")
        price = driver.get_text(".product-price .price")
        driver.click_button(
            ".id-absolute.id-bottom-0.id-left-0.id-right-0.id-top-0.id-bg-black.id-opacity-5:nth-child(2)"
        )
        image = driver.get_attribute(".id-relative.id-h-full.id-w-full img", "src")
        description_html = driver.get_html(".module_attribute > .attribute-layout > .attribute-info")
        description = str(description_html)

        with Session(engine) as session:
            stmt = select(Product).where(Product.name == name)
            if session.exec(stmt).first():
                return

            # Download the image from url
            image_data = requests.get(image).content
            image_path = Path(f"app/images/{uuid4()}.jpg")
            image_path.parent.mkdir(parents=True, exist_ok=True)
            with open(image_path, "wb") as f:
                f.write(image_data)
            print("Description: " + description)
            product = Product(name=name, price=price, image=image, base=url, description = description)

            # product = Product(name=name, price=price, image=image, base=url)

            session.add(product)
            session.commit()
            print("Added product to database")

    except Exception:
        raise Exception("Error while crawling product")
    finally:
        driver.close_current_tab()


def crawl_alibaba():
    driver = Driver(remote=True)
    try:
        driver.get("https://www.alibaba.com/")
        driver.click_link(".ranking-card-box > .ranking-title > .view-more")
        driver.click_button(
            ".tab-wrapper.level-2 > .tab-inner-wrapper > .tab-item:nth-child(2)"
        )
        driver.scroll_to_bottom()

        for i in range(3):
            driver.click_link(
                f".hugo4-pc-grid .hugo4-pc-grid-item:nth-child({i + 1}) a"
            )
            driver.scroll_to_bottom()
            for j in range(3):
                try:
                    crawl_product(driver, j)
                except Exception:
                    continue

            driver.close_current_tab()
    except Exception as e:
        logger.error(e)
    finally:
        driver.quit()
