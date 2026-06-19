from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class BetSlipPage(BasePage):
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    VALIDATION_MESSAGE = (By.CSS_SELECTOR, "#bet-slip .stakeWarning")
    PLACE_BET_BUTTON = (By.ID, "bet-slip-place-bet")

    def get_bet_slip_stake_input(self):
        return self.find_element(self.STAKE_INPUT)
    
    def input_bet_slip_stake(self, stake: float):
        return self.type_text(self.STAKE_INPUT, stake)
    
    def get_validation_message(self):
        return self.find_element(self.VALIDATION_MESSAGE).text
    
    def get_place_bet_button(self):
        return self.find_element(self.PLACE_BET_BUTTON)