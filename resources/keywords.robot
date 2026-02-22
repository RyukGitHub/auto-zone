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
        Log To Console    Found "I agree" modal, clicking it...
        Wait For Elements State    ${btn}    visible    timeout=5s
        Sleep    1s
        Click    ${btn}
    ELSE
        ${btn2}=    Set Variable    css=button.agree:has-text("I agree")
        ${count2}=  Get Element Count    ${btn2}
        IF    ${count2} > 0
            Log To Console    Found alternative consent modal, clicking it...
            Wait For Elements State    ${btn2}    visible    timeout=5s
            Sleep    1s
            Click    ${btn2}
        ELSE
            ${btn3}=    Set Variable    css=button.btn-primary.agree
            ${count3}=  Get Element Count    ${btn3}
            IF    ${count3} > 0
                Log To Console    Found tertiary consent modal button, clicking it...
                Wait For Elements State    ${btn3}    visible    timeout=5s
                Sleep    1s
                Click    ${btn3}
            END
        END
    END
    Sleep    2s

Close content modal if present
    [Documentation]    Backwards-compatible alias.
    Close consent modal if present

Open join page
    [Arguments]    ${url}=${JOIN_URL}
    Log To Console    Opening join page URL: ${url}
    Set Browser Timeout    ${BROWSER_TIMEOUT}
    New Page    about:blank
    Go To    ${url}    timeout=20s
    Sleep    1s
    ${current_url}=    Get Url
    ${is_sfw}=    Run Keyword And Return Status    Should Contain    ${current_url}    /sfw
    IF    ${is_sfw}
        Log To Console    SFW Redirect detected. Reloading join page: ${url}
        Go To    ${url}    timeout=20s
        Sleep    1s
        Close consent modal if present
    END

Select payment method ACH
    [Documentation]    Select ACH payment option (cascid=${CASCID}) if available.
    ${ach}=    Set Variable    css=a[data-ignore-join-block="true"][href*="cascid=${CASCID}"]:has-text("ACH")
    ${count}=    Get Element Count    ${ach}
    IF    ${count} > 0
        Log To Console    Found ACH payment option, clicking it...
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
        Log To Console    Found fallback 30 Day Membership option, clicking it...
        Click    ${option_alt}
    ELSE
        Log To Console    Found 30 Day Membership option, clicking it...
        Click    ${option}
    END
    ${submit_btn}=    Set Variable    css=button.submit-btn:has-text("Get Access Now")
    ${submit_count}=    Get Element Count    ${submit_btn}
    IF    ${submit_count} > 0
        Log To Console    Found Get Access Now button, clicking it...
        Run Keyword And Ignore Error    Wait For Elements State    ${submit_btn}    visible    timeout=2s
        Run Keyword And Ignore Error    Click    ${submit_btn}
    ELSE
        ${submit_btn2}=    Set Variable    css=button.submit-btn[type="submit"]
        ${submit_count2}=    Get Element Count    ${submit_btn2}
        IF    ${submit_count2} > 0
            Log To Console    Found alternative submit button, clicking it...
            Run Keyword And Ignore Error    Wait For Elements State    ${submit_btn2}    visible    timeout=2s
            Run Keyword And Ignore Error    Click    ${submit_btn2}
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
        Log To Console    Filling basic information in checkout step...
        Fill CCBill personal details
        Fill CCBill payment details    account_num=${acno}    routing_num=${rtno}
        Click submit order
        RETURN    ${email}
    ELSE
        Log To Console    Username prompt did not appear. Attempting CCBill checkout directly.
        Verify redirected to CCBill signup
        Log To Console    Filling basic information in checkout step...
        Fill CCBill personal details
        Fill CCBill payment details    account_num=${acno}    routing_num=${rtno}
        Click submit order
        RETURN    ${email}
    END

Verify redirected to CCBill signup
    [Documentation]    Verify redirect to CCBill signup page and log the final URL.
    [Arguments]    ${prefix}=https://bill.ccbill.com/jpost/signup
    Wait Until Keyword Succeeds    20s    1s    Current URL should start with    ${prefix}
    ${finalUrl}=    Get Url
    Log To Console    Redirected URL: ${finalUrl}

