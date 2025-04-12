import asyncio
import re
from asyncio import Semaphore
from fake_useragent import FakeUserAgent
from playwright.async_api import async_playwright, ProxySettings, Position, expect
from yaspin.core import Yaspin
from config import *
from sources import Source, Morpho, Aave, Fluid, Compound
from models import Mode, Pair, MorphoCheckboxCoordinates, FluidPeriodsBtnCoordinates, LendingToSearch


async def format_proxy(proxy: str | None = None) -> dict | None:
    if proxy == '' or proxy is None:
        return None

    server, port, username, password = proxy.split(':')
    proxy = {
        "server": f"http://{server}:{port}",
        "username": username,
        "password": password,
    }
    return proxy


async def aave_fill_source_sm(source: Source, proxy: ProxySettings, sp: Yaspin, semaphore: Semaphore, result_search: list[Source]):
    async with semaphore:
        await aave_fill_source(source, proxy, sp, result_search)


async def aave_fill_source(source: Source, proxy: ProxySettings, sp: Yaspin, result_search: list[Source]):
    await asyncio.sleep(aave_request_delay)

    try:
        async with asyncio.timeout(aave_timeout):
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    args=['--disable-blink-features=AutomationControlled'],
                    proxy=proxy,
                    headless=headless,
                )
                browser = await browser.new_context(user_agent=FakeUserAgent().chrome)

                aave = await browser.new_page()
                await aave.goto(source.url)
                await aave.wait_for_load_state('networkidle')

                current = aave.locator(
                    '//*[@id="__next"]/main/div[2]/div/div[2]/div[1]/div/div[4]/div/div/div[1]/div[3]/div/p')
                await expect(current).to_be_visible(timeout=aave_expect_timeout)
                await current.click()
                current_text = await current.text_content()
                source.period.current = current_text.replace('%', '')

                async def foo(xpath_btn: str) -> str:
                    await aave.locator(xpath_btn).click()
                    waited = aave.locator('//*[@id="__next"]/main/div[2]/div/div[2]/div[1]/div/div[4]/div/div/div[2]/div[2]/p')
                    await expect(waited).not_to_be_visible(timeout=aave_expect_timeout)
                    heap_of_shit = aave.get_by_text(re.compile('Avg.'))
                    return (await heap_of_shit.all_text_contents())[1].split(' ')[-1].replace('%', '')

                source.period.month = await foo('//*[@id="__next"]/main/div[2]/div/div[2]/div[1]/div/div[4]/div/div/div[2]/div[1]/div[2]/button[1]/p')
                source.period.month_six = await foo('//*[@id="__next"]/main/div[2]/div/div[2]/div[1]/div/div[4]/div/div/div[2]/div[1]/div[2]/button[2]/p')
                source.period.year = await foo('//*[@id="__next"]/main/div[2]/div/div[2]/div[1]/div/div[4]/div/div/div[2]/div[1]/div[2]/button[3]/p')

                source.period.day = '~'
                source.period.week = '~'
                source.period.month_three = '~'
                source.period.all_time = '~'

                result_search.append(source)
    except TimeoutError as e:
        sp.write(f'💥 Fail - Coroutine timeout - {source.lending} | {source.chain} | {source.name} | {source.url}, error: {e}')
    except Exception as e:
        sp.write(f'💥 Fail - {source.lending} | {source.chain} | {source.name} | {source.url}, error: {e}')


async def morpho_fill_source_sm(source: Source, proxy: ProxySettings, sp: Yaspin, semaphore: Semaphore, result_sources: list[Source]):
    async with semaphore:
        await morpho_fill_source(source, proxy, sp, result_sources)


