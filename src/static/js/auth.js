/**
 * Campus Resource Hub - Authentication Pages JavaScript
 * Shared JS for login and register pages
 */

// ============================================================
// Theme Toggle
// ============================================================
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Load saved theme on page load
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

// ============================================================
// Password Visibility Toggle
// ============================================================
function togglePassword() {
    const passwordInput = document.getElementById('password');
    if (!passwordInput) return;

    const wrapper = passwordInput.closest('.password-input-wrapper');
    if (!wrapper) return;

    const toggle = wrapper.querySelector('.password-toggle');
    if (!toggle) return;

    if (passwordInput.type === 'password') {
        // Show password - change to eye WITHOUT slash
        passwordInput.type = 'text';
        toggle.innerHTML = `
            <g clip-path="url(#clip_eye_open_login)">
                <path d="M4.5 6.75C3.46447 6.75 2.625 5.91053 2.625 4.875C2.625 3.83947 3.46447 3 4.5 3C5.53553 3 6.375 3.83947 6.375 4.875C6.375 5.91053 5.53553 6.75 4.5 6.75Z" stroke="white" stroke-opacity="0.72" stroke-width="0.5625" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M4.5 8.0625C6.5625 8.0625 8.25 6.5625 8.625 4.875C8.25 3.1875 6.5625 1.6875 4.5 1.6875C2.4375 1.6875 0.75 3.1875 0.375 4.875C0.75 6.5625 2.4375 8.0625 4.5 8.0625Z" stroke="white" stroke-opacity="0.72" stroke-width="0.5625" stroke-linecap="round" stroke-linejoin="round"/>
            </g>
            <defs>
                <clipPath id="clip_eye_open_login">
                    <rect width="9" height="9" fill="white"/>
                </clipPath>
            </defs>
        `;
    } else {
        // Hide password - change to eye WITH slash
        passwordInput.type = 'password';
        toggle.innerHTML = `
            <g clip-path="url(#clip_eye_closed_login)">
                <path d="M1.48863 3.07526C1.13877 3.48818 0.878258 3.9691 0.723508 4.4877C1.20666 6.10993 2.70923 7.29239 4.48777 7.29239C4.85911 7.29239 5.21811 7.24078 5.55842 7.14468M2.32929 2.32921C2.96974 1.90659 3.72044 1.68185 4.48777 1.68301C6.26632 1.68301 7.76851 2.86547 8.25166 4.48695C7.98689 5.37299 7.4185 6.13746 6.64626 6.64619M2.32929 2.32921L1.12215 1.12208M2.32929 2.32921L3.69423 3.69416M6.64626 6.64619L7.8534 7.85333M6.64626 6.64619L5.28131 5.28124C5.3855 5.17706 5.46814 5.05337 5.52452 4.91725C5.58091 4.78112 5.60993 4.63523 5.60993 4.48789C5.60993 4.34055 5.58091 4.19465 5.52452 4.05853C5.46814 3.92241 5.3855 3.79872 5.28131 3.69454C5.17713 3.59035 5.05344 3.50771 4.91732 3.45132C4.7812 3.39494 4.6353 3.36592 4.48796 3.36592C4.34062 3.36592 4.19472 3.39494 4.0586 3.45132C3.92248 3.50771 3.79879 3.59035 3.69461 3.69454M5.28094 5.28087L3.69498 3.69491" stroke="white" stroke-opacity="0.72" stroke-width="0.560937" stroke-linecap="round" stroke-linejoin="round"/>
            </g>
            <defs>
                <clipPath id="clip_eye_closed_login">
                    <rect fill="white" width="8.975" height="8.975"/>
                </clipPath>
            </defs>
        `;
    }
}

