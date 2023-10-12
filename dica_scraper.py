from ast import arguments
from audioop import add
from playwright.sync_api import sync_playwright
from csv import DictReader, DictWriter
from rich import inspect
from helper_functions import file_exists_checker
import pathlib
from clean_registration_numbers import clean_registration_numbers
from console import console
import time
import random


def dica_scraper(
    headless=True,
    max_delay=0,
    timeout=30000,
    browser="chromium",
    proxy="",
    proxy_username="",
    proxy_password="",
):
    with sync_playwright() as p:

        # checks if folders exist
        d = pathlib.Path("data/output")
        d.mkdir(parents=True, exist_ok=True)

        # all created file names and fieldname variables
        company_details_name = "companies"
        company_details_fieldnames = [
            "company_name_english",
            "company_name_myanmar",
            "registration_number",
            "registration_date",
            "company_type",
            "status",
            "foreign_company",
            "small_company",
            "annual_return_due_date",
            "principal_activity",
            "registration_number_in_jurisdiction_of_corporation",
            "jurisdiction_of_incorporation",
            "financial_statement_due_date",
            "url",
        ]
        officers_file_name = "officers"
        officers_fieldnames = [
            "registration_number",
            "name",
            "type",
            "nationality",
            "n.r.c._for_myanmar_citizens",
            "company_name_english",
            "company_name_myanmar",
            "registration_date",
            "company_type",
            "status",
            "foreign_company",
            "small_company",
            "annual_return_due_date",
            "registration_number_in_jurisdiction_of_corporation",
            "jurisdiction_of_incorporation",
            "financial_statement_due_date",
            "url",
        ]

        addresses_file_name = "addresses"
        addresses_fieldnames = [
            "registration_number",
            "type",
            "address",
            "effective_date",
        ]

        filing_history_name = "filing_history"
        filing_history_fieldnames = [
            "registration_number",
            "document_no.",
            "form_filing_type",
            "filing_date",
            "effective_date",
        ]

        succeeded_registration_numbers_name = "succeeded_registration_numbers"
        succeeded_registration_numbers_fieldname = ["registration_number"]
        failed_registration_numbers_name = "failed_registration_numbers"
        failed_registration_numbers_fieldname = ["registration_number"]

        data_path = "data/"
        output_path = "data/output/"

        # checks if files exist and creates them if they done exist
        file_exists_checker(output_path, officers_file_name, officers_fieldnames)
        file_exists_checker(output_path, addresses_file_name, addresses_fieldnames)
        file_exists_checker(output_path, filing_history_name, filing_history_fieldnames)
        file_exists_checker(
            output_path, company_details_name, company_details_fieldnames
        )
        file_exists_checker(
            data_path,
            succeeded_registration_numbers_name,
            succeeded_registration_numbers_fieldname,
        )
        file_exists_checker(
            data_path,
            failed_registration_numbers_name,
            failed_registration_numbers_fieldname,
        )
        # cleaning input
        console.log("Cleaning input file.\n", style="info")
        clean_registration_numbers()

        # reads registration numbers
        file_handle = open("data/dica_registration_numbers.csv", "r")
        csv_reader = DictReader(file_handle)

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
        if browser == "chromium":
            # selects and opens browser
            dica = p.chromium.launch_persistent_context(**browser_context)
            page = dica.new_page()
        elif browser == "firefox":
            # selects and opens browser
            dica = p.firefox.launch_persistent_context(**browser_context)
            page = dica.new_page()
        else:
            # selects and opens browser
            dica = p.webkit.launch_persistent_context(**browser_context)
            page = dica.new_page()

        for row in csv_reader:
            try:
                console.log(
                    f'Scraping registration number: {row["registration_number"].strip()}',
                    style="info",
                )
                # goes to dica link
                page.goto(
                    "https://www.myco.dica.gov.mm/corp/search.aspx",
                    wait_until="domcontentloaded",
                    timeout=timeout,
                )

                # clicks on search bar
                page.click(
                    '//*[@id="app"]/div/div/div[1]/div/div[1]/div/div[2]/input',
                    timeout=timeout,
                )

                # types reg number into search bar
                page.fill(
                    '//*[@id="app"]/div/div/div[1]/div/div[1]/div/div[2]/input',
                    row["registration_number"].strip(),
                    timeout=timeout,
                )

                # presses the search button
                page.keyboard.press("Enter")

                # clicks on the resulting title which indirectly navigates the browser to the company details page
                page.click(
                    '//*[@id="app"]/div/div/div[2]/div/div[1]/div[2]/div/div/div[1]/a',
                    timeout=timeout,
                )

                # waits for elements in details page to load before proceeding
                page.locator(
                    '//*[@id="EntityCtrl"]/div[2]/div[6]/div[1]/div[1]/div[1]/label'
                ).click(timeout=timeout)

                # scrapes and stores all company details
                company_row = {}
                corporation_row = {}
                officer_row = {}
                address_row = {}
                filing_history_row = {}

                url = page.url
                if (
                    page.query_selector(
                        '//*[@id="EntityCtrl"]/div[2]/div[6]/div[1]/div[1]/div[1]/label'
                    ).inner_text()
                    == "Company Name (English)"
                ):
                    company_name_english = page.query_selector(
                        '//*[@id="txtCompanyName"]'
                    )
                    company_row[
                        "company_name_english"
                    ] = company_name_english.inner_text().strip()
                    officer_row[
                        "company_name_english"
                    ] = company_name_english.inner_text().strip()

                    company_name_myanmar = page.query_selector(
                        '//*[@id="txtFictitiousName"]'
                    )
                    company_row[
                        "company_name_myanmar"
                    ] = company_name_myanmar.inner_text().strip()
                    officer_row[
                        "company_name_myanmar"
                    ] = company_name_myanmar.inner_text().strip()

                    registration_number = page.query_selector(
                        '//*[@id="txtRegistrationNumber"]'
                    )
                    company_row[
                        "registration_number"
                    ] = registration_number.inner_text().strip()
                    officer_row[
                        "registration_number"
                    ] = registration_number.inner_text().strip()

                    registration_date = page.query_selector(
                        '//*[@id="txtRegistrationDate"]'
                    )
                    company_row[
                        "registration_date"
                    ] = registration_date.inner_text().strip()
                    officer_row[
                        "registration_date"
                    ] = registration_date.inner_text().strip()

                    company_type = page.query_selector('//*[@id="txtCompanyType"]')
                    company_row["company_type"] = company_type.inner_text().strip()
                    officer_row["company_type"] = company_type.inner_text().strip()

                    status = page.query_selector('//*[@id="txtCompanyStatus"]')
                    company_row["status"] = status.inner_text().strip()
                    officer_row["status"] = status.inner_text().strip()

                    foreign_company = page.query_selector(
                        '//*[@id="ctl00_cphBody_ForeignCompany"]/span'
                    )
                    company_row[
                        "foreign_company"
                    ] = foreign_company.inner_text().strip()
                    officer_row[
                        "foreign_company"
                    ] = foreign_company.inner_text().strip()

                    small_company = page.query_selector(
                        '//*[@id="ctl00_cphBody_SmallCompany"]/span'
                    )
                    company_row["small_company"] = small_company.inner_text().strip()
                    officer_row["small_company"] = small_company.inner_text().strip()

                    company_row["url"] = url

                    if page.is_visible(
                        '//*[@id="EntityCtrl"]/div[2]/div[6]/div[1]/div[3]/div/label'
                    ):
                        annual_return_due_date = page.query_selector(
                            '//*[@id="txtAnnualReturnDueDate"]'
                        )
                        company_row[
                            "annual_return_due_date"
                        ] = annual_return_due_date.inner_text().strip()
                        officer_row[
                            "annual_return_due_date"
                        ] = annual_return_due_date.inner_text().strip()

                        # scrape principal activity
                        number_of_rows = 1
                        principal_activity_data = []
                        while True:
                            if (
                                page.is_visible(
                                    f'//*[@id="ctl00_cphBody_PrincipalActivity"]/div[{number_of_rows}]'
                                )
                                == True
                            ):
                                principal_activity_data.append(
                                    page.query_selector(
                                        f'//*[@id="ctl00_cphBody_PrincipalActivity"]/div[{number_of_rows}]'
                                    ).inner_text()
                                )
                                number_of_rows = number_of_rows + 1
                            else:
                                break

                        # converty principal activity to string
                        principal_activity_string = ""
                        for elements in principal_activity_data:
                            principal_activity_string = (
                                principal_activity_string + str(elements) + "|"
                            )
                        company_row["principal_activity"] = principal_activity_string

                    # writes to companies
                    page.click('//*[@id="CompanyProfileTabFilingHistory"]')
                    with open(
                        f"{output_path}{company_details_name}.csv",
                        "a",
                        newline="",
                        encoding="utf-8",
                    ) as f_object:
                        dictwriter_object = DictWriter(
                            f_object, fieldnames=company_details_fieldnames
                        )
                        dictwriter_object.writerow(company_row)
                else:
                    # names
                    name_of_corporation = page.query_selector(
                        '//*[@id="txtOverseasName"]'
                    )
                    corporation_row[
                        "company_name_english"
                    ] = name_of_corporation.inner_text().strip()
                    officer_row[
                        "company_name_english"
                    ] = name_of_corporation.inner_text().strip()

                    # corporation registration number
                    registration_number_in_jurisdiction_of_corporation = (
                        page.query_selector(
                            '//*[@id="txtOverseasRegNumberInJurisdiction"]'
                        )
                    )
                    corporation_row[
                        "registration_number_in_jurisdiction_of_corporation"
                    ] = (
                        registration_number_in_jurisdiction_of_corporation.inner_text().strip()
                    )
                    officer_row[
                        "registration_number_in_jurisdiction_of_corporation"
                    ] = (
                        registration_number_in_jurisdiction_of_corporation.inner_text().strip()
                    )

                    # jurisdiction
                    jurisdiction_of_incorporation = page.query_selector(
                        '//*[@id="txtOverseasJurisdiction"]'
                    )
                    corporation_row[
                        "jurisdiction_of_incorporation"
                    ] = jurisdiction_of_incorporation.inner_text().strip()
                    officer_row[
                        "jurisdiction_of_incorporation"
                    ] = jurisdiction_of_incorporation.inner_text().strip()

                    # type of company
                    company_type = page.query_selector(
                        '//*[@id="txtOverseasCompanyType"]'
                    )
                    corporation_row["company_type"] = company_type.inner_text().strip()
                    officer_row["company_type"] = company_type.inner_text().strip()

                    # company status
                    status = page.query_selector('//*[@id="txtOverseasCompanyStatus"]')
                    corporation_row["status"] = status.inner_text().strip()
                    officer_row["status"] = status.inner_text().strip()

                    # company registration number
                    registration_number = page.query_selector(
                        '//*[@id="txtOverseasRegistrationNumber"]'
                    )
                    corporation_row[
                        "registration_number"
                    ] = registration_number.inner_text().strip()
                    officer_row[
                        "registration_number"
                    ] = registration_number.inner_text().strip()

                    # company date of registration
                    registration_date = page.query_selector(
                        '//*[@id="txtOverseasRegistrationDate"]'
                    )
                    corporation_row[
                        "registration_date"
                    ] = registration_date.inner_text().strip()
                    officer_row[
                        "registration_date"
                    ] = registration_date.inner_text().strip()

                    # annual return due date
                    annual_return_due_date = page.query_selector(
                        '//*[@id="txtOverseasAnnualReturnDueDate"]'
                    )
                    corporation_row[
                        "annual_return_due_date"
                    ] = annual_return_due_date.inner_text().strip()
                    officer_row[
                        "annual_return_due_date"
                    ] = annual_return_due_date.inner_text().strip()

                    # financial statement due date
                    financial_statement_due_date = page.query_selector(
                        '//*[@id="txtOverseasFinancialStatementDueDate"]'
                    )
                    corporation_row[
                        "financial_statement_due_date"
                    ] = financial_statement_due_date.inner_text().strip()
                    officer_row[
                        "financial_statement_due_date"
                    ] = financial_statement_due_date.inner_text().strip()

                    # url
                    corporation_row["url"] = url
                    officer_row["url"] = url

                    # writes to companies
                    page.click('//*[@id="CompanyProfileTabFilingHistory"]')
                    with open(
                        f"{output_path}{company_details_name}.csv",
                        "a",
                        newline="",
                        encoding="utf-8",
                    ) as f_object:
                        dictwriter_object = DictWriter(
                            f_object, fieldnames=company_details_fieldnames
                        )
                        dictwriter_object.writerow(corporation_row)

                # Scrape officers
                page.click('//*[@id="CompanyProfileTabDirectors"]')
                number_of_rows = 1
                while True:
                    if (
                        page.is_visible(
                            f'//*[@id="tabCompanyProfileTabDirectors"]/div/div/table/tbody/tr[{number_of_rows}]'
                        )
                        == True
                    ):
                        name = page.query_selector(
                            f'//*[@id="tabCompanyProfileTabDirectors"]/div/div/table/tbody/tr[{number_of_rows}]/td[1]'
                        )
                        officer_row["name"] = name.inner_text().strip()

                        type = page.query_selector(
                            f'//*[@id="tabCompanyProfileTabDirectors"]/div/div/table/tbody/tr[{number_of_rows}]/td[2]'
                        )
                        officer_row["type"] = type.inner_text().strip()

                        nationality = page.query_selector(
                            f'//*[@id="tabCompanyProfileTabDirectors"]/div/div/table/tbody/tr[{number_of_rows}]/td[3]'
                        )
                        officer_row["nationality"] = nationality.inner_text().strip()

                        n_r_c_for_myanmar_citizens = page.query_selector(
                            f'//*[@id="tabCompanyProfileTabDirectors"]/div/div/table/tbody/tr[{number_of_rows}]/td[4]'
                        )
                        officer_row[
                            "n.r.c._for_myanmar_citizens"
                        ] = n_r_c_for_myanmar_citizens.inner_text().strip()

                        if (
                            page.query_selector(
                                '//*[@id="EntityCtrl"]/div[2]/div[6]/div[1]/div[1]/div[1]/label'
                            ).inner_text()
                            == "Company Name (English)"
                        ):
                            if number_of_rows == 1:
                                del company_row["principal_activity"]
                            # writes to officers file
                            company_officers_row = officer_row | company_row

                            with open(
                                f"{output_path}{officers_file_name}.csv",
                                "a",
                                newline="",
                                encoding="utf-8",
                            ) as f_object:
                                dictwriter_object = DictWriter(
                                    f_object, fieldnames=officers_fieldnames
                                )
                                dictwriter_object.writerow(company_officers_row)
                        else:
                            # writes to officers file
                            corporation_officers_row = officer_row | corporation_row

                            with open(
                                f"{output_path}{officers_file_name}.csv",
                                "a",
                                newline="",
                                encoding="utf-8",
                            ) as f_object:
                                dictwriter_object = DictWriter(
                                    f_object, fieldnames=officers_fieldnames
                                )
                                dictwriter_object.writerow(corporation_officers_row)
                            f_object.close()
                        number_of_rows = number_of_rows + 1
                    else:
                        break

                # Scrape addresses
                page.click('//*[@id="CompanyProfileTabDetails"]')
                number_of_rows = 1
                while True:
                    if (
                        page.is_visible(
                            f'//*[@id="tabCompanyProfileTabDetails"]/div/table/tbody/tr[{number_of_rows}]'
                        )
                        == True
                    ):
                        type = page.query_selector(
                            f'//*[@id="tabCompanyProfileTabDetails"]/div/table/tbody/tr[{number_of_rows}]/td[1]'
                        )
                        address_row["type"] = type.inner_text().strip()

                        address = page.query_selector(
                            f"//*[@id='tabCompanyProfileTabDetails']/div/table/tbody/tr[{number_of_rows}]/td[2]/div"
                        )
                        address_row["address"] = address.inner_html().strip()

                        effective_date = page.query_selector(
                            f'//*[@id="tabCompanyProfileTabDetails"]/div/table/tbody/tr[{number_of_rows}]/td[3]'
                        )
                        address_row[
                            "effective_date"
                        ] = effective_date.inner_text().strip()

                        address_row["registration_number"] = row[
                            "registration_number"
                        ].strip()

                        # writes to addresses
                        with open(
                            f"{output_path}{addresses_file_name}.csv",
                            "a",
                            newline="",
                            encoding="utf-8",
                        ) as f_object:
                            dictwriter_object = DictWriter(
                                f_object, fieldnames=addresses_fieldnames
                            )
                            dictwriter_object.writerow(address_row)
                            f_object.close()
                        number_of_rows = number_of_rows + 1
                    else:
                        break

                # Scrape Filing history
                page.click('//*[@id="CompanyProfileTabFilingHistory"]')
                number_of_rows = 1
                while True:
                    if (
                        page.is_visible(
                            f'//*[@id="tabCompanyProfileTabFilingHistory"]/div/div[2]/table/tbody/tr[{number_of_rows}]'
                        )
                        == True
                    ):
                        document_no = page.query_selector(
                            f'//*[@id="tabCompanyProfileTabFilingHistory"]/div/div[2]/table/tbody/tr[{number_of_rows}]/td[1]'
                        )
                        filing_history_row[
                            "document_no."
                        ] = document_no.inner_text().strip()

                        form_filing_type = page.query_selector(
                            f'//*[@id="tabCompanyProfileTabFilingHistory"]/div/div[2]/table/tbody/tr[{number_of_rows}]/td[2]'
                        )
                        filing_history_row[
                            "form_filing_type"
                        ] = form_filing_type.inner_text().strip()

                        filing_date = page.query_selector(
                            f'//*[@id="tabCompanyProfileTabFilingHistory"]/div/div[2]/table/tbody/tr[{number_of_rows}]/td[3]'
                        )
                        filing_history_row[
                            "filing_date"
                        ] = filing_date.inner_text().strip()

                        effective_date = page.query_selector(
                            f'//*[@id="tabCompanyProfileTabFilingHistory"]/div/div[2]/table/tbody/tr[{number_of_rows}]/td[4]'
                        )
                        filing_history_row[
                            "effective_date"
                        ] = effective_date.inner_text().strip()

                        filing_history_row["registration_number"] = row[
                            "registration_number"
                        ].strip()

                        # writes to filing history
                        with open(
                            f"{output_path}{filing_history_name}.csv",
                            "a",
                            newline="",
                            encoding="utf-8",
                        ) as f_object:
                            dictwriter_object = DictWriter(
                                f_object, fieldnames=filing_history_fieldnames
                            )
                            dictwriter_object.writerow(filing_history_row)
                            f_object.close()
                        number_of_rows = number_of_rows + 1
                    else:
                        break

                # if scrape is successful then the registration number is saved in registation_number
                with open(
                    f"{data_path}{succeeded_registration_numbers_name}.csv",
                    "a",
                    newline="",
                    encoding="utf-8",
                ) as f_object:
                    dictwriter_object = DictWriter(
                        f_object,
                        fieldnames=succeeded_registration_numbers_fieldname,
                    )
                    dictwriter_object.writerow(
                        {"registration_number": row["registration_number"].strip()}
                    )
                console.log(
                    f'Successfully scraped registration number: {row["registration_number"].strip()}\n',
                    style="debug",
                )
            except Exception as error:

                # catches errors and writes failed registration number to failed_registration_numbers
                with open(
                    f"{data_path}{failed_registration_numbers_name}.csv",
                    "a",
                    newline="",
                    encoding="utf-8",
                ) as f_object:
                    dictwriter_object = DictWriter(
                        f_object, fieldnames=failed_registration_numbers_fieldname
                    )
                    dictwriter_object.writerow(
                        {"registration_number": row["registration_number"].strip()}
                    )
                console.log(
                    f"Failed to scrape registration number: {row['registration_number'].strip()}\n",
                    style="error",
                )
                console.log(error, style="error")
            if max_delay > 0:
                delay = random.randrange(0, max_delay)
                console.log(
                    f"Waiting for {delay} seconds before scraping next company.",
                    style="info",
                )
                time.sleep(delay)
        dica.close()
        console.log("Cleaning input file.\n", style="info")
        clean_registration_numbers()


if __name__ == "__main__":
    dica_scraper()
