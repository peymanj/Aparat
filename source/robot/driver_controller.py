from .chrome_driver import chrome_driver
# from firefox_driver import firefox_driver



def get_driver(driver_selection, show_browser):
    #new coment line
    # if driver_selection == "firefox":
    #     driver = firefox_driver()
    if driver_selection == "chrome":
        driver = chrome_driver(show_browser)
    return driver
