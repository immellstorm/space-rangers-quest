(function () {
    const btn = document.getElementById("back-to-game");
    if (!btn) return;
    btn.addEventListener("click", function (e) {
        if (history.length > 1) {
            e.preventDefault();
            history.back();
        }
    });
})();