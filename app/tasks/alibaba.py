import logging
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.core.crawler import Driver
from app.core.db import engine
from app.models.product import Product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def crawl_product(driver: Driver, session: Session, index: int) -> None:
    try:
        # Open product page
        shopping_href = driver.get_attribute(
            f".hugo4-pc-grid-item:nth-child({index + 1}) a", "href"
        )
        driver.open_link(shopping_href)

        # Get product information
        title = driver.get_text(".product-title-container > h1")
        price = driver.get_text(".product-price .price")
        driver.click_button(
            ".id-absolute.id-bottom-0.id-left-0.id-right-0.id-top-0.id-bg-black.id-opacity-5:nth-child(2)"
        )
        image = driver.get_attribute(".id-relative.id-h-full.id-w-full img", "src")

        # Close product page
        driver.close_current_tab()
    except Exception:
        raise Exception("Error while getting product information")

    # Add product to database
    try:
        product = session.exec(select(Product).filter(Product.title == title)).one()
        if not product:
            product = Product(
                title=title, price=price, image_href=image, shopping_href=shopping_href
            )
            session.add(product)
    except Exception:
        raise Exception("Error while adding product to database")


def crawl_alibaba():
    driver = Driver(remote=True)
    try:
        # Open Alibaba top ranking page
        driver.get("https://www.alibaba.com/")
        driver.click_link(".ranking-card-box > .ranking-title > .view-more")
        driver.click_button(
            ".tab-wrapper.level-2 > .tab-inner-wrapper > .tab-item:nth-child(2)"
        )
        driver.scroll_to_bottom()

        with Session(engine) as session:
            # Delete products created more than 30 days ago
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            products = session.exec(
                select(Product).filter(Product.created_at < thirty_days_ago)
            )
            for product in products:
                session.delete(product)

            # Crawl products
            for i in range(5):
                driver.click_link(
                    f".hugo4-pc-grid .hugo4-pc-grid-item:nth-child({i + 1}) a"
                )
                driver.scroll_to_bottom()
                for j in range(5):
                    crawl_product(driver, session, j)

                driver.close_current_tab()

            session.commit()
    except Exception as e:
        logger.error(e)
    finally:
        driver.quit()
