document.addEventListener("DOMContentLoaded", () => {

    const input = document.getElementById("achFilter");
    const toggle = document.getElementById("filterToggle");
    const menu = document.getElementById("filterMenu");

    // 🛑 ZÁCHRANNÁ BRZDA: Pokud tyto elementy na stránce nejsou, skript se dál neprovede
    if (!input || !toggle || !menu) return;

    const checkboxes = document.querySelectorAll("#filterMenu input");
    const items = Array.from(document.querySelectorAll(".ach-item"));

    /* =========================
       DROPDOWN
    ========================= */

    toggle.addEventListener("click", () => {
        menu.classList.toggle("show");
    });

    document.addEventListener("click", (e) => {
        if (!toggle.contains(e.target) && !menu.contains(e.target)) {
            menu.classList.remove("show");
        }
    });

    /* =========================
       TYPES
    ========================= */

    function getActiveTypes() {
        return Array.from(checkboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value.trim().toLowerCase());
    }

    /* =========================
       FILTER
    ========================= */

    function filter() {
        const text = input.value.toLowerCase();
        const activeTypes = getActiveTypes(); // Získáme pole aktivních checkboxů

        items.forEach(item => {
            const title = item.querySelector("h4")?.textContent.toLowerCase() || "";
            // Získáme typy achievementu a rozdělíme je do pole (např. ["story", "missable"])
            const itemTypes = (item.dataset.type || "").toLowerCase().split(" ").filter(t => t); 

            const matchText = title.includes(text);
            
            // ZKONTROLUJEME, JESTLI MÁ ACHIEVEMENT ALESPOŇ JEDEN Z VYBRANÝCH TYPŮ
            // Pokud není vybrán žádný filtr (activeTypes.length === 0), zobrazíme vše
            // Jinak zkontrolujeme, zda se některý z typů achievementu (itemTypes) shoduje s některým vybraným filtrem (activeTypes)
            const matchType = activeTypes.length === 0 || itemTypes.some(t => activeTypes.includes(t));

            const show = matchText && matchType;

            item.style.display = show ? "" : "none";
            item.style.opacity = show ? "1" : "0";
            item.style.transform = show ? "scale(1)" : "scale(0.98)";
            item.style.transition = "all 0.2s ease";
        });
    }

    const sortSelect = document.getElementById('sortSelect');
    const achList = document.querySelector('.ach-list');

    if (sortSelect && achList) {
        sortSelect.addEventListener('change', (e) => {
            const order = e.target.value;
            
            // Pokud uživatel vybere výchozí prázdnou možnost, nic neřadíme
            if (order === 'default') return;

            // Vybereme všechny kartičky achievementů
            const items = Array.from(achList.querySelectorAll('.ach-item'));

            // Seřadíme pole prvků podle textu uvnitř <h4>
            items.sort((a, b) => {
                const titleA = a.querySelector('h4').innerText.toLowerCase();
                const titleB = b.querySelector('h4').innerText.toLowerCase();
                
                if (order === 'asc') {
                    return titleA.localeCompare(titleB);
                } else if (order === 'desc') {
                    return titleB.localeCompare(titleA);
                }
            });

            // Přidáme seřazené prvky zpět (čímž se vizuálně přeskládají)
            items.forEach(item => achList.appendChild(item));
        });
    }

    input.addEventListener("input", filter);
    checkboxes.forEach(cb => cb.addEventListener("change", filter));

});