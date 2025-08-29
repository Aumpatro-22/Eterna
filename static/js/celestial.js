// Celestial Serenity Theme Interactions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements with fade-in effect
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach((el, i) => {
        setTimeout(() => {
            el.style.opacity = '1';
        }, 100 * i);
    });
    
    // Generate starfield background
    createStarField();
    
    // Initialize form fields with celestial styles
    enhanceFormFields();
});

// Create a dynamic starfield in the background
function createStarField() {
    // Avoid duplicate starfields
    if (document.querySelector('.star-field')) return;

    const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const starField = document.createElement('div');
    starField.className = 'star-field';
    starField.style.cssText = `
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1; pointer-events: none; opacity: 0.7;
    `;

    // Adaptive star count
    let numberOfStars = 100;
    if (window.innerWidth < 640) numberOfStars = 45;
    else if (window.innerWidth < 1024) numberOfStars = 70;
    if (prefersReduced) numberOfStars = Math.floor(numberOfStars * 0.6);

    for (let i = 0; i < numberOfStars; i++) {
        const star = document.createElement('div');

        const x = Math.random() * 100;
        const y = Math.random() * 100;

        const size = Math.random() * 1.8 + 0.6;
        const opacity = Math.random() * 0.4 + 0.25;

        star.style.cssText = `
            position: absolute;
            top: ${y}%;
            left: ${x}%;
            width: ${size}px; height: ${size}px;
            background-color: rgba(255, 255, 255, ${opacity});
            border-radius: 50%;
            box-shadow: 0 0 ${size * 2}px rgba(255, 255, 255, 0.8);
            ${prefersReduced ? '' : `animation: twinkle ${Math.random() * 5 + 3}s infinite alternate;`}
        `;

        starField.appendChild(star);
    }

    document.body.appendChild(starField);
}

// Enhanced form interactions
function enhanceFormFields() {
    // Add celestial styling to all form elements
    const inputs = document.querySelectorAll('input:not([type="checkbox"]):not([type="radio"]), textarea, select');
    
    inputs.forEach(input => {
        // Add focus effects
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('input-focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('input-focused');
        });
    });

    // Add subtle label animation
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        const input = group.querySelector('input, textarea, select');
        const label = group.querySelector('label');
        
        if (input && label) {
            input.addEventListener('focus', () => {
                label.classList.add('label-focused');
            });
            
            input.addEventListener('blur', () => {
                if (input.value === '') {
                    label.classList.remove('label-focused');
                }
            });
            
            // Initialize if input has value
            if (input.value !== '') {
                label.classList.add('label-focused');
            }
        }
    });
}

// Toggle between constellation and standard view
function toggleView() {
    const standardView = document.getElementById('standard-view');
    const constellationView = document.getElementById('constellation-view');
    const toggleButton = document.getElementById('view-toggle');
    
    if (standardView && constellationView && toggleButton) {
        if (constellationView.classList.contains('hidden')) {
            standardView.classList.add('hidden');
            constellationView.classList.remove('hidden');
            toggleButton.innerHTML = '<i class="fas fa-th-large mr-2"></i> Standard View';
            
            // Initialize constellation view
            initConstellationView(constellationView);
        } else {
            standardView.classList.remove('hidden');
            constellationView.classList.add('hidden');
            toggleButton.innerHTML = '<i class="fas fa-stars mr-2"></i> Constellation View';
        }
    }
}

// Transform memorial cards into interactive constellation
function initConstellationView(container) {
    // Clear previous stars if any
    container.innerHTML = '';
    
    // Get all memorial data
    const memorials = document.querySelectorAll('.memorial-data');
    
    // Position memorials randomly in the container
    memorials.forEach(memorial => {
        const id = memorial.getAttribute('data-id');
        const name = memorial.getAttribute('data-name');
        const url = memorial.getAttribute('data-url');
        const year = memorial.getAttribute('data-year') || '';
        
        // Create star element
        const star = document.createElement('a');
        star.href = url;
        star.classList.add('memorial-star');
        
        // Random position (avoid edges)
        const x = 10 + Math.random() * 80; // 10% to 90% width
        const y = 10 + Math.random() * 80; // 10% to 90% height
        
        star.style.cssText = `
            position: absolute;
            left: ${x}%;
            top: ${y}%;
            width: 12px;
            height: 12px;
            background: rgba(212, 175, 55, 0.8);
            border-radius: 50%;
            box-shadow: 0 0 10px rgba(212, 175, 55, 0.6);
            transform: scale(1);
            transition: all 0.3s ease;
        `;
        
        // Create tooltip
        const tooltip = document.createElement('div');
        tooltip.classList.add('tooltip');
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(18, 23, 56, 0.9);
            padding: 8px 15px;
            border-radius: 8px;
            color: #fffff0;
            width: 150px;
            left: 50%;
            transform: translateX(-50%) translateY(15px);
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s ease;
            z-index: 10;
            border: 1px solid rgba(212, 175, 55, 0.3);
        `;
        tooltip.innerHTML = `${name}${year ? `<br><span style="font-size: 0.8rem; color: #e6e6fa;">${year}</span>` : ''}`;
        
        star.appendChild(tooltip);
        
        // Hover effects
        star.addEventListener('mouseenter', () => {
            star.style.transform = 'scale(1.8)';
            star.style.boxShadow = '0 0 20px rgba(212, 175, 55, 0.9)';
            tooltip.style.opacity = '1';
            tooltip.style.transform = 'translateX(-50%) translateY(10px)';
        });
        
        star.addEventListener('mouseleave', () => {
            star.style.transform = 'scale(1)';
            star.style.boxShadow = '0 0 10px rgba(212, 175, 55, 0.6)';
            tooltip.style.opacity = '0';
            tooltip.style.transform = 'translateX(-50%) translateY(15px)';
        });
        
        container.appendChild(star);
    });
}
