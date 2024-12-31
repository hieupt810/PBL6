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
    category = "Specification"
    attribute_data[category] = {}
    spec_items = soup.select(".prodSpecifications_showUl__fmY8y li")

    for item in spec_items:
        key = item.find("span").text.strip().replace(":", "").strip()
        value_div = item.find("div", class_="prodSpecifications_deswrap___Z092")
        if value_div:
            value = (
                value_div.find("a").text.strip()
                if value_div.find("a")
                else value_div.text.strip()
            )
            attribute_data[category][key] = value

    return json.dumps(attribute_data)


def crawl_product(driver: Driver, index: int) -> None:
    url = driver.get_attribute(
        f"#mainList > div > ul > li:nth-child({index}) a", "href"
    ).strip()
    if not url:
        raise Exception("URL not found.")

    try:
        name = driver.get_text(
            f"#mainList > div > ul > li:nth-child({index}) .pro-name"
        ).strip()
        price = driver.get_text(
            f"#mainList > div > ul > li:nth-child({index}) .pro-price strong"
        ).strip()
        image = driver.get_attribute(
            f"#mainList > div > ul > li:nth-child({index}) img", "src"
        )

        filename = save_image(image)
        logger.debug(f"Saved image to {filename}")

        category, probs = predict(filename)
        logger.info(f"Predicted category {category} with probability is {probs}%")

        driver.open_link(url)
        description_html = driver.get_html(
            ".prodSpecifications_prodSpecifications__iKzXe"
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
                probability=probs,
                image=filename,
                base_url=url,
                description=description,
            )
            session.add(product)
            session.commit()
            logger.info(f"Product {product.id} has been saved to database.")
    except Exception as e:
        logger.error(e)
    finally:
        driver.close_current_tab()


def dhgate():
    driver = Driver(remote=True)
    try:
        driver.get("https://www.dhgate.com/")
        driver.click_link(
            ".topRanking_topRanking__H2V_w > .topRanking_topTitle__3Mz1P > .topRanking_topViewAll__5lAdy"
        )
        for i in range(6):
            driver.click_button(
                f".swiper-container.swiper-container-initialized.swiper-container-horizontal > .swiper-wrapper > .swiper-slide:nth-child({i + 1})"
            )
            products_count = len(driver.find_elements("#mainList > div > ul > li"))
            for j in range(products_count):
                try:
                    time.sleep(1)
                    crawl_product(driver, j + 1)
                except Exception:
                    continue
        driver.close_current_tab()
    except Exception as e:
        logger.error(e)
    finally:
        driver.quit()
