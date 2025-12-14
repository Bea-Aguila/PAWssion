window.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('loader');

    setTimeout(() => {
        loader.style.opacity = 0; // fade out
        setTimeout(() => {
            loader.style.display = 'none';
        }, 1000);
    }, 1000); // loader duration
});


// Ito lang ang code para sa paw print. Walang dependencies.
document.addEventListener('click', (event) => {
    
    const clickX = event.clientX;
    const clickY = event.clientY;

    const paw = document.createElement('span');
    paw.classList.add('paw-burst');
    paw.textContent = '🐾'; 

    paw.style.left = `${clickX}px`;
    paw.style.top = `${clickY}px`;

    document.body.appendChild(paw);
    
    requestAnimationFrame(() => {
        paw.classList.add('active');
    });
    
    setTimeout(() => {
        paw.classList.remove('active'); 
        setTimeout(() => {
            paw.remove();
        }, 500); 
    }, 50); 
});