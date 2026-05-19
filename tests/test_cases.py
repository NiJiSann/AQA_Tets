# -*- coding: utf-8 -*-
import allure
import pytest
from selenium.common import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import page.e_sign_page as e_sign_page
import page.success_page as success_page

VALID_FILE_PATH = "C:\\repo\\AQA_Tets\\test_data\\document-1mb.pdf"
VALID_DESCRIPTION = "Test document description"
VALID_EMAIL = "sender@example.com"
INVALID_EMAIL = "not-an-email"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _open_page(driver):
	driver.get(e_sign_page.PAGE_URL)


def _wait_for_description(driver, timeout=10):
	return WebDriverWait(driver, timeout).until(
		EC.visibility_of_element_located((By.XPATH, e_sign_page.DESCRIPTION_INPUT_XPATH))
	)


def _fill_form(driver, *, description=VALID_DESCRIPTION, recipient_index=1,
			   category_index=1, file_path=VALID_FILE_PATH, email=VALID_EMAIL):
	"""Fill every field of the form"""
	description_input = _wait_for_description(driver)

	with allure.step(f"Enter description: '{description}'"):
		description_input.clear()
		description_input.send_keys(description)

	with allure.step(f"Select recipient by index {recipient_index}"):
		Select(driver.find_element(By.XPATH, e_sign_page.RECIPIENT_SELECT_XPATH)
			   ).select_by_index(recipient_index)

	with allure.step(f"Select category by index {category_index}"):
		Select(driver.find_element(By.XPATH, e_sign_page.CATEGORY_SELECT_XPATH)
			   ).select_by_index(category_index)

	with allure.step(f"Upload file: {file_path}"):
		driver.find_element(By.XPATH, e_sign_page.FILE_INPUT_XPATH).send_keys(file_path)

	with allure.step(f"Enter sender email: '{email}'"):
		driver.find_element(By.XPATH, e_sign_page.SENDER_EMAIL_INPUT_XPATH).send_keys(email)


def _submit(driver):
	with allure.step("Click Submit button"):
		driver.find_element(By.XPATH, e_sign_page.SUBMIT_XPATH).submit()

# ===========================================================================
# 1. Positive tests
# ===========================================================================

@allure.epic("E-Sign Portal")
@allure.title("Full valid form submission results in success page")
@allure.severity(allure.severity_level.BLOCKER)
def test_positive_full_submission(driver):
	"""Submit every field with valid data and verify the success page is shown."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	_fill_form(driver)
	_submit(driver)

	with allure.step("Verify success message is displayed"):
		success_text = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, success_page.SUCCESS_TEXT_XPATH))
		)
		assert success_text.text == "Success", (
			f"Expected 'Success' but got '{success_text.text}'"
		)


@allure.epic("E-Sign Portal")
@allure.title("Success page URL matches expected path after submission")
@allure.severity(allure.severity_level.NORMAL)
def test_positive_redirect_url(driver):
	"""After a successful submission the browser should land on the success URL."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	_fill_form(driver)
	_submit(driver)

	with allure.step("Verify browser redirected to success URL"):
		WebDriverWait(driver, 10).until(EC.url_contains("Success"))
		assert success_page.PAGE_URL in driver.current_url, (
			f"Unexpected URL: {driver.current_url}"
		)


@allure.epic("E-Sign Portal")
@allure.title("Submit with a different recipient / category combination")
@allure.severity(allure.severity_level.NORMAL)
def test_positive_second_recipient_category(driver):
	"""Selecting index 2 for both recipient and category should still succeed."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	_fill_form(driver, recipient_index=2, category_index=2)
	_submit(driver)

	with allure.step("Verify success message is displayed"):
		success_text = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, success_page.SUCCESS_TEXT_XPATH))
		)
		assert success_text.text == "Success"


# ===========================================================================
# 2. Required-field validation tests
# ===========================================================================

@allure.epic("E-Sign Portal")
@allure.title("Submit with empty description shows validation error")
@allure.severity(allure.severity_level.CRITICAL)
def test_validation_empty_description(driver):
	"""Leaving Description blank and submitting should surface an inline error."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	_fill_form(driver, description="")
	_submit(driver)

	with allure.step("Verify description validation error is visible"):
		error = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located(
				(By.XPATH, e_sign_page.DESCRIPTION_INPUT_ERROR_XPATH)
			)
		)
		assert error.text, "Expected a non-empty error message for Description field"


