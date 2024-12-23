from pathlib import Path
import time
from uuid import uuid4

import requests
from sqlmodel import Session, select
from bs4 import BeautifulSoup
from app.core.crawler import Driver
from app.core.db import engine
from app.logger import get_logger
from app.models.product import Product
import json

logger = get_logger(__name__)


def extract_attributes(html):
    soup = BeautifulSoup(html, 'html.parser')

    attribute_data = {}
    category = "Specification"  # Tạo category mặc định là "Specification"
    attribute_data[category] = {}

    # Tìm tất cả các thẻ li trong phần specifications
    spec_items = soup.select('.prodSpecifications_showUl__fmY8y li')

    for item in spec_items:
        # Lấy key (phần text trước dấu :)
        key = item.find('span').text.strip().replace(':', '').strip()

        # Lấy value (phần text trong div)
        value_div = item.find('div', class_='prodSpecifications_deswrap___Z092')
        if value_div:
            # Nếu có thẻ a bên trong, lấy text của thẻ a
            value = value_div.find('a').text.strip() if value_div.find('a') else value_div.text.strip()
            attribute_data[category][key] = value

    return json.dumps(attribute_data)

def crawl_product(driver: Driver, index: int) -> None:
    print("CRAWLING----------------------------------------------------------------------------------")
    url = driver.get_attribute(f"#mainList > div > ul > li:nth-child({index}) > a", "href")
    print(url)
    if not url:
        raise Exception("Error to find product URL")

    try:
        driver.open_link(url)
        print("INDEX: " + str(index))
        print("OPENED: "  + url)

        name = driver.get_text(".productInfo_productInfo__V8sBz > h1")
        print(name)
        price = driver.get_text(".productPrice_priceWarp__rWYY7 .productPrice_price__LcDwB")
        print(price)
        image = driver.get_attribute("#masterImg", "src")
        print(str(image))
        description_html = driver.get_html(".prodSpecifications_prodSpecifications__iKzXe")
        description = str(extract_attributes(description_html))
        print(description)
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
            product = Product(name=name, price=price, image=image, base=url, description = description)
            session.add(product)
            session.commit()
            print("Added product " + name + " to database")

    except Exception:
        print("Error while crawling product")
    finally:
        driver.close_current_tab()
        print("CLOSE TAB " + url)
        print("---------------------------------------------------------------------------------------")


def crawl_dhgate():
    driver = Driver(remote=True)
    try:
        driver.get("https://www.dhgate.com/")
        driver.click_link(".topRanking_topRanking__H2V_w > .topRanking_topTitle__3Mz1P > .topRanking_topViewAll__5lAdy")

        for i in range(6):
            driver.click_button(
                f".swiper-container.swiper-container-initialized.swiper-container-horizontal > .swiper-wrapper > .swiper-slide:nth-child({i + 1})"
            )
            products_count = len(driver.find_elements("#mainList > div > ul > li"))
            print("THIS SWIPE_SLIDE HAVE: " + str(products_count) + " PRODUCTS")
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
