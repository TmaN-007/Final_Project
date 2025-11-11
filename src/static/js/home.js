/**
 * Campus Resource Hub - Dashboard JavaScript
 * Handles theme toggle and account dropdown
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
// Account Dropdown
// ============================================================
function toggleAccountMenu() {
    const dropdown = document.querySelector('.account-dropdown');
    dropdown.classList.toggle('active');
}

// Close dropdown when clicking outside
document.addEventListener('click', (event) => {
    const dropdown = document.querySelector('.account-dropdown');
    const accountButton = document.querySelector('.account-button');

    if (dropdown && !dropdown.contains(event.target)) {
        dropdown.classList.remove('active');
    }
});

// Prevent dropdown from closing when clicking inside
document.addEventListener('DOMContentLoaded', () => {
    const accountMenu = document.getElementById('accountMenu');
    if (accountMenu) {
        accountMenu.addEventListener('click', (event) => {
            // Allow links to work but prevent menu from toggling
            if (event.target.tagName === 'A') {
                return;
            }
            event.stopPropagation();
        });
    }
});

// ============================================================
// Initialize on DOM Load
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    loadTheme();

    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Slide out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ============================================================
// Category Carousel Animations
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    const categoryBoxes = document.querySelectorAll('.category-box');
    let currentHoveredBox = null;

    categoryBoxes.forEach((box) => {
        box.addEventListener('mouseenter', function() {
            // If hovering the same box, ignore
            if (currentHoveredBox === this) return;

            // Clean up previous hover if exists
            if (currentHoveredBox) {
                const prevDetails = currentHoveredBox.querySelector('.category-details');
                const prevIcon = currentHoveredBox.querySelector('.category-icon');
                const prevTitle = currentHoveredBox.querySelector('.category-name');

                // Remove anime.js animations
                anime.remove([prevDetails, prevIcon, prevTitle]);

                // Reset previous box immediately
                prevDetails.style.display = 'none';
                prevDetails.style.opacity = '0';
                prevDetails.classList.remove('show');
                anime.set([prevIcon, prevTitle], {
                    translateY: 0,
                    scale: 1
                });
            }

            currentHoveredBox = this;
            const allBoxes = Array.from(categoryBoxes);
            const hoveredIndex = allBoxes.indexOf(this);
            const details = this.querySelector('.category-details');
            const icon = this.querySelector('.category-icon');
            const title = this.querySelector('.category-name');

            // Remove any existing animations on current box
            anime.remove([this, icon, title, details]);

            // Expand width horizontally only (other boxes shrink simultaneously)
            anime({
                targets: this,
                width: '340px',
                maxWidth: '340px',
                minWidth: '340px',
                duration: 500,
                easing: 'easeOutCubic'
            });

            // Move icon and title up and scale them down slightly
            anime({
                targets: [icon, title],
                translateY: [0, -8],
                scale: [1, 0.92],
                duration: 500,
                easing: 'easeOutCubic'
            });

            // Shrink other boxes simultaneously
            allBoxes.forEach((otherBox, otherIndex) => {
                if (otherIndex !== hoveredIndex) {
                    anime.remove(otherBox);
                    anime({
                        targets: otherBox,
                        width: '130px',
                        maxWidth: '130px',
                        minWidth: '130px',
                        duration: 500,
                        easing: 'easeOutCubic'
                    });
                }
            });

            // After 300ms (during expansion), start showing details with smooth fade
            setTimeout(() => {
                // Check if still hovering this box
                if (currentHoveredBox !== this) return;

                details.style.display = 'block';
                details.classList.add('show');
                anime({
                    targets: details,
                    opacity: [0, 1],
                    translateY: [10, 0],
                    duration: 350,
                    easing: 'easeOutCubic'
                });
            }, 300);
        });

        box.addEventListener('mouseleave', function() {
            if (currentHoveredBox !== this) return;

            currentHoveredBox = null;
            const details = this.querySelector('.category-details');
            const icon = this.querySelector('.category-icon');
            const title = this.querySelector('.category-name');

            // Remove existing animations
            anime.remove([details, icon, title]);

            // Immediately hide details to prevent squishing during box shrink
            details.style.opacity = '0';
            details.style.display = 'none';
            details.classList.remove('show');

            // Reset icon and title position and scale
            anime({
                targets: [icon, title],
                translateY: [-8, 0],
                scale: [0.92, 1],
                duration: 500,
                easing: 'easeOutCubic'
            });

            // Reset all widths smoothly
            anime.remove(categoryBoxes);
            anime({
                targets: categoryBoxes,
                width: '180px',
                maxWidth: '180px',
                minWidth: '180px',
                duration: 500,
                easing: 'easeOutCubic'
            });
        });
    });
});