async def morpho_fill_source(source: Source, proxy: ProxySettings, sp: Yaspin, result_sources: list[Source]):
    await asyncio.sleep(morpho_request_delay)

    try:
        async with asyncio.timeout(morpho_timeout):
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    args=['--disable-blink-features=AutomationControlled'],
                    proxy=proxy,
                    headless=headless,
                )
                browser = await browser.new_context(user_agent=FakeUserAgent().chrome)

                morpho = await browser.new_page()
                await morpho.goto(source.url)
                await morpho.wait_for_load_state('networkidle')

                # popup to close if exists
                btn_to_close = morpho.locator('//*[@id="radix-:r0:"]/button')
                if await btn_to_close.is_visible():
                    await btn_to_close.click()

                current = morpho.locator(
                    '//*[@id="section-layout"]/div/div[1]/div[2]/div[3]/div/span')
                await expect(current).to_be_visible(timeout=morpho_expect_timeout)
                current_text = await current.text_content()
                source.period.current = current_text.replace('%', '')

                async def foo(position: Pair) -> str:
                    history_period_btn = morpho.locator(
                        '//*[@id="section-layout"]/div/div[2]/div/div[1]/div/div[3]/div[1]/div[1]/button')

                    await expect(history_period_btn).to_be_visible(timeout=morpho_expect_timeout)
                    await history_period_btn.click()

                    await asyncio.sleep(morpho_search_delay)  # search by coordinates, dont remove
                    await morpho.mouse.click(x=position.x, y=position.y)
                    await asyncio.sleep(morpho_search_delay)  # search by coordinates, dont remove

                    avg_value = morpho.locator(
                        '//html/body/main/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div/div[3]/div[1]/div[2]/div/div/span/div')
                    await expect(avg_value).to_be_visible(timeout=morpho_expect_timeout)
                    avg_value_text = await avg_value.text_content()

                    return avg_value_text.strip().split(' ')[-1].replace('%', '')

                source.period.week = await foo(MorphoCheckboxCoordinates.week)
                source.period.month = await foo(MorphoCheckboxCoordinates.month)
                source.period.month_three = await foo(MorphoCheckboxCoordinates.month_three)
                source.period.all_time = await foo(MorphoCheckboxCoordinates.all_time)

                source.period.day = '~'
                source.period.month_six = '~'
                source.period.year = '~'

                result_sources.append(source)
    except TimeoutError as e:
        sp.write(f'💥 Fail - Coroutine timeout - {source.lending} | {source.chain} | {source.name} | {source.url}, error: {e}')
    except Exception as e:
        sp.write(f'💥 Fail - {source.lending} | {source.chain} | {source.name} | {source.url}, error: {e}')


async def fluid_fill_source_sm(source: Source, proxy: ProxySettings, sp: Yaspin, semaphore: Semaphore, result_search: list[Source]):
    async with semaphore:
        await fluid_fill_source(source, proxy, sp, result_search)


