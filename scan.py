#!/usr/bin/env python
# Scans for available USCIS appointment
import argparse
from splinter import Browser
import time

def parse_opts():
    uscis_url = "https://my.uscis.gov/en/appointment/new?appointment%5Binternational%5D=false"
    parser = argparse.ArgumentParser(description=
            'Scans USCIS website for available appointment at the local field office.')
    parser.add_argument('zipcode', help='The zipcode to look for closest field office')
    parser.add_argument('office', help='Name of the local field office you prefer')
    parser.add_argument('--phone', help='Sends a text to this phone number should an appointment slot be available')
    parser.add_argument('--url', help='USCIS appointment address (inside US only)',
            default=uscis_url)
    return parser.parse_args()

def get_earliest_date(browser):
    """ Returns a string representing the earliest available date for appointments,
                None if no appointments are available.
    """
    time_texts = browser.find_by_css('span#time-text')
    if len(time_texts) > 0:
        return time_texts.first.value
    return None

def notify(phone, earliest_date):
    print "Earliest date is {}".format(earliest_date)

def navigate_available_appointments(browser, url, zipcode, office):
    """ Raises ValueError if the specified zipcode-office name combo does not work """
    # Visit URL
    browser.visit(url)
    browser.fill('appointments_appointment[zip]', zipcode)
    # Find and click the 'search' button
    button = browser.find_by_id('field_office_query')
    # Interact with elements
    button.click()
    found_office = None
    for office_div in browser.find_by_css(".field-office-name"):
        if office.lower() in office_div.html.lower():
            found_office = office_div
            break
    if not found_office:
       raise ValueError("Unable to locate office '{}'".format(office))

    found_office.click()
    # decline to fill survey form
    nothanks = browser.find_by_css('.fsrDeclineButton')
    while True:
        try:
            nothanks.click()
            break
        except Exception, e:
            print "Retrying canceling popup.."
            time.sleep(2)

    buttons = browser.find_by_css('form input[type=submit]')
    for index, button in enumerate(buttons):
        print index, button.html, button.visible
        if button.visible:
            button.click()
            break

def main():
    args = parse_opts()
    error = None
    with Browser() as browser:
        try:
            navigate_available_appointments(browser, args.url, args.zipcode, args.office)
        except ValueError as e:
            print "Error: {}".format(e)
            exit(4)

        time.sleep(3)
        earliest_date = get_earliest_date(browser)
        if earliest_date:
            notify(args.phone, earliest_date)
        else:
            print "No appointment slots available."

if __name__ == "__main__":
    main()
