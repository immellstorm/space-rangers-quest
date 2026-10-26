(function () {
    const glossary = {
        "peleng": "Пеленги — разумная раса, похожая на лягушек и ящериц. Четыре руки, любовь к спиртному и болотам.",
        "duzallag": "Дзухаллаг — пеленгская диверсионно-разведывательная организация.",
        "poluos": "Полуось — индустриальная планета, покрытая сетью гостиниц, казино и ресторанов.",
        "betelgeuse": "Бетельгейзе — звездная система, в которой находится планета Полуось.",
        "malok": "Малоки — крупная мускулистая раса, славящаяся силой и тяжелым вооружением.",
        "gaal": "Гаальцы — высокоразвитая раса, известная спецслужбами и технологиями.",
        "dominatory": "Доминаторы — враждебная раса, с которой идет война.",
        "kacap": "Кацап — пеленг, пират, контрабандист.",
        "fenya": "Фэяне — технически одаренная раса, инженеры и ученые.",
        "raksh": "Рахиш — родная планета пеленгов, болотистая и опасная.",
        "rusman": "Русман — агент с планеты Окошки Виста, посредник.",
        "cruiser": "Крейсер Дзухаллага — секретный военный корабль.",
        "ryaska": "Болотная ряска — традиционный пеленгский коктейль.",
        "vtekilla": "Втыкилла — крепкий напиток, популярный среди пиратов.",
        "guanava": "Гуанава — очень крепкая настойка для бывалых пиратов.",
        "dark_drink": "Махпельское тёмное — слабое пиво.",
        "nucker_malok": "Малокское ядерное — экстремально крепкий напиток."
    };

    document.addEventListener("DOMContentLoaded", function () {
        const tip = document.createElement("div");
        tip.className = "glossary-tooltip-fixed";
        document.body.appendChild(tip);

        document.querySelectorAll(".glossary-term").forEach(function (term) {
            const key = term.getAttribute("data-term");
            if (!key || !glossary[key]) return;

            term.addEventListener("mouseenter", function () {
                tip.textContent = glossary[key];
                tip.classList.add("visible");

                const rect = term.getBoundingClientRect();
                const tipW = tip.offsetWidth;
                const tipH = tip.offsetHeight;

                let left = rect.left + rect.width / 2 - tipW / 2;
                left = Math.max(10, Math.min(left, window.innerWidth - tipW - 10));

                let top = rect.bottom + 6;
                if (top + tipH > window.innerHeight - 10) {
                    top = rect.top - tipH - 6;
                }

                tip.style.left = left + "px";
                tip.style.top = top + "px";
            });

            term.addEventListener("mouseleave", function () {
                tip.classList.remove("visible");
            });

            term.addEventListener("click", function () {
                window.location.href = "/glossary#" + key;
            });
        });
    });
})();