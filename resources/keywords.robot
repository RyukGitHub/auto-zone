*** Settings ***
Library    Browser
Library    DateTime

*** Variables ***
${EMAIL}       ${EMPTY}
${PASSWORD}    ruby1234
${ACNO}        903219417861450
${RTNO}        063201875

*** Keywords ***
Close consent modal if present
    ${btn}=    Set Variable    css=div.modal-dialog button[data-bs-dismiss="modal"]:has-text("I agree")
    ${count}=  Get Element Count    ${btn}
    IF    ${count} > 0
        Wait For Elements State    ${btn}    visible    timeout=5s
        Click    ${btn}
    END

Close content modal if present
    [Documentation]    Backwards-compatible alias.
    Close consent modal if present

Open join page
    [Arguments]    ${url}=https://nfbusty.com/join?cascid=132
    New Page    ${url}

Select 30 day membership option
    [Documentation]    Select the "30 Day Membership" plan after the modal is closed.
    ${option}=    Set Variable    css=label.join-option:has-text("30 Day Membership")
    Wait For Elements State    ${option}    visible    timeout=10s
    Click    ${option}

Close modal and select 30 day membership
    [Documentation]    Close the modal if shown, then select the 30 day plan.
    Close consent modal if present
    Select 30 day membership option

Enter email and password and proceed to checkout
    [Documentation]    If the username prompt modal appears, fill email/password, click Proceed to Checkout, and log the email.
    [Arguments]    ${password}=${PASSWORD}    ${email}=${EMAIL}    ${acno}=${ACNO}    ${rtno}=${RTNO}
    ${emailCount}=    Get Element Count    css=#UsernamePromptEmail
    IF    ${emailCount} > 0
        Wait For Elements State    css=#UsernamePromptEmail    visible    timeout=15s
        Wait For Elements State    css=#UsernamePromptPassword    visible    timeout=15s
        IF    '${email}' == '${EMPTY}'
            ${epoch}=    Get Time    epoch
            ${email}=    Set Variable    test${epoch}@yopmail.com
        END
        Fill Text    css=#UsernamePromptEmail       ${email}
        Fill Text    css=#UsernamePromptPassword    ${password}
        Log To Console    Email used: ${email}
        Wait For Elements State    css=button#Checkout    visible    timeout=15s
        Click    css=button#Checkout
        Verify redirected to CCBill signup
        Fill CCBill personal details
        Fill CCBill payment details    account_num=${acno}    routing_num=${rtno}
        Click submit order
    END

Verify redirected to CCBill signup
    [Documentation]    Verify redirect to CCBill signup page and log the final URL.
    [Arguments]    ${prefix}=https://bill.ccbill.com/jpost/signup
    Wait Until Keyword Succeeds    30s    1s    Current URL should start with    ${prefix}
    ${finalUrl}=    Get Url
    Log To Console    Redirected URL: ${finalUrl}

Fill CCBill personal details
    [Documentation]    Fill CCBill signup personal info after redirect.
    [Arguments]    ${first}=Robin    ${last}=Mon    ${address}=55 E 10th St    ${city}=New York    ${state}=New York    ${country}=United States    ${zip}=10003
    Wait For Elements State    css=input[name="customer_fname"]    visible    timeout=30s
    Fill Text    css=input[name="customer_fname"]    ${first}
    Fill Text    css=input[name="customer_lname"]    ${last}
    Fill Text    css=input[name="address1"]          ${address}
    Fill Text    css=input[name="city"]              ${city}
    Run Keyword And Ignore Error    Select Options By    css=#stateId      label    ${state}
    Run Keyword And Ignore Error    Select Options By    css=#stateId      value    NY
    Run Keyword And Ignore Error    Select Options By    css=#countryId    label    ${country}
    Run Keyword And Ignore Error    Select Options By    css=#countryId    value    US
    Fill Text    css=input[name="zipcode"]           ${zip}

Fill CCBill payment details
    [Documentation]    Fill CCBill payment info fields (ACH) after redirect.
    [Arguments]    ${name_on_account}=Robin Mon    ${account_num}=${ACNO}    ${routing_num}=${RTNO}
    Wait For Elements State    css=input[name="name_on_account"]    visible    timeout=30s
    Fill Text    css=input[name="name_on_account"]    ${name_on_account}
    Wait For Elements State    css=#bankAccountInput    visible    timeout=30s
    Wait For Elements State    css=#routingNumInput     visible    timeout=30s
    Fill Text    css=#bankAccountInput    ${account_num}
    Fill Text    css=#routingNumInput     ${routing_num}
    Log To Console    Account used: ${account_num} | Routing used: ${routing_num}

Click submit order
    [Documentation]    Click CCBill "Submit Order" button.
    Wait For Elements State    css=input.submitField    visible    timeout=30s
    Click    css=input.submitField
    Log To Console    Clicked: Submit Order
    Verify email notification page

Verify email notification page
    [Documentation]    Verify redirect to email notification page and Resend Email button is visible.
    Wait Until Keyword Succeeds    45s    1s    Current URL should start with    https://bill.ccbill.com/jpost/emailNotification.cgi
    ${finalUrl}=    Get Url
    Log To Console    Redirected URL: ${finalUrl}
    Wait For Elements State    css=input[name="resendEmail"]    visible    timeout=30s
    Log To Console    PASS: Resend Email button is visible

Current URL should start with
    [Arguments]    ${prefix}
    ${url}=    Get Url
    Should Start With    ${url}    ${prefix}

Select 30 day membership and proceed to checkout
    [Documentation]    Close consent modal, select 30 day membership, fill email/password if prompted, proceed to checkout.
    [Arguments]    ${password}=${PASSWORD}    ${email}=${EMAIL}    ${acno}=${ACNO}    ${rtno}=${RTNO}
    Close modal and select 30 day membership
    Enter email and password and proceed to checkout    ${password}    ${email}    ${acno}    ${rtno}