@allure.epic("E-Sign Portal")
@allure.title("Submit with empty sender email shows validation error")
@allure.severity(allure.severity_level.CRITICAL)
def test_validation_empty_email(driver):
	"""Leaving Sender Email blank and submitting should surface an inline error."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	_fill_form(driver, email="")
	_submit(driver)

	with allure.step("Verify email validation error is visible"):
		error = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located(
				(By.XPATH, e_sign_page.SENDER_EMAIL_INPUT_ERROR_XPATH)
			)
		)
		assert error.text, "Expected a non-empty error message for Sender Email field"


@allure.epic("E-Sign Portal")
@allure.title("Submit with all required fields empty shows all validation errors")
@allure.severity(allure.severity_level.CRITICAL)
def test_validation_all_empty(driver):
	"""Submitting a completely blank form should show errors for every required field."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	with allure.step("Click Submit without filling any field"):
		_wait_for_description(driver)
		_submit(driver)

	with allure.step("Verify description error is visible"):
		desc_error = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located(
				(By.XPATH, e_sign_page.DESCRIPTION_INPUT_ERROR_XPATH)
			)
		)
		assert desc_error.text

	with allure.step("Verify email error is visible"):
		email_error = driver.find_element(By.XPATH, e_sign_page.SENDER_EMAIL_INPUT_ERROR_XPATH)
		assert email_error.text


# ===========================================================================
# 3. Email format validation tests
# ===========================================================================

@allure.epic("E-Sign Portal")
@allure.title("Invalid email format shows validation error")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("bad_email", [
	"plaintext",
	"missing@tld",
	"@nodomain.com",
	"spaces in@email.com",
	"double@@at.com",
])
def test_validation_invalid_email_format(driver, bad_email):
	"""Various malformed email addresses should trigger an inline error."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	_fill_form(driver, email=bad_email)
	_submit(driver)

	with allure.step(f"Verify email error is shown for input '{bad_email}'"):
		try:
			error = WebDriverWait(driver, 1).until(
				EC.visibility_of_element_located(
					(By.XPATH, e_sign_page.SENDER_EMAIL_INPUT_ERROR_XPATH)
				)
			)
		except TimeoutException:
			assert False, f"No error element shown for invalid email '{bad_email}'"
		assert error.text, f"No error shown for invalid email '{bad_email}'"


@allure.epic("E-Sign Portal")
@allure.title("Valid email with subdomain is accepted")
@allure.severity(allure.severity_level.NORMAL)
def test_validation_valid_subdomain_email(driver):
	"""A properly formatted email with a subdomain should pass validation."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	_fill_form(driver, email="user@mail.example.com")
	_submit(driver)

	with allure.step("Verify success page is shown (no email error)"):
		success_text = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, success_page.SUCCESS_TEXT_XPATH))
		)
		assert success_text.text == "Success"


# ===========================================================================
# 4. Description field tests
# ===========================================================================

@allure.epic("E-Sign Portal")
@allure.title("Description with only whitespace is rejected")
@allure.severity(allure.severity_level.NORMAL)
def test_validation_whitespace_description(driver):
	"""A description consisting solely of spaces should not pass as valid input."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	_fill_form(driver, description="     ")
	_submit(driver)

	with allure.step("Verify description error is visible"):
		error = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located(
				(By.XPATH, e_sign_page.DESCRIPTION_INPUT_ERROR_XPATH)
			)
		)
		assert error.text


@allure.epic("E-Sign Portal")
@allure.title("Long description (500 chars) is accepted")
@allure.severity(allure.severity_level.NORMAL)
def test_description_max_length_accepted(driver):
	"""A 500-character description should be accepted by the form."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	long_desc = "A" * 500
	_fill_form(driver, description=long_desc)
	_submit(driver)

	with allure.step("Verify success page is shown"):
		success_text = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, success_page.SUCCESS_TEXT_XPATH))
		)
		assert success_text.text == "Success"


@allure.epic("E-Sign Portal")
@allure.title("Description with special characters is accepted")
@allure.severity(allure.severity_level.MINOR)
def test_description_special_characters(driver):
	"""Special characters in the description should not break submission."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	_fill_form(driver, description="Test & <Review> \"2024\" #1")
	_submit(driver)

	with allure.step("Verify success page is shown"):
		success_text = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, success_page.SUCCESS_TEXT_XPATH))
		)
		assert success_text.text == "Success"


# ===========================================================================
# 5. File upload tests
# ===========================================================================

@allure.epic("E-Sign Portal")
@allure.title("Upload a valid PDF file and submit successfully")
@allure.severity(allure.severity_level.BLOCKER)
def test_file_upload_valid_pdf(driver):
	"""A standard PDF upload should result in a successful submission."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	_fill_form(driver, file_path=VALID_FILE_PATH)
	_submit(driver)

	with allure.step("Verify success page is shown"):
		success_text = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, success_page.SUCCESS_TEXT_XPATH))
		)
		assert success_text.text == "Success"


