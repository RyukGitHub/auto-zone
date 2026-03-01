*** Settings ***
Library    Browser
Library    Collections
Library    ${EXECDIR}/libraries/TelegramNotifier.py
Library    ${EXECDIR}/libraries/Generator.py
Resource   ../resources/keywords.robot
Suite Setup    Setup Site Configuration

*** Variables ***
${SITE_NAME}    nfbusty
${FINAL_EMAIL}  ${EMPTY}

*** Test Cases ***
TC01
    Open join page    ${JOIN_URL}
    ${email}=    Select 30 day membership and proceed to checkout
    Set Suite Variable    ${FINAL_EMAIL}    ${email}
    [Teardown]    Send Telegram Notification    ${TEST STATUS}    ${SITE_NAME}    ${FINAL_EMAIL}    ${PASSWORD}    ${ACNO}    ${RTNO}

*** Keywords ***
Setup Site Configuration
    Import Resource    ${EXECDIR}/resources/sites/${SITE_NAME}.robot
