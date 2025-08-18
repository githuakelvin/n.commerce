// Kenya Commerce - Main JavaScript File

$(document).ready(function () {
    'use strict';

    // Initialize all components
    initBackToTop();
    initSmoothScrolling();
    initProductImageZoom();
    initQuantityInputs();
    initFormValidation();
    initSearchAutocomplete();
    initMobileMenu();
    initLazyLoading();
    initScrollAnimations();

    // Back to Top Button
    function initBackToTop() {
        const backToTopBtn = $('#backToTop');

        $(window).scroll(function () {
            if ($(this).scrollTop() > 300) {
                backToTopBtn.addClass('show');
            } else {
                backToTopBtn.removeClass('show');
            }
        });

        backToTopBtn.click(function () {
            $('html, body').animate({
                scrollTop: 0
            }, 800);
        });
    }

    // Smooth Scrolling for Anchor Links
    function initSmoothScrolling() {
        $('a[href^="#"]').click(function (e) {
            e.preventDefault();

            const target = $(this.getAttribute('href'));
            if (target.length) {
                $('html, body').animate({
                    scrollTop: target.offset().top - 80
                }, 800);
            }
        });
    }

    // Product Image Zoom Effect
    function initProductImageZoom() {
        $('.product-image').hover(
            function () {
                $(this).find('img').css('transform', 'scale(1.1)');
            },
            function () {
                $(this).find('img').css('transform', 'scale(1)');
            }
        );
    }

    // Quantity Input Controls
    function initQuantityInputs() {
        $('.quantity-control').each(function () {
            const $input = $(this).find('.quantity-input');
            const $decrease = $(this).find('.quantity-decrease');
            const $increase = $(this).find('.quantity-increase');

            $decrease.click(function () {
                let currentVal = parseInt($input.val());
                if (currentVal > 1) {
                    $input.val(currentVal - 1);
                    updateCartItemQuantity($input);
                }
            });

            $increase.click(function () {
                let currentVal = parseInt($input.val());
                $input.val(currentVal + 1);
                updateCartItemQuantity($input);
            });

            $input.on('change', function () {
                updateCartItemQuantity($(this));
            });
        });
    }

    // Update Cart Item Quantity
    function updateCartItemQuantity($input) {
        const itemId = $input.data('item-id');
        const quantity = $input.val();

        $.ajax({
            url: `/products/cart/update/${itemId}/`,
            method: 'POST',
            data: {
                quantity: quantity,
                csrfmiddlewaretoken: getCookie('csrftoken')
            },
            success: function (response) {
                if (response.success) {
                    updateCartTotals(response);
                    showAlert('Success', 'Cart updated successfully!', 'success');
                } else {
                    showAlert('Error', response.message || 'Failed to update cart', 'error');
                    // Reset to previous value
                    $input.val(response.previous_quantity || 1);
                }
            },
            error: function () {
                showAlert('Error', 'Failed to update cart', 'error');
            }
        });
    }

    // Form Validation
    function initFormValidation() {
        $('form').each(function () {
            $(this).on('submit', function (e) {
                if (!validateForm($(this))) {
                    e.preventDefault();
                    return false;
                }
            });
        });
    }

    // Validate Form Fields
    function validateForm($form) {
        let isValid = true;

        $form.find('[required]').each(function () {
            const $field = $(this);
            const value = $field.val().trim();

            if (!value) {
                showFieldError($field, 'This field is required');
                isValid = false;
            } else {
                clearFieldError($field);
            }

            // Email validation
            if ($field.attr('type') === 'email' && value) {
                if (!isValidEmail(value)) {
                    showFieldError($field, 'Please enter a valid email address');
                    isValid = false;
                }
            }

            // Phone validation
            if ($field.hasClass('phone-input') && value) {
                if (!isValidPhone(value)) {
                    showFieldError($field, 'Please enter a valid phone number');
                    isValid = false;
                }
            }
        });

        return isValid;
    }

    // Show Field Error
    function showFieldError($field, message) {
        clearFieldError($field);

        $field.addClass('is-invalid');
        $field.after(`<div class="invalid-feedback">${message}</div>`);
    }

    // Clear Field Error
    function clearFieldError($field) {
        $field.removeClass('is-invalid');
        $field.siblings('.invalid-feedback').remove();
    }

    // Email Validation
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Phone Validation
    function isValidPhone(phone) {
        const phoneRegex = /^(\+?254|0)?[17]\d{8}$/;
        return phoneRegex.test(phone);
    }

    // Search Autocomplete
    function initSearchAutocomplete() {
        $('.search-input').each(function () {
            const $input = $(this);
            const $suggestions = $('<div class="search-suggestions"></div>');

            $input.after($suggestions);

            $input.on('input', function () {
                const query = $(this).val().trim();

                if (query.length < 2) {
                    $suggestions.hide();
                    return;
                }

                // Debounce search
                clearTimeout($input.data('searchTimeout'));
                $input.data('searchTimeout', setTimeout(function () {
                    performSearch(query, $suggestions);
                }, 300));
            });

            // Hide suggestions when clicking outside
            $(document).on('click', function (e) {
                if (!$(e.target).closest('.search-input, .search-suggestions').length) {
                    $suggestions.hide();
                }
            });
        });
    }

    // Perform Search
    function performSearch(query, $suggestions) {
        $.ajax({
            url: '/products/api/search/',
            method: 'GET',
            data: { q: query, limit: 5 },
            success: function (response) {
                if (response.results && response.results.length > 0) {
                    displaySearchSuggestions(response.results, $suggestions);
                } else {
                    $suggestions.html('<div class="no-results">No products found</div>');
                }
                $suggestions.show();
            },
            error: function () {
                $suggestions.html('<div class="error">Search failed</div>');
                $suggestions.show();
            }
        });
    }

    // Display Search Suggestions
    function displaySearchSuggestions(results, $suggestions) {
        let html = '';

        results.forEach(function (product) {
            html += `
                <div class="suggestion-item" data-product-id="${product.id}">
                    <div class="suggestion-image">
                        <img src="${product.image || '/static/images/placeholder.png'}" alt="${product.name}">
                    </div>
                    <div class="suggestion-content">
                        <div class="suggestion-name">${product.name}</div>
                        <div class="suggestion-price">KES ${product.price}</div>
                    </div>
                </div>
            `;
        });

        $suggestions.html(html);

        // Handle suggestion clicks
        $suggestions.find('.suggestion-item').click(function () {
            const productId = $(this).data('product-id');
            window.location.href = `/products/product/${productId}/`;
        });
    }

    // Mobile Menu Toggle
    function initMobileMenu() {
        $('.navbar-toggler').click(function () {
            const $navbar = $(this).closest('.navbar');
            $navbar.toggleClass('expanded');
        });

        // Close mobile menu when clicking on a link
        $('.navbar-nav .nav-link').click(function () {
            if ($(window).width() < 992) {
                $('.navbar-collapse').collapse('hide');
            }
        });
    }

    // Lazy Loading for Images
    function initLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    // Scroll Animations
    function initScrollAnimations() {
        if ('IntersectionObserver' in window) {
            const animationObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate');
                    }
                });
            }, {
                threshold: 0.1
            });

            document.querySelectorAll('.animate-on-scroll').forEach(el => {
                animationObserver.observe(el);
            });
        }
    }

    // Add to Cart Animation
    function animateAddToCart($button) {
        $button.addClass('adding');

        setTimeout(() => {
            $button.removeClass('adding');
            $button.addClass('added');

            setTimeout(() => {
                $button.removeClass('added');
            }, 2000);
        }, 1000);
    }

    // Update Cart Totals
    function updateCartTotals(data) {
        if (data.cart_items_count !== undefined) {
            $('.cart-count').text(data.cart_items_count);
        }

        if (data.cart_total !== undefined) {
            $('.cart-total').text(`KES ${data.cart_total.toFixed(2)}`);
        }

        if (data.subtotal !== undefined) {
            $('.subtotal').text(`KES ${data.subtotal.toFixed(2)}`);
        }

        if (data.total !== undefined) {
            $('.total').text(`KES ${data.total.toFixed(2)}`);
        }
    }

    // Show Alert Message
    function showAlert(title, message, type = 'info') {
        const alertClass = `alert-${type}`;
        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                <strong>${title}:</strong> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // Remove existing alerts
        $('.alert').remove();

        // Add new alert
        $('.main-content').prepend(alertHtml);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            $('.alert').fadeOut();
        }, 5000);
    }

    // Get Cookie Value
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Currency Formatter
    function formatCurrency(amount, currency = 'KES') {
        return `${currency} ${parseFloat(amount).toLocaleString('en-KE', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}`;
    }

    // Number Formatter
    function formatNumber(number) {
        return parseInt(number).toLocaleString('en-KE');
    }

    // Date Formatter
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-KE', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    // Debounce Function
    function debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction() {
            const context = this;
            const args = arguments;
            const later = function () {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    }

    // Throttle Function
    function throttle(func, limit) {
        let inThrottle;
        return function () {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Local Storage Helper
    const Storage = {
        set: function (key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.error('Error saving to localStorage:', e);
            }
        },

        get: function (key) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : null;
            } catch (e) {
                console.error('Error reading from localStorage:', e);
                return null;
            }
        },

        remove: function (key) {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                console.error('Error removing from localStorage:', e);
            }
        }
    };

    // Session Storage Helper
    const SessionStorage = {
        set: function (key, value) {
            try {
                sessionStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.error('Error saving to sessionStorage:', e);
            }
        },

        get: function (key) {
            try {
                const item = sessionStorage.getItem(key);
                return item ? JSON.parse(item) : null;
            } catch (e) {
                console.error('Error reading from sessionStorage:', e);
                return null;
            }
        },

        remove: function (key) {
            try {
                sessionStorage.removeItem(key);
            } catch (e) {
                console.error('Error removing from sessionStorage:', e);
            }
        }
    };

    // Utility Functions
    window.KenyaCommerce = {
        formatCurrency: formatCurrency,
        formatNumber: formatNumber,
        formatDate: formatDate,
        showAlert: showAlert,
        Storage: Storage,
        SessionStorage: SessionStorage
    };

    // Console welcome message
    console.log('%c🇰🇪 Welcome to Kenya Commerce! 🇰🇪', 'color: #007bff; font-size: 20px; font-weight: bold;');
    console.log('%cBuilt with ❤️ for the Kenyan market', 'color: #28a745; font-size: 14px;');
});


