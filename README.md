# Important
* Part A of the project is located within [part_a](./part_a/) directory
* You can see [my comments](./MY_COMMENTS.md) to understand some approaches i took and where i used the AI and why.



# Test Automation project

## First steps

### Basic structure
- config_properties for common variables and browser
- browser_manager and configuration_manager to handle the browser opening and support two for the beginning - Chrome and Firefox
- base_page.py for common helpers
- main_page.py to handle the app page
- pytest.ini to create TestCase id marker
- created structure for api tests representation in ./endpoints and ./endpoints/models for the schema checks