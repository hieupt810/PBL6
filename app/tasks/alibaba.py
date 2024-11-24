from sqlmodel import Session

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
        title = driver.get_text(".product-title-container > h1")
        price = driver.get_text(".product-price .price")
        driver.click_button(
            ".id-absolute.id-bottom-0.id-left-0.id-right-0.id-top-0.id-bg-black.id-opacity-5:nth-child(2)"
        )
        image = driver.get_attribute(".id-relative.id-h-full.id-w-full img", "src")
        product = Product(title=title, price=price, image_url=image, url=url)
        with Session(engine) as session:
            session.add(product)
            session.commit()
    except Exception as e:
        logger.error(e)
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

        for i in range(5):
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
