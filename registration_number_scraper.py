from playwright.sync_api import sync_playwright
from csv import DictWriter
import pathlib
from clean_registration_numbers import clean_registration_numbers
from console import console
from string import ascii_lowercase


def scrape_new_registration_numbers(
    headless, timeout=90000, proxy="", proxy_username="", proxy_password=""
):
    with sync_playwright() as p:
        # checks if folders exist
        d = pathlib.Path("data/output")
        d.mkdir(parents=True, exist_ok=True)

        registration_numbers = set()

        browser_context = {
            "user_data_dir": "",
            "headless": headless,
        }

        if proxy:
            browser_context["proxy"] = {
                "server": proxy,
                "username": proxy_username,
                "password": proxy_password,
            }

        # selects and opens browser
        browser = p.chromium.launch_persistent_context(**browser_context)
        page = browser.new_page()

        # goes to dica search page
        page.goto(
            "https://www.myco.dica.gov.mm/corp/search.aspx",
            wait_until="domcontentloaded",
            timeout=timeout,
        )
        console.log("Browser opened.\n", style="debug")

        console.log(
            f"Configuring search results to newest.\n",
            style="keyword",
        )

        # inputs character number into search bar
        page.fill(
            '//*[@id="app"]/div/div/div[1]/div/div[1]/div/div[2]/input',
            f"*a*",
        )

        # presses enter on the search button
        page.keyboard.press("Enter")

        # clicks on text which does nothing except wait for the text to be visible
        page.click(
            '//*[@id="app"]/div/div/div[2]/div[3]/div[1]/div[2]/div/div[1]/div[1]/div',
            timeout=timeout,
        )

        # clicks on registration date
        page.click(
            '//*[@id="app"]/div/div/div[2]/div[2]/fieldset/span/span[4]/button/span/span',
            timeout=timeout,
        )

        # clicks on text which does nothing except wait for the text to be visible
        page.click(
            '//*[@id="app"]/div/div/div[2]/div[3]/div[1]/div[2]/div/div[1]/div[1]/div',
            timeout=timeout,
        )

        # clicks on registration date
        page.click(
            '//*[@id="app"]/div/div/div[2]/div[2]/fieldset/span/span[4]/button/span/span',
            timeout=timeout,
        )

        # clicks on text which does nothing except wait for the text to be visible
        page.click(
            '//*[@id="app"]/div/div/div[2]/div[3]/div[1]/div[2]/div/div[1]/div[1]/div',
            timeout=timeout,
        )

        # clicks on per page dropdown
        page.click('//*[@id="app"]/div/div/div[1]/div/div[2]/div/div/select')

        # presses arrow down on keyboard
        page.keyboard.press("ArrowDown")

        # presses arrow down on keyboard
        page.keyboard.press("ArrowDown")

        # presses enter on the search button
        page.keyboard.press("Enter")

        # clicks on text which does nothing except wait for the text to be visible
        page.click(
            '//*[@id="app"]/div/div/div[2]/div[3]/div[1]/div[2]/div/div[1]/div[1]/div',
            timeout=timeout,
        )

        for character in ascii_lowercase:
            try:
                console.log(
                    f"Scraping new registration numbers using letter: {character}\n",
                    style="info",
                )

                # clicks on search bar
                page.click('//*[@id="app"]/div/div/div[1]/div/div[1]/div/div[2]/input')

                # inputs character number into search bar
                page.fill(
                    '//*[@id="app"]/div/div/div[1]/div/div[1]/div/div[2]/input',
                    f"*{character}*",
                )

                # presses enter on the search button
                page.keyboard.press("Enter")

                # clicks on text which does nothing except wait for the text to be visible
                page.click(
                    '//*[@id="app"]/div/div/div[2]/div[3]/div[1]/div[2]/div/div[1]/div[1]/div',
                    timeout=timeout,
                )
                for company in range(1, 51):
                    registration_numbers.add(
                        page.query_selector(
                            f'//*[@id="app"]/div/div/div[2]/div[3]/div[1]/div[2]/div/div[{company}]/div[1]/a'
                        )
                        .inner_text()
                        .split(" ")[-1]
                    )
            except Exception as error:
                console.log(
                    f"Failed to scape new registration number: {character}\n",
                    style="error",
                )
                console.log(error, style="error")
        for registration_number in registration_numbers:
            field_names = ["registration_number"]
            with open(
                f"data/dica_registration_numbers.csv",
                "a",
                newline="",
                encoding="utf-8",
            ) as f_object:
                dictwriter_object = DictWriter(f_object, fieldnames=field_names)
                dictwriter_object.writerow({"registration_number": registration_number})
            f_object.close()
        console.log(
            f"Successfully scraped numbers writen to dica registration numbers.\n",
            style="debug",
        )
        browser.close()
        clean_registration_numbers()


if __name__ == "__main__":
    scrape_new_registration_numbers()
