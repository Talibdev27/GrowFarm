document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Project category filter
    const categorySelect = document.getElementById('category-filter');
    const riskSelect = document.getElementById('risk-filter');
    
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            applyFilters();
        });
    }
    
    if (riskSelect) {
        riskSelect.addEventListener('change', function() {
            applyFilters();
        });
    }
    
    function applyFilters() {
        let url = new URL(window.location.href);
        const params = new URLSearchParams(url.search);
        
        const categoryValue = categorySelect ? categorySelect.value : null;
        const riskValue = riskSelect ? riskSelect.value : null;
        
        if (categoryValue) {
            params.set('category', categoryValue);
        } else {
            params.delete('category');
        }
        
        if (riskValue) {
            params.set('risk', riskValue);
        } else {
            params.delete('risk');
        }
        
        // Reset to page 1 when filtering
        params.set('page', '1');
        
        url.search = params.toString();
        window.location.href = url.toString();
    }

    // Project funding progress animation
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(progressBar) {
        const width = progressBar.getAttribute('aria-valuenow') + '%';
        progressBar.style.width = '0%';
        setTimeout(function() {
            progressBar.style.width = width;
        }, 100);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Message status update
    const messageItems = document.querySelectorAll('.message-item');
    messageItems.forEach(function(item) {
        item.addEventListener('click', function() {
            const messageId = this.getAttribute('data-message-id');
            if (messageId && this.classList.contains('unread')) {
                fetch(`/mark_read/${messageId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }).then(response => {
                    if (response.ok) {
                        this.classList.remove('unread');
                    }
                });
            }
        });
    });

    // Investment modal auto-focus
    const investmentModal = document.getElementById('investmentModal');
    if (investmentModal) {
        investmentModal.addEventListener('shown.bs.modal', function() {
            document.getElementById('amount').focus();
        });
    }

    // Hero section parallax effect
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', function() {
            const scrollPosition = window.scrollY;
            hero.style.backgroundPositionY = 50 - (scrollPosition * 0.1) + '%';
        });
    }

    // Animate elements on scroll
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    function checkIfInView() {
        const windowHeight = window.innerHeight;
        const windowTopPosition = window.scrollY;
        const windowBottomPosition = windowTopPosition + windowHeight;
        
        animateElements.forEach(function(element) {
            const elementHeight = element.offsetHeight;
            const elementTopPosition = element.offsetTop;
            const elementBottomPosition = elementTopPosition + elementHeight;
            
            // Check if element is in view
            if (
                elementBottomPosition >= windowTopPosition &&
                elementTopPosition <= windowBottomPosition
            ) {
                element.classList.add('animated');
            }
        });
    }
    
    window.addEventListener('scroll', checkIfInView);
    window.addEventListener('resize', checkIfInView);
    checkIfInView();
});
