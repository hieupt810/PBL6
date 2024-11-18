from app.core.crawler import Driver


def crawl_product(driver: Driver, index: int):
    driver.click_link(f".hugo4-pc-grid-item:nth-child({index + 1}) a")
    title = driver.get_text(".product-title-container > h1")
    price = driver.get_text(".product-price .price")

    # Image
    driver.click_button(
        ".id-absolute.id-bottom-0.id-left-0.id-right-0.id-top-0.id-bg-black.id-opacity-5:nth-child(2)"
    )
    image = driver.get_image(".id-relative.id-h-full.id-w-full img")

    driver.close_current_tab()
    return {"title": title, "price": price, "image": image}


def crawl_alibaba():
    driver = Driver(remote=True, action_wait_second=1, load_wait_second=5)
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
            for j in range(5):
                product = crawl_product(driver, j)
                print(product)
            driver.close_current_tab()
    finally:
        driver.quit()
