import re

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class MainPage(BasePage):
    BALANCE_ELEMENT = (By.ID, "header-balance")
    FIRST_POSSIBLE_ODDS_BUTTON = (By.CSS_SELECTOR, "#match-list div button")

    def get_title(self):
        return self.driver.title
    
    def get_balance(self):
        balance_str = self.find_element(self.BALANCE_ELEMENT).text
        return float(re.sub(r"[^\d.]", "", balance_str))
    
    def click_first_possible_odds_button(self):
        return self.find_element(self.FIRST_POSSIBLE_ODDS_BUTTON).click()