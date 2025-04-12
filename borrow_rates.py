import asyncio
import os

import csv
import functools
from datetime import datetime
import click
from rich.console import Console
from rich.table import Table
from yaspin import yaspin
from models import LendingToSearch, Mode
from config import aave_font_color, compound_font_color, morpho_font_color, fluid_font_color
from pw import fill


def make_async(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


@click.command()
@make_async
@click.option('-m', "--multi", type=int,
              help='number of simultaneous requests')
@click.option('-l', "--lending", type=click.Choice(['all', 'aave', 'fluid', 'compound', 'morpho'], case_sensitive=False), default='all', show_default=True,
              help='lending to search token')
@click.option('-t', "--token",
              help='token to search borrow rates')
async def cli(multi: int, lending: str, token: str):
    with yaspin(text='fetching data', timer=True) as sp:
        match lending:
            case 'all':
                _lending = LendingToSearch.ALL
            case 'aave':
                _lending = LendingToSearch.AAVE
            case 'fluid':
                _lending = LendingToSearch.FLUID
            case 'compound':
                _lending = LendingToSearch.COMPOUND
            case 'morpho':
                _lending = LendingToSearch.MORPHO

        mode = Mode.ASYNC if multi else Mode.SYNC

        results = await fill(lending=_lending, mode=mode, token=token, sp=sp, coroutines=multi)
        if not results:
            sp.fail(f'\n💥 Fail - all requests failed |')
            return

        results = sorted(results, key=lambda x: (x.lending, x.chain))

        table = Table(expand=True, title='\n[bold]Borrow rates[bold]')

        table.add_column(header='lending', justify='center', style='cyan', no_wrap=True)
        table.add_column(header='chain', justify='center', style='cyan', no_wrap=True)
        table.add_column(header='token name', justify='center', style='cyan', no_wrap=True)
        table.add_column(header='current', justify='center', style='cyan', no_wrap=True)
        table.add_column(header='day', justify='center', style='cyan', no_wrap=True)
        table.add_column(header='week', justify='center', style='cyan', no_wrap=True)
        table.add_column(header='month', justify='center', style='cyan', no_wrap=True)
        table.add_column(header='3 month', justify='center', style='cyan', no_wrap=True)
        table.add_column(header='6 month', justify='center', style='cyan', no_wrap=True)
        table.add_column(header='year', justify='center', style='cyan', no_wrap=True)
        table.add_column(header='all time', justify='center', style='cyan', no_wrap=True)

        for result in results:
            match result.lending:
                case 'aave':
                    style = aave_font_color
                case 'compound':
                    style = compound_font_color
                case 'fluid':
                    style = fluid_font_color
                case 'morpho':
                    style = morpho_font_color

            table.add_row(
                result.lending,
                result.chain,
                result.name,
                result.period.current,
                result.period.day,
                result.period.week,
                result.period.month,
                result.period.month_three,
                result.period.month_six,
                result.period.year,
                result.period.all_time,
                style=style,
            )

        console = Console()
        console.print(table)

        if not os.path.exists('csv'):
            os.makedirs('csv')

        if not token:
            token = 'all'

        with open(f'csv/{lending} - {token} - {datetime.now().strftime("%H:%M:%S %d-%m-%Y")}.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=';')
            csv_writer.writerow(['lending', 'chain', 'token name', 'url', 'current', 'day', 'week', 'month', '3 month', '6 month', 'year', 'all time'])
            for result in results:
                csv_writer.writerow(
                    [
                        f'{result.lending}',
                        f'{result.chain}',
                        f'{result.name}',
                        f'{result.url}',
                        f'{result.period.current}',
                        f'{result.period.day}',
                        f'{result.period.week}',
                        f'{result.period.month}',
                        f'{result.period.month_three}',
                        f'{result.period.month_six}',
                        f'{result.period.year}',
                        f'{result.period.all_time}',
                    ]
                )

        sp.ok('\nDone |')


if __name__ == '__main__':
    cli()
