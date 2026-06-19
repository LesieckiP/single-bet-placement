from jproperties import Properties


class ConfigurationManager:
    __configs = Properties()
    with open("resources/config.properties", "rb") as __config_file:
        __configs.load(__config_file)

    @staticmethod
    def browser() -> str:
        return ConfigurationManager.__configs["browser"].data
    
    @staticmethod
    def app_url() -> str:
        return ConfigurationManager.__configs["app_url"].data
    
    @staticmethod
    def api_url() -> str:
        return ConfigurationManager.__configs["api_url"].data

    @staticmethod
    def username() -> str:
        return ConfigurationManager.__configs["username"].data

    @staticmethod
    def min_stake() -> float:
        return float(ConfigurationManager.__configs["min_stake"].data)

    @staticmethod
    def max_stake() -> float:
        return float(ConfigurationManager.__configs["max_stake"].data)