import json

from bs4 import BeautifulSoup
from sqlmodel import Session, select

from app.core.crawler import Driver
from app.core.db import engine
from app.models.filter import Constant
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
        description_html = driver.get_html(
            ".module_attribute > .attribute-layout > .attribute-info"
        )
        description = str(extract_attributes(description_html))

        with Session(engine) as session:
            stmt = select(Product).where(Product.name == name)
            if session.exec(stmt).first():
                return

            image_path = save_image(image)
            predict_category = predict(image_path)
            category = session.exec(
                select(Constant).where(Constant.name == predict_category)
            ).first()
            product = Product(
                name=name,
                price=price,
                category_id=category.id,
                image=image_path,
                base=url,
                description=description,
            )
            session.add(product)
            session.commit()

            print(f"Product with id = {product.id} added to database successfully")
    except Exception:
        raise Exception("Error while crawling product")
    finally:
        driver.close_current_tab()


def alibaba():
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
        print("[ERROR] Error while crawling Alibaba", e)
    finally:
        driver.quit()