async def fluid_fill_source(source: Source, proxy: ProxySettings, sp: Yaspin, result_search: list[Source]):
    await asyncio.sleep(fluid_request_delay)

    try:
        async with asyncio.timeout(fluid_timeout):
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    args=['--disable-blink-features=AutomationControlled'],
                    proxy=proxy,
                    headless=headless,
                )
                browser = await browser.new_context(user_agent=FakeUserAgent().chrome)

                fluid = await browser.new_page()
                await fluid.goto(source.url)
                await fluid.wait_for_load_state('networkidle')

                id = source.url.split('#')[1]

                details_btn = fluid.locator(f'//*[@id="__nuxt"]/div/div[3]/div[3]/div/div[2]/div[2]/details[{id}]')
                await expect(details_btn).to_be_visible(timeout=fluid_expect_timeout)
                await details_btn.click(position={'x': 901, 'y': 193})  # history_btn position, because dynamic id in xpath

                await asyncio.sleep(fluid_search_delay)  # search by coordinates, dont remove
                await fluid.mouse.click(x=FluidPeriodsBtnCoordinates.day.x, y=FluidPeriodsBtnCoordinates.day.y)  # because dynamic id in xpath
                await asyncio.sleep(fluid_search_delay)  # search by coordinates, dont remove

                chart = fluid.locator(
                    f'//*[@id="__nuxt"]/div/div[3]/div[3]/div/div[2]/div[2]/details[{id}]/div/div[2]/div[1]/div[2]/div[3]/x-vue-echarts/div[1]')
                await expect(chart).to_be_visible(timeout=fluid_expect_timeout)
                await chart.hover(position=Position({'x': 410, 'y': 0}))

                current_value = fluid.locator(
                    f'//*[@id="__nuxt"]/div/div[3]/div[3]/div/div[2]/div[2]/details[{id}]/div/div[2]/div[1]/div[2]/div[3]/x-vue-echarts/div[2]/div/div[1]/span')
                await expect(current_value).to_be_visible(timeout=fluid_expect_timeout)
                current_value_text = await current_value.text_content()
                source.period.current = current_value_text.strip().split(' ')[-1].replace('%', '')

                avg_value = fluid.locator(
                    f'//*[@id="__nuxt"]/div/div[3]/div[3]/div/div[2]/div[2]/details[{id}]/div/div[2]/div[1]/div[2]/div[3]/x-vue-echarts/div[2]/div/div[2]/p[2]')
                await expect(avg_value).to_be_visible(timeout=fluid_expect_timeout)
                avg_value_text = await avg_value.text_content()
                source.period.day = avg_value_text.strip().split(' ')[-1].replace('%', '')

                async def foo(position: Pair, _id: str) -> str:
                    await fluid.mouse.click(x=position.x, y=position.y)
                    await asyncio.sleep(fluid_search_delay)  # search by coordinates, dont remove
                    _chart = fluid.locator(
                        f'//*[@id="__nuxt"]/div/div[3]/div[3]/div/div[2]/div[2]/details[{_id}]/div/div[2]/div[1]/div[2]/div[3]/x-vue-echarts/div[1]')
                    await expect(_chart).to_be_visible(timeout=fluid_expect_timeout)
                    await _chart.hover()

                    _avg_value = fluid.locator(
                        f'//*[@id="__nuxt"]/div/div[3]/div[3]/div/div[2]/div[2]/details[{id}]/div/div[2]/div[1]/div[2]/div[3]/x-vue-echarts/div[2]/div/div[2]/p[2]')
                    await expect(_avg_value).to_be_visible(timeout=fluid_expect_timeout)
                    _avg_value_text = await _avg_value.text_content()
                    return _avg_value_text.strip().split(' ')[-1].replace('%', '')

                source.period.week = await foo(FluidPeriodsBtnCoordinates.week, id)
                source.period.month = await foo(FluidPeriodsBtnCoordinates.month, id)
                source.period.year = await foo(FluidPeriodsBtnCoordinates.year, id)

                source.period.month_three = '~'
                source.period.month_six = '~'
                source.period.all_time = '~'

                result_search.append(source)
    except TimeoutError as e:
        sp.write(f'💥 Fail - Coroutine timeout - {source.lending} | {source.chain} | {source.name} | {source.url}, error: {e}')
    except Exception as e:
        sp.write(f'💥 Fail - {source.lending} | {source.chain} | {source.name} | {source.url}, error: {e}')


async def compound_fill_source_sm(source: Source, proxy: ProxySettings, sp: Yaspin, semaphore: Semaphore, result_search: list[Source]):
    async with semaphore:
        await compound_fill_source(source, proxy, sp, result_search)


async def compound_fill_source(source: Source, proxy: ProxySettings, sp: Yaspin, result_search: list[Source]):
    await asyncio.sleep(compound_request_delay)

    try:
        async with asyncio.timeout(compound_timeout):
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    args=['--disable-blink-features=AutomationControlled'],
                    proxy=proxy,
                    headless=headless,
                )
                browser = await browser.new_context(user_agent=FakeUserAgent().chrome)

                compound = await browser.new_page()
                await compound.goto(source.url)
                await compound.wait_for_load_state('networkidle')

                current_value = compound.locator(
                    '//*[@id="root"]/main/div[2]/div[2]/div/div[1]/div[1]/h4')
                await expect(current_value).to_be_visible()
                current_value_text = await current_value.text_content()
                source.period.current = current_value_text.replace('%', '')

                chart = compound.locator(
                    '//*[@id="root"]/main/section/div[2]/div[2]')
                month_avg: float = 0
                for i in range(0, 30):
                    await chart.hover(position={'x': 8.31 + 16.62 * i, 'y': 150})
                    rate_value = await compound.wait_for_selector(".market-history-panel__hover__value")
                    reta_value_text = await rate_value.text_content()
                    month_avg += float(reta_value_text.strip().split(' ')[-1].replace('%', ''))
                    await asyncio.sleep(0.05)  # dont remove

                source.period.month = f'{month_avg / 30:.2f}'

                source.period.day = '~'
                source.period.week = '~'
                source.period.month_three = '~'
                source.period.month_six = '~'
                source.period.year = '~'
                source.period.all_time = '~'

                result_search.append(source)
    except TimeoutError as e:
        sp.write(f'💥 Fail - Coroutine timeout - {source.lending} | {source.chain} | {source.name} | {source.url}, error: {e}')
    except Exception as e:
        sp.write(f'💥 Fail - {source.lending} | {source.chain} | {source.name} | {source.url}, error: {e}')


