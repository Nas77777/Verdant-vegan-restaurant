document.addEventListener('DOMContentLoaded', function() {
    const mobileMenu = document.querySelector('.mobile-menu');
    const navLinks = document.querySelector('.nav-links');
    const navbar = document.querySelector('.navbar');
    let isMenuOpen = false;

    mobileMenu.addEventListener('click', function() {
        isMenuOpen = !isMenuOpen;
        mobileMenu.innerHTML = isMenuOpen ? 
            '<i class="fas fa-times"></i>' : 
            '<i class="fas fa-bars"></i>';
        
        navLinks.classList.toggle('nav-active');
        document.body.style.overflow = isMenuOpen ? 'hidden' : 'auto';
    });

    // Close menu when user clicks a link outside
    document.addEventListener('click', function(event) {
        if (isMenuOpen && !navbar.contains(event.target)) {
            isMenuOpen = false;
            mobileMenu.innerHTML = '<i class="fas fa-bars"></i>';
            navLinks.classList.remove('nav-active');
            document.body.style.overflow = 'auto';
        }
    });

    // closing the menu when the usder clicks a link in the menu 
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', function() {
            if (isMenuOpen) {
                isMenuOpen = false;
                mobileMenu.innerHTML = '<i class="fas fa-bars"></i>';
                navLinks.classList.remove('nav-active');
                document.body.style.overflow = 'auto';
            }
        });
    });

    const featuredProducts = [...document.querySelectorAll('.products-slider')];
    const nextBtn = [...document.querySelectorAll('.next-btn')];
    const prevBtn = [...document.querySelectorAll('.prev-btn')];

    featuredProducts.forEach((item, i) => {
        let containerDimension = item.getBoundingClientRect();
        let containerWidth = containerDimension.width;

        nextBtn[i].addEventListener('click', () => item.scrollLeft += containerWidth);
        prevBtn[i].addEventListener('click', () => item.scrollLeft -= containerWidth);
    });

    // Scroll Animation for the timeline section
    function handleScrollAnimation() {
        const items = document.querySelectorAll('.timeline-item');
        const screenWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        if (screenWidth < 768) {

            items.forEach(item => item.classList.add('animate'));
            return;
        }


        items.forEach(item => {
            const rect = item.getBoundingClientRect();
            if (rect.top <= windowHeight * 0.75) {
                item.classList.add('animate');
            }
        });
    }


    let scrollTimeout;
    function throttleScroll() {
        if (scrollTimeout) return;
        scrollTimeout = setTimeout(() => {
            handleScrollAnimation();
            scrollTimeout = null;
        }, 100);
    }

    function initScrollAnimation() {
        const screenWidth = window.innerWidth;

        if (screenWidth >= 768) {
            document.addEventListener('scroll', throttleScroll);
        } else {
            document.querySelectorAll('.timeline-item').forEach(item => item.classList.add('animate'));
        }
    }

    initScrollAnimation();


    window.addEventListener('resize', initScrollAnimation);
});