Fill CCBill personal details
    [Documentation]    Fill CCBill signup personal info after redirect.
    [Arguments]    ${first}=Robin    ${last}=Mon    ${address}=55 E 10th St    ${city}=New York    ${state}=New York    ${country}=United States    ${zip}=10003    ${phone}=7797797791
    Wait For Elements State    css=input[name="address1"]    visible    timeout=20s
    ${fname_count}=    Get Element Count    css=input[name="customer_fname"]
    IF    ${fname_count} > 0
        Fill Text    css=input[name="customer_fname"]    ${first}
        Fill Text    css=input[name="customer_lname"]    ${last}
    END
    Fill Text    css=input[name="address1"]          ${address}
    Fill Text    css=input[name="city"]              ${city}
    Run Keyword And Ignore Error    Select Options By    css=#stateId      label    ${state}
    Run Keyword And Ignore Error    Select Options By    css=#stateId      value    NY
    Run Keyword And Ignore Error    Select Options By    css=#countryId    label    ${country}
    Run Keyword And Ignore Error    Select Options By    css=#countryId    value    US
    Fill Text    css=input[name="zipcode"]           ${zip}
    
    # Fill optional phone number if present
    ${phone_count}=    Get Element Count    css=input[name="phone_number"]
    IF    ${phone_count} > 0
        Fill Text    css=input[name="phone_number"]    ${phone}
    END

Fill CCBill payment details
    [Documentation]    Fill CCBill payment info fields (ACH) after redirect.
    [Arguments]    ${name_on_account}=Robin Mon    ${account_num}=${ACNO}    ${routing_num}=${RTNO}
    
    IF    '${account_num}' == '${EMPTY}'
        ${account_num}=    Generate Account Number
        Set Suite Variable    ${ACNO}    ${account_num}
    END
    
    # Generate routing details dynamically or validate the user-provided one
    ${rtno_to_test}=    Set Variable If    '${routing_num}' == '${EMPTY}'    ${None}    ${routing_num}
    ${routing_data}=    Get Routing Number Details    ${rtno_to_test}
    
    # Extract details from dictionary
    ${final_rtno}=    Get From Dictionary    ${routing_data}    routing
    ${bank_name}=     Get From Dictionary    ${routing_data}    bank
    ${bank_city}=     Get From Dictionary    ${routing_data}    city
    ${bank_zip}=      Get From Dictionary    ${routing_data}    zip
    
    # Set suite variables for the Discord Teardown
    Set Suite Variable    ${RTNO}         ${final_rtno}
    Set Suite Variable    ${BANK_NAME}    ${bank_name}
    Set Suite Variable    ${BANK_CITY}    ${bank_city}
    Set Suite Variable    ${BANK_ZIP}     ${bank_zip}
    
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
    [Documentation]    Click CCBill "Submit Order" button, handle optional "Process Transaction" confirmation, and verify success.
    ${submit_btn}=    Set Variable    css=input[name="submit"]
    ${count}=    Get Element Count    ${submit_btn}
    IF    ${count} == 0
        ${submit_btn}=    Set Variable    css=input.submitField
    END
    Wait For Elements State    ${submit_btn}    visible    timeout=20s
    Capture screenshot    before-submit-order
    Click    ${submit_btn}
    Log To Console    Clicked: Submit Order / Complete this Purchase
    
    # Handle optional Process Transaction confirmation screen
    Sleep    3s
    ${process_count}=    Get Element Count    css=input[value="Process Transaction"]
    IF    ${process_count} > 0
        Log To Console    Found "Process Transaction" confirmation, clicking it...
        Click    css=input[value="Process Transaction"]
        Sleep    2s
    END

    Verify success redirect

Verify success redirect
    [Documentation]    Verify redirect to either email notification page or merchant login page.
    Wait Until Keyword Succeeds    25s    3s    Url should indicate success

Url should indicate success
    ${url}=    Get Url
    ${is_email}=    Run Keyword And Return Status    Should Contain    ${url}    emailNotification.cgi
    ${is_signup}=    Run Keyword And Return Status    Should Contain    ${url}    bill.ccbill.com/jpost/signup
    
    IF    ${is_email}
        Log To Console    PASS: Redirected to CCBill Email Notification
        Wait For Elements State    css=input[name="resendEmail"]    visible    timeout=5s
    ELSE IF    ${is_signup}
        # If there's an error message, we fail immediately so the test terminates
        ${err_count}=    Get Element Count    css=div.error
        IF    ${err_count} > 0
            ${err_txt}=    Get Text    css=div.error
            # Ignore empty error blocks that CCBill leaves in DOM
            IF    '${err_txt}' != '${EMPTY}'
                Fail    Transaction failed on CCBill: ${err_txt}
            END
        END
        Fail    Still on CCBill signup page, transaction not complete yet.
    ELSE
        Log To Console    PASS: Redirected to merchant site successfully: ${url}
    END

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
    ${final_email}=    Enter email and password and proceed to checkout    ${password}    ${email}    ${acno}    ${rtno}
    RETURN    ${final_email}
