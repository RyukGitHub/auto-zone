*** Settings ***
Library    Browser
Library    Collections
Library    ${EXECDIR}/resources/TelegramNotifier.py
Library    ${EXECDIR}/resources/Generator.py
Resource   ../resources/keywords.robot
Suite Setup    Setup Site Configuration

*** Variables ***
${SITE_NAME}    nfbusty

*** Test Cases ***
TC01
    Open join page    ${JOIN_URL}
    ${final_email}=    Select 30 day membership and proceed to checkout
    [Teardown]    Send Telegram Notification    ${TEST STATUS}    ${SITE_NAME}    ${final_email}    ${PASSWORD}    ${ACNO}    ${RTNO}

*** Keywords ***
Setup Site Configuration
    Import Resource    ${EXECDIR}/resources/sites/${SITE_NAME}.robot
