from pathlib import Path
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


# def extract_attributes(html):
#     soup = BeautifulSoup(html, 'html.parser')

#     attribute_data = {}

#     for heading in soup.find_all('h3'):
#         category = heading.text.strip()
#         attribute_data[category] = {}

#         attribute_list = heading.find_next_sibling('div', class_='attribute-list')
#         if attribute_list:
#             for item in attribute_list.find_all('div', class_='attribute-item'):
#                 left_div = item.find('div', class_='left')
#                 right_div = item.find('div', class_='right')
#                 if left_div and right_div:
#                      key = left_div.text.strip()
#                      value = right_div.find('span').text.strip()
#                      attribute_data[category][key] = value
#     return json.dumps(attribute_data)

def crawl_product(driver: Driver, index: int) -> None:
    url = driver.get_attribute(f".ul > .li:nth-child({index}) > a", "href")
    if not url:
        raise Exception("Error to find product URL")

    try:
        driver.open_link(url)
        name = driver.get_text(".productMain_productMain__AVkr2 > .productMain_productMainRight__ZVyY1 > .productInfo_productInfoWarp__3em82 > .productInfo_productInfo__V8sBz > h1")
        price = driver.get_text(".productMain_productMain__AVkr2 > .productMain_productMainRight__ZVyY1 > .prodTotal_prodTotalWrap__igF18 > .prodTotal_prodTotal___vdH_ > .prodTotal_total__dSPWE")
        # driver.click_button(
        #     ".id-absolute.id-bottom-0.id-left-0.id-right-0.id-top-0.id-bg-black.id-opacity-5:nth-child(2)"
        # )
        # image = driver.get_attribute(".id-relative.id-h-full.id-w-full img", "src")
        # description_html = driver.get_html(".module_attribute > .attribute-layout > .attribute-info")
        # description = str(extract_attributes(description_html))

        with Session(engine) as session:
            stmt = select(Product).where(Product.name == name)
            if session.exec(stmt).first():
                return

            # Download the image from url
            # image_data = requests.get(image).content
            image_path = Path(f"app/images/{uuid4()}.jpg")
            image_path.parent.mkdir(parents=True, exist_ok=True)
            # with open(image_path, "wb") as f:
            #     f.write(image_data)
            # print("Description: " + description)
            product = Product(name=name, price=price, image="", base=url, description = "description")

            # product = Product(name=name, price=price, image=image, base=url)

            session.add(product)
            session.commit()
            print("Added product to database")

    except Exception:
        raise Exception("Error while crawling product")
    finally:
        driver.close_current_tab()


def crawl_dhgate():
    driver = Driver(remote=True)
    try:
        driver.get("https://www.dhgate.com/")
        driver.click_link(".topRanking_topRanking__H2V_w > .topRanking_topTitle__3Mz1P > .topRanking_topViewAll__5lAdy")

        for i in range(6):
            driver.click_button(
                f".swiper-container.swiper-container-initialized.swiper-container-horizontal > .swiper-wrapper > .swiper-slide:nth-child({i + 1})"
            )
            for i in range(3):
                for j in range(5):
                    try:
                        crawl_product(driver, i + j + 1)
                    except Exception:
                        continue

                driver.close_current_tab()


        # driver.scroll_to_bottom()

        # for i in range(3):
        #     driver.click_link(
        #         f".hugo4-pc-grid .hugo4-pc-grid-item:nth-child({i + 1}) a"
        #     )
        #     driver.scroll_to_bottom()
        #     for j in range(3):
        #         try:
        #             crawl_product(driver, j)
        #         except Exception:
        #             continue

    except Exception as e:
        logger.error(e)
    finally:
        driver.quit()
