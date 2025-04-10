document.addEventListener('DOMContentLoaded', function() {
    const mobileMenu = document.querySelector('.mobile-menu');
    const navLinks = document.querySelector('.nav-links');
    const navbar = document.querySelector('.navbar');
    let isMenuOpen = false;

    // Toggle menu function
    mobileMenu.addEventListener('click', function() {
        isMenuOpen = !isMenuOpen;
        mobileMenu.innerHTML = isMenuOpen ? 
            '<i class="fas fa-times"></i>' : 
            '<i class="fas fa-bars"></i>';
        
        navLinks.classList.toggle('nav-active');
        document.body.style.overflow = isMenuOpen ? 'hidden' : 'auto';
    });

    const menuBtns = document.querySelectorAll('.menu-nav-btn');
    const menuCategories = document.querySelectorAll('.menu-category');
    
    menuBtns.forEach(btn => {
        btn.addEventListener('click', () => {

            menuBtns.forEach(b => b.classList.remove('active'));

            btn.classList.add('active');
            

            menuCategories.forEach(cat => cat.classList.remove('active'));
        
            const category = document.getElementById(btn.dataset.category);
            category.classList.add('active');
        });
    });
    

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, {
        threshold: 0.1
    });

    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        observer.observe(item);
    });
    
});
