# supported colors in result table - https://rich.readthedocs.io/en/stable/appendix/colors.html

from random import randint

# for debug, set False to open browser and see what happens
headless = True

# format shoud be 'ip:port:login:pass', if login and/or pass empty just omit it 'ip:port::'
aave_proxy = ''
# delay between requests, min/max, in seconds
aave_request_delay = randint(0, 0)
# max timeout for searches on page, in seconds
aave_timeout = 60
# stdout color in result table
aave_font_color = 'red'
# timeout for element search on page, in milliseconds
aave_expect_timeout = 30_000

morpho_proxy = ''
morpho_request_delay = randint(0, 0)
# delay between search on page, not recommended to set < 1, in seconds
morpho_search_delay = 1
morpho_timeout = 60
morpho_font_color = 'dodger_blue2'
morpho_expect_timeout = 30_000

fluid_proxy = ''
fluid_request_delay = randint(0, 0)
fluid_search_delay = 1
fluid_timeout = 60
fluid_font_color = 'cyan'
fluid_expect_timeout = 30_000

compound_proxy = ''
compound_request_delay = randint(0, 0)
compound_timeout = 60
compound_font_color = 'green3'
compound_expect_timeout = 30_000
