document.addEventListener('DOMContentLoaded', function() {

    // --- Helper Functions ---

    // Function to validate email format
    const isValidEmail = (email) => {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailPattern.test(email);
    };

    // Function to validate verification code format (e.g., 6 digits)
    const isValidVerificationCode = (code) => {
        // Assuming a 6-digit numeric code. Adjust regex if format differs.
        const codePattern = /^\d{6}$/; 
        return codePattern.test(code);
    };

    // Function to display field error
    const showFieldError = (inputElement, errorElement, message) => {
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
        if (inputElement) {
            inputElement.classList.add('input-error-border');
        }
    };

    // Function to hide field error
    const hideFieldError = (inputElement, errorElement) => {
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        }
        if (inputElement) {
            inputElement.classList.remove('input-error-border');
        }
    };

    // Password visibility toggle
    function setupPasswordToggle(passwordInput, confirmPasswordInput, toggleIcon1, toggleIcon2 = null) {
        const toggleVisibility = () => {
            const currentType = passwordInput.getAttribute('type');
            const newType = currentType === 'password' ? 'text' : 'password';

            if (passwordInput) passwordInput.setAttribute('type', newType);
            if (confirmPasswordInput) confirmPasswordInput.setAttribute('type', newType);

            const updateIcon = (iconElement) => {
                if (iconElement) {
                    iconElement.querySelector('i').classList.remove('fa-eye', 'fa-eye-slash');
                    if (newType === 'password') {
                        iconElement.querySelector('i').classList.add('fa-eye-slash');
                    } else {
                        iconElement.querySelector('i').classList.add('fa-eye');
                    }
                }
            };

            updateIcon(toggleIcon1);
            if (toggleIcon2) updateIcon(toggleIcon2);
        };

        if (passwordInput && toggleIcon1) {
            toggleIcon1.addEventListener('click', toggleVisibility);
        }
        if (confirmPasswordInput && toggleIcon2) {
            toggleIcon2.addEventListener('click', toggleVisibility);
        }
    }

    // --- Field Focus Tracker (for blur validation) ---
    // Tracks if a field has been focused at least once.
    // Errors will only show on blur if the field has been focused.
    const fieldFocusTracker = {
        emailRegister: false,
        usernameRegister: false,
        passwordRegister: false,
        password2Register: false,
        emailRequest: false,
        codeConfirm: false,
        newPassword1Confirm: false,
        newPassword2Confirm: false
    };

    // --- Reusable Password Strength Checker ---
    function checkPasswordStrength(passwordInput, strengthBar, strengthText, strengthMeterContainer, 
                                     lengthReq, uppercaseReq, lowercaseReq, numberReq, symbolReq) {
        const password = passwordInput.value;
        let metCount = 0;

        // Reset all requirements
        [lengthReq, uppercaseReq, lowercaseReq, numberReq, symbolReq].forEach(req => {
            if (req) { // Check if element exists before manipulating
                req.classList.remove('met-requirement');
                const icon = req.querySelector('.requirement-icon i');
                if (icon) {
                    icon.classList.remove('fa-check-circle');
                    icon.classList.add('fa-circle');
                }
            }
        });

        // Rule 1: At least 8 characters
        if (password.length >= 8) {
            metCount++;
            if (lengthReq) {
                lengthReq.classList.add('met-requirement');
                lengthReq.querySelector('.requirement-icon i').classList.remove('fa-circle');
                lengthReq.querySelector('.requirement-icon i').classList.add('fa-check-circle');
            }
        }

        // Rule 2: One uppercase letter
        if (/[A-Z]/.test(password)) {
            metCount++;
            if (uppercaseReq) {
                uppercaseReq.classList.add('met-requirement');
                uppercaseReq.querySelector('.requirement-icon i').classList.remove('fa-circle');
                uppercaseReq.querySelector('.requirement-icon i').classList.add('fa-check-circle');
            }
        }

        // Rule 3: One lowercase letter
        if (/[a-z]/.test(password)) {
            metCount++;
            if (lowercaseReq) {
                lowercaseReq.classList.add('met-requirement');
                lowercaseReq.querySelector('.requirement-icon i').classList.remove('fa-circle');
                lowercaseReq.querySelector('.requirement-icon i').classList.add('fa-check-circle');
            }
        }

        // Rule 4: One number
        if (/\d/.test(password)) {
            metCount++;
            if (numberReq) {
                numberReq.classList.add('met-requirement');
                numberReq.querySelector('.requirement-icon i').classList.remove('fa-circle');
                numberReq.querySelector('.requirement-icon i').classList.add('fa-check-circle');
            }
        }

        // Rule 5: One symbol (non-alphanumeric)
        if (/[^a-zA-Z0-9]/.test(password)) {
            metCount++;
            if (symbolReq) {
                symbolReq.classList.add('met-requirement');
                symbolReq.querySelector('.requirement-icon i').classList.remove('fa-circle');
                symbolReq.querySelector('.requirement-icon i').classList.add('fa-check-circle');
            }
        }

        // Update strength bar and text
        let strength = 'Weak';
        let barWidth = (metCount / 5) * 100;

        if (strengthMeterContainer) {
            strengthMeterContainer.classList.remove('strength-weak', 'strength-fair', 'strength-good', 'strength-strong');

            if (password.length === 0) {
                strength = 'Weak';
                barWidth = 0;
                strengthMeterContainer.classList.add('strength-weak');
            } else if (metCount <= 2) {
                strength = 'Weak';
                strengthMeterContainer.classList.add('strength-weak');
            } else if (metCount === 3) {
                strength = 'Fair';
                strengthMeterContainer.classList.add('strength-fair');
            } else if (metCount === 4) {
                strength = 'Good';
                strengthMeterContainer.classList.add('strength-good');
            } else if (metCount === 5) {
                strength = 'Strong';
                strengthMeterContainer.classList.add('strength-strong');
            }
        }

        if (strengthBar) strengthBar.style.width = barWidth + '%';
        if (strengthText) strengthText.textContent = strength;
    }

    // --- Validation Functions for Specific Fields ---

    const validateEmailField = (input, errorSpan, focusTrackerKey) => {
        const email = input.value.trim();
        if (email === '') {
            showFieldError(input, errorSpan, 'Email address is required');
            return false;
        } else if (!isValidEmail(email)) {
            showFieldError(input, errorSpan, 'Please enter a valid email address');
            return false;
        } else {
            hideFieldError(input, errorSpan);
            return true;
        }
    };

    const validateUsernameField = (input, errorSpan, focusTrackerKey) => {
        const username = input.value.trim();
        if (username === '') {
            showFieldError(input, errorSpan, 'Full name is required');
            return false;
        } else {
            hideFieldError(input, errorSpan);
            return true;
        }
    };

    const validatePasswordField = (input, errorSpan, focusTrackerKey) => {
        const password = input.value.trim();
        if (password === '') {
            showFieldError(input, errorSpan, 'Password is required');
            return false;
        } else {
            hideFieldError(input, errorSpan);
            return true;
        }
    };

    const validateConfirmPasswordField = (passwordInput1, passwordInput2, errorSpan, matchErrorSpan, focusTrackerKey) => {
        const password2 = passwordInput2.value.trim();
        let isValid = true;

        if (password2 === '') {
            showFieldError(passwordInput2, errorSpan, 'Please confirm your password');
            isValid = false;
        } else {
            hideFieldError(passwordInput2, errorSpan);
        }

        if (passwordInput1.value !== passwordInput2.value && passwordInput2.value !== '') {
            showFieldError(passwordInput2, matchErrorSpan, 'Passwords do not match');
            isValid = false;
        } else {
            hideFieldError(passwordInput2, matchErrorSpan);
        }
        return isValid;
    };

    const validateVerificationCodeField = (input, errorSpan, focusTrackerKey) => {
        const code = input.value.trim();
        if (code === '') {
            showFieldError(input, errorSpan, 'Verification code is required');
            return false;
        } else if (!isValidVerificationCode(code)) {
            showFieldError(input, errorSpan, 'Invalid code format');
            return false;
        } else {
            hideFieldError(input, errorSpan);
            return true;
        }
    };

    // --- Event Listener Setup ---

    // --- Register Page Logic ---
    const registerForm = document.getElementById('registerForm');
    const emailInputRegister = document.getElementById('id_email');
    const usernameInputRegister = document.getElementById('id_username');
    const passwordInputRegister = document.getElementById('id_password1');
    const password2InputRegister = document.getElementById('id_password2');
    const termsCheckboxRegister = document.getElementById('terms_agreement');

    const emailErrorRegister = document.getElementById('email-error');
    const usernameErrorRegister = document.getElementById('username-error');
    const passwordErrorRegister = document.getElementById('password-error');
    const password2ErrorRegister = document.getElementById('password2-error');
    const passwordMatchMessageRegister = document.getElementById('password-match-message');
    const checkboxErrorRegister = document.getElementById('checkbox-error');

    // Register Password Toggle
    const togglePassword1Register = document.getElementById('togglePassword1');
    const togglePassword2Register = document.getElementById('togglePassword2');
    if (passwordInputRegister && togglePassword1Register) {
        setupPasswordToggle(passwordInputRegister, password2InputRegister, togglePassword1Register, togglePassword2Register);
    }

    // Register Password Strength Indicator
    const strengthBarRegister = document.getElementById('strength-bar');
    const strengthTextRegister = document.getElementById('strength-text');
    const strengthMeterContainerRegister = document.getElementById('password-strength-meter-container');
    const lengthReqRegister = document.getElementById('length-req');
    const uppercaseReqRegister = document.getElementById('uppercase-req');
    const lowercaseReqRegister = document.getElementById('lowercase-req');
    const numberReqRegister = document.getElementById('number-req');
    const symbolReqRegister = document.getElementById('symbol-req');

    if (passwordInputRegister && strengthBarRegister && strengthTextRegister) {
        passwordInputRegister.addEventListener('input', () => 
            checkPasswordStrength(
                passwordInputRegister, strengthBarRegister, strengthTextRegister, strengthMeterContainerRegister,
                lengthReqRegister, uppercaseReqRegister, lowercaseReqRegister, numberReqRegister, symbolReqRegister
            )
        );
    }

    // Register Form Field Event Listeners (Blur & Input)
    if (emailInputRegister) {
        emailInputRegister.addEventListener('focus', () => fieldFocusTracker.emailRegister = true);
        emailInputRegister.addEventListener('blur', () => { if (fieldFocusTracker.emailRegister) validateEmailField(emailInputRegister, emailErrorRegister, 'emailRegister'); });
        emailInputRegister.addEventListener('input', () => hideFieldError(emailInputRegister, emailErrorRegister));
    }
    if (usernameInputRegister) {
        usernameInputRegister.addEventListener('focus', () => fieldFocusTracker.usernameRegister = true);
        usernameInputRegister.addEventListener('blur', () => { if (fieldFocusTracker.usernameRegister) validateUsernameField(usernameInputRegister, usernameErrorRegister, 'usernameRegister'); });
        usernameInputRegister.addEventListener('input', () => hideFieldError(usernameInputRegister, usernameErrorRegister));
    }
    if (passwordInputRegister) {
        passwordInputRegister.addEventListener('focus', () => fieldFocusTracker.passwordRegister = true);
        passwordInputRegister.addEventListener('blur', () => { if (fieldFocusTracker.passwordRegister) validatePasswordField(passwordInputRegister, passwordErrorRegister, 'passwordRegister'); });
        passwordInputRegister.addEventListener('input', () => {
            hideFieldError(passwordInputRegister, passwordErrorRegister);
            if (password2InputRegister) { // Also re-validate confirm password if password changes
                validateConfirmPasswordField(passwordInputRegister, password2InputRegister, password2ErrorRegister, passwordMatchMessageRegister, 'password2Register');
            }
        });
    }
    if (password2InputRegister) {
        password2InputRegister.addEventListener('focus', () => fieldFocusTracker.password2Register = true);
        password2InputRegister.addEventListener('blur', () => { if (fieldFocusTracker.password2Register) validateConfirmPasswordField(passwordInputRegister, password2InputRegister, password2ErrorRegister, passwordMatchMessageRegister, 'password2Register'); });
        password2InputRegister.addEventListener('input', () => {
            hideFieldError(password2InputRegister, password2ErrorRegister);
            hideFieldError(password2InputRegister, passwordMatchMessageRegister); // Clear mismatch on input
            validateConfirmPasswordField(passwordInputRegister, password2InputRegister, password2ErrorRegister, passwordMatchMessageRegister, 'password2Register'); // Re-validate on input
        });
    }

    // Register Form Submission
    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            let isValid = true;

            // Mark all fields as "focused" for submission validation
            for (const key in fieldFocusTracker) {
                fieldFocusTracker[key] = true;
            }

            if (emailInputRegister && !validateEmailField(emailInputRegister, emailErrorRegister, 'emailRegister')) isValid = false;
            if (usernameInputRegister && !validateUsernameField(usernameInputRegister, usernameErrorRegister, 'usernameRegister')) isValid = false;
            if (passwordInputRegister && !validatePasswordField(passwordInputRegister, passwordErrorRegister, 'passwordRegister')) isValid = false;
            if (password2InputRegister && !validateConfirmPasswordField(passwordInputRegister, password2InputRegister, password2ErrorRegister, passwordMatchMessageRegister, 'password2Register')) isValid = false;

            if (termsCheckboxRegister && checkboxErrorRegister) {
                if (!termsCheckboxRegister.checked) {
                    showFieldError(null, checkboxErrorRegister, 'Please agree to the Terms of Service and Privacy Policy');
                    isValid = false;
                } else {
                    hideFieldError(null, checkboxErrorRegister);
                }
            }
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }

    // --- Forgot Password Request Page Logic ---
    const resetPasswordRequestForm = document.getElementById('resetPasswordRequestForm');
    const emailInputRequest = document.getElementById('id_email'); // Assuming ID is id_email
    const emailErrorRequest = document.getElementById('email-request-error');

    if (emailInputRequest) {
        emailInputRequest.addEventListener('focus', () => fieldFocusTracker.emailRequest = true);
        emailInputRequest.addEventListener('blur', () => { if (fieldFocusTracker.emailRequest) validateEmailField(emailInputRequest, emailErrorRequest, 'emailRequest'); });
        emailInputRequest.addEventListener('input', () => hideFieldError(emailInputRequest, emailErrorRequest));
    }

    if (resetPasswordRequestForm) {
        resetPasswordRequestForm.addEventListener('submit', function(event) {
            let isValid = true;
            fieldFocusTracker.emailRequest = true; // For submission, consider it focused

            if (emailInputRequest && !validateEmailField(emailInputRequest, emailErrorRequest, 'emailRequest')) isValid = false;

            if (!isValid) {
                event.preventDefault();
            }
        });
    }

    // --- Forgot Password Confirm Page Logic ---
    const resetPasswordConfirmForm = document.getElementById('resetPasswordConfirmForm');
    const codeInputConfirm = document.getElementById('id_code');
    const newPassword1InputConfirm = document.getElementById('id_new_password1');
    const newPassword2InputConfirm = document.getElementById('id_new_password2');

    const codeErrorConfirm = document.getElementById('code-error');
    const newPassword1ErrorConfirm = document.getElementById('new-password1-error');
    const newPassword2ErrorConfirm = document.getElementById('new-password2-error');
    const passwordMatchMessageConfirm = document.getElementById('password-match-message-reset'); // Updated ID

    // Reset Password Confirm Page Password Toggle
    const toggleNewPassword1Confirm = document.getElementById('toggleNewPassword1');
    const toggleNewPassword2Confirm = document.getElementById('toggleNewPassword2');
    if (newPassword1InputConfirm && toggleNewPassword1Confirm) {
        setupPasswordToggle(newPassword1InputConfirm, newPassword2InputConfirm, toggleNewPassword1Confirm, toggleNewPassword2Confirm);
    }

    // Reset Password Confirm Page Password Strength Indicator
    const strengthBarConfirm = document.getElementById('strength-bar-reset'); // Updated ID
    const strengthTextConfirm = document.getElementById('strength-text-reset'); // Updated ID
    const strengthMeterContainerConfirm = document.getElementById('password-strength-meter-container-reset'); // Updated ID
    const lengthReqConfirm = document.getElementById('length-req-reset'); // Updated ID
    const uppercaseReqConfirm = document.getElementById('uppercase-req-reset'); // Updated ID
    const lowercaseReqConfirm = document.getElementById('lowercase-req-reset'); // Updated ID
    const numberReqConfirm = document.getElementById('number-req-reset'); // Updated ID
    const symbolReqConfirm = document.getElementById('symbol-req-reset'); // Updated ID

    if (newPassword1InputConfirm && strengthBarConfirm && strengthTextConfirm) {
        newPassword1InputConfirm.addEventListener('input', () => 
            checkPasswordStrength(
                newPassword1InputConfirm, strengthBarConfirm, strengthTextConfirm, strengthMeterContainerConfirm,
                lengthReqConfirm, uppercaseReqConfirm, lowercaseReqConfirm, numberReqConfirm, symbolReqConfirm
            )
        );
    }


    // Confirm Form Field Event Listeners (Blur & Input)
    if (codeInputConfirm) {
        codeInputConfirm.addEventListener('focus', () => fieldFocusTracker.codeConfirm = true);
        codeInputConfirm.addEventListener('blur', () => { if (fieldFocusTracker.codeConfirm) validateVerificationCodeField(codeInputConfirm, codeErrorConfirm, 'codeConfirm'); });
        codeInputConfirm.addEventListener('input', () => hideFieldError(codeInputConfirm, codeErrorConfirm));
    }
    if (newPassword1InputConfirm) {
        newPassword1InputConfirm.addEventListener('focus', () => fieldFocusTracker.newPassword1Confirm = true);
        newPassword1InputConfirm.addEventListener('blur', () => { if (fieldFocusTracker.newPassword1Confirm) validatePasswordField(newPassword1InputConfirm, newPassword1ErrorConfirm, 'newPassword1Confirm'); });
        newPassword1InputConfirm.addEventListener('input', () => {
            hideFieldError(newPassword1InputConfirm, newPassword1ErrorConfirm);
            if (newPassword2InputConfirm) { // Also re-validate confirm password if password changes
                validateConfirmPasswordField(newPassword1InputConfirm, newPassword2InputConfirm, newPassword2ErrorConfirm, passwordMatchMessageConfirm, 'newPassword2Confirm');
            }
        });
    }
    if (newPassword2InputConfirm) {
        newPassword2InputConfirm.addEventListener('focus', () => fieldFocusTracker.newPassword2Confirm = true);
        newPassword2InputConfirm.addEventListener('blur', () => { if (fieldFocusTracker.newPassword2Confirm) validateConfirmPasswordField(newPassword1InputConfirm, newPassword2InputConfirm, newPassword2ErrorConfirm, passwordMatchMessageConfirm, 'newPassword2Confirm'); });
        newPassword2InputConfirm.addEventListener('input', () => {
            hideFieldError(newPassword2InputConfirm, newPassword2ErrorConfirm);
            hideFieldError(newPassword2InputConfirm, passwordMatchMessageConfirm); // Clear mismatch on input
            validateConfirmPasswordField(newPassword1InputConfirm, newPassword2InputConfirm, newPassword2ErrorConfirm, passwordMatchMessageConfirm, 'newPassword2Confirm'); // Re-validate on input
        });
    }

    // Reset Password Confirm Form Submission
    if (resetPasswordConfirmForm) {
        resetPasswordConfirmForm.addEventListener('submit', function(event) {
            let isValid = true;

            // Mark all fields as "focused" for submission validation
            for (const key in fieldFocusTracker) {
                fieldFocusTracker[key] = true;
            }

            if (codeInputConfirm && !validateVerificationCodeField(codeInputConfirm, codeErrorConfirm, 'codeConfirm')) isValid = false;
            if (newPassword1InputConfirm && !validatePasswordField(newPassword1InputConfirm, newPassword1ErrorConfirm, 'newPassword1Confirm')) isValid = false;
            if (newPassword2InputConfirm && !validateConfirmPasswordField(newPassword1InputConfirm, newPassword2InputConfirm, newPassword2ErrorConfirm, passwordMatchMessageConfirm, 'newPassword2Confirm')) isValid = false;

            if (!isValid) {
                event.preventDefault();
            }
        });
    }

    // --- Login Page Specific Logic (from original auth.js, minimal changes) ---
    const loginForm = document.getElementById('loginForm'); // Assuming you have a loginForm ID
    const emailInputLogin = document.getElementById('id_username_login'); // Assuming ID is id_username_login
    const passwordInputLogin = document.getElementById('id_password_login'); // Assuming ID is id_password_login

    const emailErrorLogin = document.getElementById('id_username_login-error'); // Assuming error span ID
    const passwordErrorLogin = document.getElementById('id_password_login-error'); // Assuming error span ID

    // Login Password Toggle
    const loginPasswordInput = document.getElementById('id_password_login'); // Renamed for clarity with other password inputs
    const loginToggleIcon = document.getElementById('togglePasswordLogin'); // Assuming you have this ID
    if (loginPasswordInput && loginToggleIcon) {
        setupPasswordToggle(loginPasswordInput, null, loginToggleIcon, null);
    }

    // Add input event listeners to clear errors as user types for login fields
    if (emailInputLogin && emailErrorLogin) emailInputLogin.addEventListener('input', () => hideFieldError(emailInputLogin, emailErrorLogin));
    if (passwordInputLogin && passwordErrorLogin) passwordInputLogin.addEventListener('input', () => hideFieldError(passwordInputLogin, passwordErrorLogin));


    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            let isValid = true;

            // For login, just check if empty for now. Extend if more complex validation is needed.
            if (emailInputLogin && emailInputLogin.value.trim() === '') {
                showFieldError(emailInputLogin, emailErrorLogin, 'Please enter your email address.');
                isValid = false;
            } else if (emailInputLogin && emailErrorLogin) {
                hideFieldError(emailInputLogin, emailErrorLogin);
            }

            if (passwordInputLogin && passwordInputLogin.value.trim() === '') {
                showFieldError(passwordInputLogin, passwordErrorLogin, 'Please enter your password.');
                isValid = false;
            } else if (passwordInputLogin && passwordErrorLogin) {
                hideFieldError(passwordInputLogin, passwordErrorLogin);
            }

            if (!isValid) {
                event.preventDefault();
            }
        });
    }
});