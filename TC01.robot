*** Settings ***
Library    Browser
Resource   resources/keywords.robot
Suite Setup    Setup Site Configuration

*** Variables ***
${SITE_NAME}    nfbusty

*** Test Cases ***
TC01
    Open join page    ${JOIN_URL}
    Close modal and select 30 day membership

*** Keywords ***
Setup Site Configuration
    Import Resource    ${EXECDIR}/resources/sites/${SITE_NAME}.robot
