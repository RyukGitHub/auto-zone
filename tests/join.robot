*** Settings ***
Library    Browser
Library    Collections
Library    ${EXECDIR}/resources/DiscordNotifier.py
Library    ${EXECDIR}/resources/Generator.py
Resource   ../resources/keywords.robot
Suite Setup    Setup Site Configuration

*** Variables ***
${SITE_NAME}    thepovgod

*** Test Cases ***
TC01
    Open join page    ${JOIN_URL}
    ${final_email}=    Select 30 day membership and proceed to checkout
    [Teardown]    Send Discord Notification    ${TEST STATUS}    ${SITE_NAME}    ${final_email}    ${PASSWORD}    ${ACNO}    ${RTNO}    ${BANK_NAME}    ${BANK_CITY}    ${BANK_ZIP}

*** Keywords ***
Setup Site Configuration
    Import Resource    ${EXECDIR}/resources/sites/${SITE_NAME}.robot
