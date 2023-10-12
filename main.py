#!.venv/bin/python

from registration_number_scraper import scrape_new_registration_numbers
import typer
from dica_scraper import dica_scraper
from clean_registration_numbers import clean_registration_numbers
import subprocess
from helper_functions import dedupe_succeeded_registration_numbers, dedupe_output_files

app = typer.Typer()


@app.command()
def scrape(
    headless: bool = True,
    max_delay: int = 0,
    timeout: int = 30000,
    browser: str = "chromium",
    proxy: str = "",
    proxy_username: str = "",
    proxy_password: str = "",
) -> None:
    """
    Scrapes Dica companies.
    browsers include chromium by default, firefox and webkit.
    """
    dica_scraper(
        headless, max_delay, timeout, browser, proxy, proxy_username, proxy_password
    )


@app.command()
def clean_input() -> None:
    """
    Removes scraped registration numbers and duplicates.
    """
    clean_registration_numbers()


@app.command()
def scrape_new_registrations(
    headless: bool = True,
    timeout: int = 90000,
    proxy: str = "",
    proxy_username: str = "",
    proxy_password: str = "",
) -> None:
    """
    Scrapes new registration numbers.
    """
    scrape_new_registration_numbers(
        headless, timeout, proxy, proxy_username, proxy_password
    )


@app.command()
def dedupe_output():
    """
    Dedupes output file.
    """
    dedupe_succeeded_registration_numbers()
    dedupe_output_files()


@app.command()
def sync() -> None:
    """
    Syncs to s3.
    """
    subprocess.run(
        [
            "/usr/bin/s3cmd put -r /home/simon/dica-scraper/data/* s3://envisagewebscrapes/dica-new/"
        ],
        shell=True,
    )


if __name__ == "__main__":
    app()
