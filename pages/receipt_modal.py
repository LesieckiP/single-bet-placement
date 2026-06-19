import re

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ReceiptModal(BasePage):
    MODAL_ROOT = (By.ID, "modal-success")
    MATCH = (By.ID, "modal-success-match")
    STAKE = (By.ID, "modal-success-stake")
    ODDS = (By.ID, "modal-success-odds")
    PAYOUT = (By.ID, "modal-success-payout")
    BET_ID = (By.ID, "modal-success-bet-id")
    CLOSE_BUTTON = (By.ID, "modal-success-close")
    CLOSE_X_BUTTON = (By.ID, "modal-success-close-x")

    def is_displayed(self) -> bool:
        return self.is_visible(self.MODAL_ROOT)

    def get_match(self) -> str:
        return self.find_element(self.MATCH).text

    def get_stake(self) -> float:
        return float(re.sub(r"[^\d.]", "", self.find_element(self.STAKE).text))

    def get_odds(self) -> float:
        return float(self.find_element(self.ODDS).text)

    def get_payout(self) -> float:
        return float(re.sub(r"[^\d.]", "", self.find_element(self.PAYOUT).text))

    def get_bet_id(self) -> str:
        return self.find_element(self.BET_ID).text

    def close(self):
        self.click(self.CLOSE_BUTTON).click()

    def close_x(self):
        self.click(self.CLOSE_X_BUTTON).click()
