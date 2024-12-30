from pathlib import Path
import time
from uuid import uuid4

import requests
from app.utils import predict, save_image
from sqlmodel import Session, select
from bs4 import BeautifulSoup
from app.core.crawler import Driver
from app.core.db import engine
from app.models.product import Product
import json


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

    # Lấy URL sản phẩm từ thẻ <a>
    url = driver.get_attribute(f"#mainList > div > ul > li:nth-child({index}) a", "href").strip()
    print(f"Product URL: {url}")  # In ra URL sản phẩm
    if not url:
        raise Exception("Error to find product URL")


    try:
        name = driver.get_text(f"#mainList > div > ul > li:nth-child({index}) .pro-name").strip()
        print(name)
        price = driver.get_text(f"#mainList > div > ul > li:nth-child({index}) .pro-price strong").strip()
        print(price)
        image = driver.get_attribute(f"#mainList > div > ul > li:nth-child({index}) img", "src")
        # print(str(image))
        filename = save_image(image)
        #predict
        time.sleep(5)
        category, probs = predict(filename)
        print(f"Predicted category {category} with probability is {probs}%")
        time.sleep(5)
        #mở url detail
        driver.open_link(url)
        print("INDEX: " + str(index))
        print("OPENED: "  + url)
        description_html = driver.get_html(".prodSpecifications_prodSpecifications__iKzXe")
        description = str(extract_attributes(description_html))
        print(description)
        with Session(engine) as session:
            stmt = select(Product).where(Product.name == name)
            if session.exec(stmt).first():
                return
            product = Product(
                name=name,
                price=price,
                category="category.lower()",
                image=filename,
                base_url=url,
                description=description,
            )
            session.add(product)
            session.commit()
            print("Added product " + name + " to database")

    except Exception:
        print("Error while crawling product")
    finally:
        driver.close_current_tab()
        print("CLOSE TAB " + url)
        print("---------------------------------------------------------------------------------------")


def dhgate():
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
        print(str(e))
    finally:
        driver.quit()