async def fill(lending: LendingToSearch, mode: Mode, sp: Yaspin, token: str, coroutines: int) -> list[Source]:
    token = token.lower() if token else ''

    aave_search = []
    for source in Aave:
        aave_search.append(source) if source.name.endswith(token) else None

    morpho_search = []
    for source in Morpho:
        morpho_search.append(source) if source.name.endswith(token) else None

    fluid_search = []
    for source in Fluid:
        fluid_search.append(source) if source.name.endswith(token) else None

    compound_search = []
    for source in Compound:
        compound_search.append(source) if source.name.endswith(token) else None

    result_search = []
    match mode:
        case mode.SYNC:
            match lending:
                case lending.ALL:
                    for source in aave_search:
                        await aave_fill_source(source, await format_proxy(aave_proxy), sp, result_search)
                    for source in morpho_search:
                        await morpho_fill_source(source, await format_proxy(morpho_proxy), sp, result_search)
                    for source in fluid_search:
                        await fluid_fill_source(source, await format_proxy(fluid_proxy), sp, result_search)
                    for source in compound_search:
                        await compound_fill_source(source, await format_proxy(compound_proxy), sp, result_search)
                case lending.AAVE:
                    for source in aave_search:
                        await aave_fill_source(source, await format_proxy(aave_proxy), sp, result_search)
                case lending.FLUID:
                    for source in fluid_search:
                        await fluid_fill_source(source, await format_proxy(fluid_proxy), sp, result_search)
                case lending.COMPOUND:
                    for source in compound_search:
                        await compound_fill_source(source, await format_proxy(compound_proxy), sp, result_search)
                case lending.MORPHO:
                    for source in morpho_search:
                        await morpho_fill_source(source, await format_proxy(morpho_proxy), sp, result_search)
        case mode.ASYNC:
            tasks = []
            semaphore = asyncio.Semaphore(coroutines)
            match lending:
                case lending.ALL:
                    for source in aave_search:
                        tasks.append(asyncio.create_task(aave_fill_source_sm(source, await format_proxy(aave_proxy), sp, semaphore, result_search)))
                    for source in morpho_search:
                        tasks.append(asyncio.create_task(morpho_fill_source_sm(source, await format_proxy(morpho_proxy), sp, semaphore, result_search)))
                    for source in fluid_search:
                        tasks.append(asyncio.create_task(fluid_fill_source_sm(source, await format_proxy(fluid_proxy), sp, semaphore, result_search)))
                    for source in compound_search:
                        tasks.append(asyncio.create_task(compound_fill_source_sm(source, await format_proxy(compound_proxy), sp, semaphore, result_search)))
                case lending.AAVE:
                    for source in aave_search:
                        tasks.append(asyncio.create_task(aave_fill_source_sm(source, await format_proxy(aave_proxy), sp, semaphore, result_search)))
                case lending.FLUID:
                    for source in fluid_search:
                        tasks.append(asyncio.create_task(fluid_fill_source_sm(source, await format_proxy(fluid_proxy), sp, semaphore, result_search)))
                case lending.COMPOUND:
                    for source in compound_search:
                        tasks.append(asyncio.create_task(compound_fill_source_sm(source, await format_proxy(compound_proxy), sp, semaphore, result_search)))
                case lending.MORPHO:
                    for source in morpho_search:
                        tasks.append(asyncio.create_task(morpho_fill_source_sm(source, await format_proxy(morpho_proxy), sp, semaphore, result_search)))

            await asyncio.gather(*tasks)

    return result_search