// Password visibility toggle for specific field by ID
function togglePasswordField(fieldId) {
    const passwordInput = document.getElementById(fieldId);
    if (!passwordInput) return;

    const wrapper = passwordInput.closest('.password-input-wrapper');
    if (!wrapper) return;

    const toggle = wrapper.querySelector('.password-toggle');
    if (!toggle) return;

    if (passwordInput.type === 'password') {
        // Show password - change to eye WITHOUT slash
        passwordInput.type = 'text';
        toggle.innerHTML = `
            <g clip-path="url(#clip_eye_open_${fieldId})">
                <path d="M4.5 6.75C3.46447 6.75 2.625 5.91053 2.625 4.875C2.625 3.83947 3.46447 3 4.5 3C5.53553 3 6.375 3.83947 6.375 4.875C6.375 5.91053 5.53553 6.75 4.5 6.75Z" stroke="white" stroke-opacity="0.72" stroke-width="0.5625" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M4.5 8.0625C6.5625 8.0625 8.25 6.5625 8.625 4.875C8.25 3.1875 6.5625 1.6875 4.5 1.6875C2.4375 1.6875 0.75 3.1875 0.375 4.875C0.75 6.5625 2.4375 8.0625 4.5 8.0625Z" stroke="white" stroke-opacity="0.72" stroke-width="0.5625" stroke-linecap="round" stroke-linejoin="round"/>
            </g>
            <defs>
                <clipPath id="clip_eye_open_${fieldId}">
                    <rect width="9" height="9" fill="white"/>
                </clipPath>
            </defs>
        `;
    } else {
        // Hide password - change to eye WITH slash
        passwordInput.type = 'password';
        toggle.innerHTML = `
            <g clip-path="url(#clip_eye_closed_${fieldId})">
                <path d="M1.48863 3.07526C1.13877 3.48818 0.878258 3.9691 0.723508 4.4877C1.20666 6.10993 2.70923 7.29239 4.48777 7.29239C4.85911 7.29239 5.21811 7.24078 5.55842 7.14468M2.32929 2.32921C2.96974 1.90659 3.72044 1.68185 4.48777 1.68301C6.26632 1.68301 7.76851 2.86547 8.25166 4.48695C7.98689 5.37299 7.4185 6.13746 6.64626 6.64619M2.32929 2.32921L1.12215 1.12208M2.32929 2.32921L3.69423 3.69416M6.64626 6.64619L7.8534 7.85333M6.64626 6.64619L5.28131 5.28124C5.3855 5.17706 5.46814 5.05337 5.52452 4.91725C5.58091 4.78112 5.60993 4.63523 5.60993 4.48789C5.60993 4.34055 5.58091 4.19465 5.52452 4.05853C5.46814 3.92241 5.3855 3.79872 5.28131 3.69454C5.17713 3.59035 5.05344 3.50771 4.91732 3.45132C4.7812 3.39494 4.6353 3.36592 4.48796 3.36592C4.34062 3.36592 4.19472 3.39494 4.0586 3.45132C3.92248 3.50771 3.79879 3.59035 3.69461 3.69454M5.28094 5.28087L3.69498 3.69491" stroke="white" stroke-opacity="0.72" stroke-width="0.560937" stroke-linecap="round" stroke-linejoin="round"/>
            </g>
            <defs>
                <clipPath id="clip_eye_closed_${fieldId}">
                    <rect fill="white" width="8.975" height="8.975"/>
                </clipPath>
            </defs>
        `;
    }
}

// ============================================================
// Form Submission Handler (for login)
// ============================================================
function handleSignIn() {
    const email = document.getElementById('email');
    const password = document.getElementById('password');

    if (!email || !password) return;

    if (!email.value || !password.value) {
        alert('Please fill in all fields');
        return;
    }

    // Form will be submitted via the form's action attribute
    // This function is here for additional client-side validation if needed
    document.querySelector('form').submit();
}

// ============================================================
// Enter Key Handler
// ============================================================
function setupEnterKeyHandlers() {
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    if (emailInput) {
        emailInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                const form = this.closest('form');
                if (form) form.submit();
            }
        });
    }

    if (passwordInput) {
        passwordInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                const form = this.closest('form');
                if (form) form.submit();
            }
        });
    }
}

// ============================================================
// Initialize on DOM Load
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    loadTheme();
    setupEnterKeyHandlers();
});