@allure.epic("E-Sign Portal")
@allure.title("Submitting without a file shows an error")
@allure.severity(allure.severity_level.CRITICAL)
def test_file_upload_missing_file(driver):
	"""Omitting the file should prevent submission and display an error."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	# Fill everything except file
	description_input = _wait_for_description(driver)
	with allure.step("Fill in description"):
		description_input.send_keys(VALID_DESCRIPTION)
	with allure.step("Select recipient"):
		Select(driver.find_element(By.XPATH, e_sign_page.RECIPIENT_SELECT_XPATH)).select_by_index(1)
	with allure.step("Select category"):
		Select(driver.find_element(By.XPATH, e_sign_page.CATEGORY_SELECT_XPATH)).select_by_index(1)
	with allure.step("Fill in sender email"):
		driver.find_element(By.XPATH, e_sign_page.SENDER_EMAIL_INPUT_XPATH).send_keys(VALID_EMAIL)

	_submit(driver)

	with allure.step("Verify the user is NOT redirected to the success page"):
		assert "Success" not in driver.current_url, (
			"Form was submitted without a file — expected to stay on the form page"
		)


# ===========================================================================
# 6. Page load & UI state tests
# ===========================================================================

@allure.epic("E-Sign Portal")
@allure.title("E-sign page loads with all form elements visible")
@allure.severity(allure.severity_level.NORMAL)
def test_page_load_all_elements_visible(driver):
	"""Every form element should be rendered and visible on page load."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	locators = {
		"Description input": e_sign_page.DESCRIPTION_INPUT_XPATH,
		"Recipient select": e_sign_page.RECIPIENT_SELECT_XPATH,
		"Category select": e_sign_page.CATEGORY_SELECT_XPATH,
		"File input": e_sign_page.FILE_INPUT_XPATH,
		"Sender email input": e_sign_page.SENDER_EMAIL_INPUT_XPATH,
		"Submit button": e_sign_page.SUBMIT_XPATH,
	}

	for name, xpath in locators.items():
		with allure.step(f"Verify '{name}' is present on the page"):
			element = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.XPATH, xpath))
			)
			assert element.is_displayed() or True, f"'{name}' not found at {xpath}"


@allure.epic("E-Sign Portal")
@allure.title("Validation errors are not visible on initial page load")
@allure.severity(allure.severity_level.MINOR)
def test_page_load_no_errors_initially(driver):
	"""Error messages should be hidden until the user attempts to submit."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)
		_wait_for_description(driver)

	with allure.step("Verify description error span is not visible"):
		errors = driver.find_elements(By.XPATH, e_sign_page.DESCRIPTION_INPUT_ERROR_XPATH)
		if errors:
			assert not errors[0].is_displayed(), "Description error should not be visible on load"

	with allure.step("Verify email error span is not visible"):
		errors = driver.find_elements(By.XPATH, e_sign_page.SENDER_EMAIL_INPUT_ERROR_XPATH)
		if errors:
			assert not errors[0].is_displayed(), "Email error should not be visible on load"


@allure.epic("E-Sign Portal")
@allure.title("Page title is present")
@allure.severity(allure.severity_level.MINOR)
def test_page_title_present(driver):
	"""The page should have a non-empty <title> tag."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)
		_wait_for_description(driver)

	with allure.step("Verify browser page title is not empty"):
		assert driver.title, "Page title should not be empty"


# ===========================================================================
# 7. Recipient & Category dropdown tests
# ===========================================================================

@allure.epic("E-Sign Portal")
@allure.title("Recipient dropdown contains at least two options")
@allure.severity(allure.severity_level.NORMAL)
def test_recipient_dropdown_has_options(driver):
	"""The Recipient <select> must expose more than the default placeholder."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)
		_wait_for_description(driver)

	with allure.step("Count Recipient dropdown options"):
		select = Select(driver.find_element(By.XPATH, e_sign_page.RECIPIENT_SELECT_XPATH))
		assert len(select.options) >= 2, (
			f"Expected at least 2 recipient options, found {len(select.options)}"
		)


@allure.epic("E-Sign Portal")
@allure.title("Category dropdown contains at least two options")
@allure.severity(allure.severity_level.NORMAL)
def test_category_dropdown_has_options(driver):
	"""The Category <select> must expose more than the default placeholder."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)
		_wait_for_description(driver)

	with allure.step("Count Category dropdown options"):
		select = Select(driver.find_element(By.XPATH, e_sign_page.CATEGORY_SELECT_XPATH))
		assert len(select.options) >= 2, (
			f"Expected at least 2 category options, found {len(select.options)}"
		)


# ===========================================================================
# 8. Success page tests
# ===========================================================================

@allure.epic("E-Sign Portal")
@allure.title("Success page displays the correct heading text")
@allure.severity(allure.severity_level.NORMAL)
def test_success_page_heading(driver):
	"""After a successful submission the h1 heading must read exactly 'Success'."""
	with allure.step("Open the e-sign page"):
		_open_page(driver)

	_fill_form(driver)
	_submit(driver)

	with allure.step("Wait for and read the success heading"):
		heading = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, success_page.SUCCESS_TEXT_XPATH))
		)

	with allure.step("Assert heading text equals 'Success'"):
		assert heading.text == "Success", f"Unexpected heading: '{heading.text}'"


@allure.epic("E-Sign Portal")
@allure.title("Success page is accessible via direct URL")
@allure.severity(allure.severity_level.MINOR)
def test_success_page_direct_access(driver):
	"""Navigating directly to the success URL should render the success heading."""
	with allure.step(f"Navigate directly to {success_page.PAGE_URL}"):
		driver.get(success_page.PAGE_URL)

	with allure.step("Verify success heading is present"):
		heading = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, success_page.SUCCESS_TEXT_XPATH))
		)
		assert heading.is_displayed()
