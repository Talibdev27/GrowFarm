document.addEventListener('DOMContentLoaded', function() {
    // Registration form validation
    const registrationForm = document.getElementById('registration-form');
    if (registrationForm) {
        const usernameInput = document.getElementById('username');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirm_password');
        
        // Username validation
        usernameInput.addEventListener('blur', function() {
            validateUsername(this);
        });
        
        // Email validation
        emailInput.addEventListener('blur', function() {
            validateEmail(this);
        });
        
        // Password validation
        passwordInput.addEventListener('input', function() {
            validatePassword(this);
            if (confirmPasswordInput.value) {
                validatePasswordMatch(confirmPasswordInput, this);
            }
        });
        
        // Confirm password validation
        confirmPasswordInput.addEventListener('input', function() {
            validatePasswordMatch(this, passwordInput);
        });
        
        // Form submission validation
        registrationForm.addEventListener('submit', function(event) {
            let isValid = true;
            
            if (!validateUsername(usernameInput)) isValid = false;
            if (!validateEmail(emailInput)) isValid = false;
            if (!validatePassword(passwordInput)) isValid = false;
            if (!validatePasswordMatch(confirmPasswordInput, passwordInput)) isValid = false;
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
    
    // Investment form validation
    const investmentForm = document.getElementById('investment-form');
    if (investmentForm) {
        const amountInput = document.getElementById('amount');
        
        amountInput.addEventListener('input', function() {
            validateInvestmentAmount(this);
        });
        
        investmentForm.addEventListener('submit', function(event) {
            if (!validateInvestmentAmount(amountInput)) {
                event.preventDefault();
            }
        });
    }
    
    // Project form validation
    const projectForm = document.getElementById('project-form');
    if (projectForm) {
        const fundingGoalInput = document.getElementById('funding_goal');
        const durationInput = document.getElementById('duration_months');
        const roiInput = document.getElementById('expected_roi');
        
        fundingGoalInput.addEventListener('input', function() {
            validateNumber(this, 1, 1000000000, 'Funding goal must be a positive number');
        });
        
        durationInput.addEventListener('input', function() {
            validateNumber(this, 1, 60, 'Duration must be between 1 and 60 months');
        });
        
        roiInput.addEventListener('input', function() {
            validateNumber(this, 0, 100, 'ROI must be between 0 and 100%');
        });
        
        projectForm.addEventListener('submit', function(event) {
            let isValid = true;
            
            if (!validateNumber(fundingGoalInput, 1, 1000000000, 'Funding goal must be a positive number')) isValid = false;
            if (!validateNumber(durationInput, 1, 60, 'Duration must be between 1 and 60 months')) isValid = false;
            if (!validateNumber(roiInput, 0, 100, 'ROI must be between 0 and 100%')) isValid = false;
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
    
    // Contact form validation
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        const nameInput = document.getElementById('name');
        const emailInput = document.getElementById('email');
        const subjectInput = document.getElementById('subject');
        const messageInput = document.getElementById('message');
        
        nameInput.addEventListener('blur', function() {
            validateRequired(this, 'Name is required');
        });
        
        emailInput.addEventListener('blur', function() {
            validateEmail(this);
        });
        
        subjectInput.addEventListener('blur', function() {
            validateRequired(this, 'Subject is required');
        });
        
        messageInput.addEventListener('blur', function() {
            validateRequired(this, 'Message is required');
        });
        
        contactForm.addEventListener('submit', function(event) {
            let isValid = true;
            
            if (!validateRequired(nameInput, 'Name is required')) isValid = false;
            if (!validateEmail(emailInput)) isValid = false;
            if (!validateRequired(subjectInput, 'Subject is required')) isValid = false;
            if (!validateRequired(messageInput, 'Message is required')) isValid = false;
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
    
    // Validation helper functions
    function validateUsername(input) {
        const value = input.value.trim();
        const minLength = 3;
        const maxLength = 25;
        
        if (value === '') {
            setInvalid(input, 'Username is required');
            return false;
        } else if (value.length < minLength) {
            setInvalid(input, `Username must be at least ${minLength} characters`);
            return false;
        } else if (value.length > maxLength) {
            setInvalid(input, `Username must be less than ${maxLength} characters`);
            return false;
        } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            setInvalid(input, 'Username can only contain letters, numbers, and underscores');
            return false;
        } else {
            setValid(input);
            return true;
        }
    }
    
    function validateEmail(input) {
        const value = input.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (value === '') {
            setInvalid(input, 'Email is required');
            return false;
        } else if (!emailRegex.test(value)) {
            setInvalid(input, 'Please enter a valid email address');
            return false;
        } else {
            setValid(input);
            return true;
        }
    }
    
    function validatePassword(input) {
        const value = input.value;
        const minLength = 8;
        
        if (value === '') {
            setInvalid(input, 'Password is required');
            return false;
        } else if (value.length < minLength) {
            setInvalid(input, `Password must be at least ${minLength} characters`);
            return false;
        } else {
            setValid(input);
            return true;
        }
    }
    
    function validatePasswordMatch(confirmInput, passwordInput) {
        const confirmValue = confirmInput.value;
        const passwordValue = passwordInput.value;
        
        if (confirmValue === '') {
            setInvalid(confirmInput, 'Please confirm your password');
            return false;
        } else if (confirmValue !== passwordValue) {
            setInvalid(confirmInput, 'Passwords do not match');
            return false;
        } else {
            setValid(confirmInput);
            return true;
        }
    }
    
    function validateInvestmentAmount(input) {
        const value = parseFloat(input.value);
        
        if (isNaN(value) || value <= 0) {
            setInvalid(input, 'Please enter a valid investment amount');
            return false;
        } else {
            setValid(input);
            return true;
        }
    }
    
    function validateNumber(input, min, max, errorMessage) {
        const value = parseFloat(input.value);
        
        if (isNaN(value) || value < min || value > max) {
            setInvalid(input, errorMessage);
            return false;
        } else {
            setValid(input);
            return true;
        }
    }
    
    function validateRequired(input, errorMessage) {
        const value = input.value.trim();
        
        if (value === '') {
            setInvalid(input, errorMessage);
            return false;
        } else {
            setValid(input);
            return true;
        }
    }
    
    function setInvalid(input, message) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        
        const feedbackElement = input.nextElementSibling;
        if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
            feedbackElement.textContent = message;
        } else {
            const feedback = document.createElement('div');
            feedback.classList.add('invalid-feedback');
            feedback.textContent = message;
            input.parentNode.insertBefore(feedback, input.nextSibling);
        }
    }
    
    function setValid(input) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        
        const feedbackElement = input.nextElementSibling;
        if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
            feedbackElement.textContent = '';
        }
    }
});
