document.addEventListener('DOMContentLoaded', () => {
    const timerBox = document.querySelector('[data-timer]');
    const submitForm = document.querySelector('[data-auto-submit]');

    if (!timerBox || !submitForm) {
        return;
    }

    const timerLabel = timerBox.querySelector('[data-timer-label]');
    let seconds = Number(timerBox.dataset.seconds || 0);

    const formatTime = (value) => {
        const mins = Math.floor(value / 60);
        const secs = value % 60;
        return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    };

    const tick = () => {
        timerLabel.textContent = formatTime(seconds);

        if (seconds <= 0) {
            submitForm.submit();
            return;
        }

        seconds -= 1;
        setTimeout(tick, 1000);
    };

    tick();
});

document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('[data-nav-toggle]');
    const nav = document.querySelector('[data-mobile-nav]');

    if (toggle && nav) {
        toggle.addEventListener('click', () => {
            nav.classList.toggle('open');
        });
    }
});