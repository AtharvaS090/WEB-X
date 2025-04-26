const burger = document.querySelector('.burger');
const nav = document.querySelector('.nav-links');

burger.addEventListener('click', () => {
    nav.classList.toggle('active');
    burger.classList.toggle('toggle');
});

const navLinks = document.querySelectorAll('.nav-links a');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        nav.classList.remove('active');
        burger.classList.remove('toggle');
    });
});

const categoryBtns = document.querySelectorAll('.category-btn');
const programCards = document.querySelectorAll('.program-card');

categoryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        categoryBtns.forEach(btn => btn.classList.remove('active'));
        btn.classList.add('active');
        
        const category = btn.dataset.category;
        
        programCards.forEach(card => {
            if (category === 'all' || card.dataset.category === category) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
});

const planTabs = document.querySelectorAll('.plan-tab');
const planContents = document.querySelectorAll('.plan-content');

planTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        planTabs.forEach(tab => tab.classList.remove('active'));
        planContents.forEach(content => content.classList.remove('active'));
        
        tab.classList.add('active');
        const planId = tab.dataset.plan;
        document.getElementById(planId).classList.add('active');
    });
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

const bmiForm = document.querySelector('#bmi form');
if (bmiForm) {
    bmiForm.addEventListener('submit', (e) => {
        const weight = document.getElementById('weight').value;
        const height = document.getElementById('height').value;
        
        if (weight <= 0 || height <= 0) {
            e.preventDefault();
            alert('Please enter valid weight and height values.');
        }
    });
}