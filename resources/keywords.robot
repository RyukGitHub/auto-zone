*** Settings ***
Library    Browser
Library    DateTime

*** Variables ***
${EMAIL}       ${EMPTY}
${PASSWORD}    ruby1234
${ACNO}        903219417861450
${RTNO}        063201875
${BROWSER_TIMEOUT}    20s

*** Keywords ***
Capture screenshot
    [Documentation]    Save a screenshot to the Robot output directory.
    [Arguments]    ${name}=screenshot
    Take Screenshot    ${name}-{index}

Close consent modal if present
    ${btn}=    Set Variable    css=div.modal-dialog button[data-bs-dismiss="modal"]:has-text("I agree")
    ${count}=  Get Element Count    ${btn}
    IF    ${count} > 0
        Wait For Elements State    ${btn}    visible    timeout=5s
        Click    ${btn}
    ELSE
        ${btn2}=    Set Variable    css=div.modal-dialog button.agree[data-bs-dismiss="modal"]
        ${count2}=  Get Element Count    ${btn2}
        IF    ${count2} > 0
            Wait For Elements State    ${btn2}    visible    timeout=5s
            Click    ${btn2}
        END
    END

Close content modal if present
    [Documentation]    Backwards-compatible alias.
    Close consent modal if present

Open join page
    [Arguments]    ${url}=${JOIN_URL}
    Set Browser Timeout    ${BROWSER_TIMEOUT}
    New Page    about:blank
    Go To    ${url}    timeout=20s

Select payment method ACH
    [Documentation]    Select ACH payment option (cascid=${CASCID}) if available.
    ${ach}=    Set Variable    css=a[data-ignore-join-block="true"][href*="cascid=${CASCID}"]:has-text("ACH")
    ${count}=    Get Element Count    ${ach}
    IF    ${count} > 0
        Click    ${ach}
        Wait Until Keyword Succeeds    20s    1s    Current URL should contain    cascid=${CASCID}
    ELSE
        Log To Console    ACH payment option not found, assuming default/only option.
    END

Select 30 day membership option
    [Documentation]    Select the "30 Day Membership" plan after the modal is closed.
    ${option}=    Set Variable    css=label.join-option:has-text("30 Day Membership")
    Capture screenshot    before-wait-membership
    ${status}    ${msg}=    Run Keyword And Ignore Error    Wait For Elements State    ${option}    visible    timeout=20s
    IF    '${status}' != 'PASS'
        ${option_alt}=    Set Variable    xpath=//label[contains(@class, 'join-option')]//div[contains(text(), '30 Day Membership')]/..
        ${status2}    ${msg2}=    Run Keyword And Ignore Error    Wait For Elements State    ${option_alt}    visible    timeout=5s
        IF    '${status2}' != 'PASS'
            ${u}=    Get Url
            ${t}=    Get Title
            Log To Console    ERROR: Membership option not visible. Title: ${t} | URL: ${u}
            Capture screenshot    membership-not-visible
            Fail    ${msg2}
        END
        Click    ${option_alt}
    ELSE
        Click    ${option}
    END
    ${submit_btn}=    Set Variable    css=button.submit-btn:has-text("Get Access Now")
    ${submit_count}=    Get Element Count    ${submit_btn}
    IF    ${submit_count} > 0
        Run Keyword And Ignore Error    Click    ${submit_btn}    timeout=2s
    ELSE
        ${submit_btn2}=    Set Variable    css=button.submit-btn[type="submit"]
        ${submit_count2}=    Get Element Count    ${submit_btn2}
        IF    ${submit_count2} > 0
            Run Keyword And Ignore Error    Click    ${submit_btn2}    timeout=2s
        END
    END
    Capture screenshot    after-select-membership

Close modal and select 30 day membership
    [Documentation]    Close the modal if shown, then select the 30 day plan.
    Close consent modal if present
    Select payment method ACH
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
        Log To Console    Email used: ${email} | Password: ${password}
        Wait For Elements State    css=button#Checkout    visible    timeout=15s
        Capture screenshot    before-click-checkout
        Click    css=button#Checkout
        Run Keyword And Ignore Error    Switch Page    NEW
        Capture screenshot    after-click-checkout
        Verify redirected to CCBill signup
        Fill CCBill personal details
        Fill CCBill payment details    account_num=${acno}    routing_num=${rtno}
        Click submit order
    ELSE
        Log To Console    Username prompt did not appear. Attempting CCBill checkout directly.
        Verify redirected to CCBill signup
        Fill CCBill personal details
        Fill CCBill payment details    account_num=${acno}    routing_num=${rtno}
        Click submit order
    END

Verify redirected to CCBill signup
    [Documentation]    Verify redirect to CCBill signup page and log the final URL.
    [Arguments]    ${prefix}=https://bill.ccbill.com/jpost/signup
    Wait Until Keyword Succeeds    20s    1s    Current URL should start with    ${prefix}
    ${finalUrl}=    Get Url
    Log To Console    Redirected URL: ${finalUrl}

Fill CCBill personal details
    [Documentation]    Fill CCBill signup personal info after redirect.
    [Arguments]    ${first}=Robin    ${last}=Mon    ${address}=55 E 10th St    ${city}=New York    ${state}=New York    ${country}=United States    ${zip}=10003
    Wait For Elements State    css=input[name="customer_fname"]    visible    timeout=20s
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
    Wait For Elements State    css=#bankAccountInput    visible    timeout=20s
    ${name_count}=    Get Element Count    css=input[name="name_on_account"]
    IF    ${name_count} > 0
        Fill Text    css=input[name="name_on_account"]    ${name_on_account}
    END
    Wait For Elements State    css=#bankAccountInput    visible    timeout=20s
    Wait For Elements State    css=#routingNumInput     visible    timeout=20s
    Fill Text    css=#bankAccountInput    ${account_num}
    Fill Text    css=#routingNumInput     ${routing_num}
    Log To Console    Account used: ${account_num} | Routing used: ${routing_num}

Click submit order
    [Documentation]    Click CCBill "Submit Order" button.
    Wait For Elements State    css=input.submitField    visible    timeout=20s
    Capture screenshot    before-submit-order
    Click    css=input.submitField
    Log To Console    Clicked: Submit Order
    Verify email notification page

Verify email notification page
    [Documentation]    Verify redirect to email notification page and Resend Email button is visible.
    Wait Until Keyword Succeeds    20s    1s    Current URL should start with    https://bill.ccbill.com/jpost/emailNotification.cgi
    ${finalUrl}=    Get Url
    Log To Console    Redirected URL: ${finalUrl}
    Wait For Elements State    css=input[name="resendEmail"]    visible    timeout=20s
    Log To Console    PASS: Resend Email button is visible

Current URL should start with
    [Arguments]    ${prefix}
    ${url}=    Get Url
    Should Start With    ${url}    ${prefix}

Current URL should contain
    [Arguments]    ${text}
    ${url}=    Get Url
    Should Contain    ${url}    ${text}

Select 30 day membership and proceed to checkout
    [Documentation]    Close consent modal, select 30 day membership, fill email/password if prompted, proceed to checkout.
    [Arguments]    ${password}=${PASSWORD}    ${email}=${EMAIL}    ${acno}=${ACNO}    ${rtno}=${RTNO}
    Close modal and select 30 day membership
    Enter email and password and proceed to checkout    ${password}    ${email}    ${acno}    ${rtno}
