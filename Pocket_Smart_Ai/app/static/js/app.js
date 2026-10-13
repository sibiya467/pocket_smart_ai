async function api(url, options = {}) {
    const response = await fetch(url, {
        credentials: "same-origin",
        ...options
    });

    const contentType =
        response.headers.get("content-type") || "";

    let data;

    if (contentType.includes("application/json")) {
        data = await response.json();
    } else {
        data = {
            detail: await response.text()
        };
    }

    if (!response.ok) {
        throw new Error(
            data.detail || "Request failed"
        );
    }

    return data;
}


async function submitRegister(event) {
    event.preventDefault();

    try {
        const data = await api("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: document.getElementById("name").value.trim(),
                email: document.getElementById("email").value.trim(),
                password: document.getElementById("password").value
            })
        });

        alert(data.message);
        window.location.href = "/login";
    } catch (error) {
        alert(error.message);
    }

    return false;
}


async function submitLogin(event) {
    event.preventDefault();

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: document.getElementById("email").value.trim(),
                password: document.getElementById("password").value
            }),
            redirect: "follow",
            credentials: "same-origin"
        });

        if (!response.ok) {
            const contentType =
                response.headers.get("content-type") || "";

            let data = {};
            if (contentType.includes("application/json")) {
                data = await response.json();
            }

            throw new Error(
                data.detail || "Login failed."
            );
        }

        if (response.redirected) {
            window.location.href = response.url;
        } else {
            window.location.href = "/dashboard";
        }
    } catch (error) {
        alert(error.message);
    }

    return false;
}


function escapeHtml(value) {
    return String(value ?? "").replace(
        /[&<>"']/g,
        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            "\"": "&quot;",
            "'": "&#039;"
        })[character]
    );
}


function renderResult(data) {
    const result = document.getElementById("result");

    if (!result) {
        return;
    }

    const items = Array.isArray(data.items)
        ? data.items
        : [];

    const tips = Array.isArray(data.tips)
        ? data.tips
        : [];

    result.innerHTML = `
        <h2>Recommendations</h2>

        <p>${escapeHtml(data.summary)}</p>

        ${items.map(item => `
            <div class="result-item">
                <strong>${escapeHtml(item.name)}</strong>
                <br>
                ${escapeHtml(item.category)}
                · ₹${escapeHtml(item.estimated_price)}
                · ${escapeHtml(item.platform)}
                <br>
                <small>${escapeHtml(item.reason)}</small>
            </div>
        `).join("")}

        <p>
            <strong>Estimated total:</strong>
            ₹${escapeHtml(data.allocated_total)}
        </p>

        <p>
            ${tips.map(escapeHtml).join("<br>")}
        </p>

        <p>
            <small>${escapeHtml(data.disclaimer)}</small>
        </p>
    `;
}


async function sendPlanner(event, url, type) {
    event.preventDefault();

    const form = new FormData(event.target);

    const budget = Number(form.get("budget"));

    if (!Number.isFinite(budget) || budget <= 0) {
        alert("Please enter a valid budget.");
        return;
    }

    let body = { budget };

    if (type === "home") {
        let items = {};

        try {
            items = JSON.parse(form.get("items") || "{}");
        } catch {
            alert("Items JSON is invalid.");
            return;
        }

        const rooms = String(form.get("rooms") || "")
            .split(",")
            .map(item => item.trim())
            .filter(Boolean);

        if (!rooms.length) {
            alert("Please enter at least one room.");
            return;
        }

        Object.assign(body, {
            rooms,
            style: String(form.get("style") || "").trim(),
            items,
            notes: String(form.get("notes") || "")
        });
    } else {
        Object.assign(body, {
            guests: Number(form.get("guests")),
            event_type: String(form.get("event_type") || "").trim(),
            venue: String(form.get("venue") || ""),
            preferences: String(form.get("preferences") || "")
        });
    }

    try {
        const data = await api(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        });

        renderResult(data);
    } catch (error) {
        alert(error.message);
    }
}


async function sendJewelry(event) {
    event.preventDefault();

    const form = new FormData(event.target);

    try {
        const data = await api("/generate-jewelry", {
            method: "POST",
            body: form
        });

        renderResult(data);
    } catch (error) {
        alert(error.message);
    }
}


async function loadDashboard() {
    const welcome = document.getElementById("welcome");

    if (!welcome) {
        return;
    }

    try {
        const session = await api("/session-info");

        welcome.textContent =
            `Welcome, ${session.name}`;

        const history = await api("/history");
        const historyElement =
            document.getElementById("history");

        if (!historyElement) {
            return;
        }

        if (!history.length) {
            historyElement.textContent =
                "No recommendations yet.";
            return;
        }

        historyElement.innerHTML = history.map(item => `
            <div class="result-item">
                <strong>${escapeHtml(item.planner)}</strong>
                · ${escapeHtml(item.created_at)}
                <br>
                ${escapeHtml(item.response.summary)}
            </div>
        `).join("");
    } catch (error) {
        welcome.textContent = error.message;

        if (error.message.toLowerCase().includes("log in")) {
            window.location.href = "/login";
        }
    }
}


document.addEventListener(
    "DOMContentLoaded",
    loadDashboard
);
