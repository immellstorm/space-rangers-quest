(function () {
    const audio = document.getElementById("menu-music");
    if (!audio) return;

    audio.volume = 0.25;

    const play = () => audio.play().catch(() => { });
    play();
    document.addEventListener("click", play, { once: true });
    document.addEventListener("keydown", play, { once: true });
})();