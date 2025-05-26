// Frontend JavaScript for MDPmotorcycles

const API_BASE_URL = "http://localhost:8000"; // Adjust as needed

// Utility to get token from localStorage
function getToken() {
    return localStorage.getItem("token");
}

// Utility to set token to localStorage
function setToken(token) {
    localStorage.setItem("token", token);
}

// Utility to remove token (logout)
function removeToken() {
    localStorage.removeItem("token");
}

// Show message in a modal or alert div
function showMessage(message) {
    let messageDiv = document.getElementById("message-div");
    if (!messageDiv) {
        messageDiv = document.createElement("div");
        messageDiv.id = "message-div";
        messageDiv.style.position = "fixed";
        messageDiv.style.top = "10px";
        messageDiv.style.left = "50%";
        messageDiv.style.transform = "translateX(-50%)";
        messageDiv.style.backgroundColor = "#333";
        messageDiv.style.color = "#fff";
        messageDiv.style.padding = "10px 20px";
        messageDiv.style.borderRadius = "5px";
        messageDiv.style.zIndex = "1000";
        document.body.appendChild(messageDiv);
    }
    messageDiv.textContent = message;
    messageDiv.style.display = "block";
}

// Hide message
function hideMessage() {
    const messageDiv = document.getElementById("message-div");
    if (messageDiv) {
        messageDiv.style.display = "none";
    }
}

// Fetch motos and display in catalog.html
function formatPrice(price) {
    // Convert price to integer to remove decimals
    const intPrice = Math.floor(price);
    // Format with apostrophe as thousands separator
    return intPrice.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "'");
}

async function loadMotos() {
    const motosList = document.getElementById("motos-list");
    if (!motosList) return;

    try {
        const response = await fetch(`${API_BASE_URL}/motos/`);
        const motos = await response.json();
        motosList.innerHTML = "";
        motos.forEach(moto => {
            const motoDiv = document.createElement("div");
            motoDiv.className = "moto-item";
            motoDiv.innerHTML = `
                <h3>${moto.nombre}</h3>
                <p>Marca: ${moto.marca}</p>
                <p>Precio: $${formatPrice(moto.precio)}</p>
                ${moto.img_url ? `<img src="${moto.img_url}" alt="${moto.nombre}" width="200" />` : ""}
                <button onclick="addToCart(${moto.id}, 'moto')">Agregar al carrito</button>
            `;
            motosList.appendChild(motoDiv);
        });
    } catch (error) {
        console.error("Error loading motos:", error);
    }
}

// Fetch accesorios and display in accessories.html
async function loadAccesorios() {
    const accesoriosList = document.getElementById("accesorios-list");
    if (!accesoriosList) return;

    try {
        const response = await fetch(`${API_BASE_URL}/accesorios/`);
        const accesorios = await response.json();
        accesoriosList.innerHTML = "";
        accesorios.forEach(acc => {
            const accDiv = document.createElement("div");
            accDiv.className = "moto-item";
            accDiv.innerHTML = `
                <h3>${acc.nombre}</h3>
                <p>Precio: $${formatPrice(acc.precio)}</p>
                <p>${acc.descripcion || ""}</p>
                ${acc.img_url ? `<img src="${acc.img_url}" alt="${acc.nombre}" width="200" />` : ""}
                <button onclick="addToCart(${acc.id}, 'accesorio')">Agregar al carrito</button>
            `;
            accesoriosList.appendChild(accDiv);
        });
    } catch (error) {
        console.error("Error loading accesorios:", error);
    }
}

// Add item to cart
async function addToCart(id_producto, tipo_producto) {
    const token = getToken();
    if (!token) {
        alert("Debe iniciar sesión para agregar al carrito.");
        return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/cart/add`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ id_producto, tipo_producto })
        });
        if (response.ok) {
            alert("Producto agregado al carrito.");
        } else {
            const data = await response.json();
            alert("Error al agregar al carrito: " + (data.detail || response.statusText));
        }
    } catch (error) {
        console.error("Error adding to cart:", error);
    }
}

// Load cart items in cart.html
async function loadCart() {
    const cartItemsDiv = document.getElementById("cart-items");
    if (!cartItemsDiv) return;

    const token = getToken();
    console.log("loadCart token:", token);
    if (!token) {
        cartItemsDiv.innerHTML = "<p>Debe iniciar sesión para ver el carrito.</p>";
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/cart/`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        console.log("loadCart response status:", response.status);
        if (!response.ok) {
            cartItemsDiv.innerHTML = "<p>Error al cargar el carrito.</p>";
            return;
        }
        const items = await response.json();
        if (items.length === 0) {
            cartItemsDiv.innerHTML = "<p>El carrito está vacío.</p>";
            return;
        }
        cartItemsDiv.innerHTML = "";

        let totalSum = 0;
        let totalQuantity = 0;

        items.forEach(item => {
            const itemDiv = document.createElement("div");
            itemDiv.className = "cart-item";

            const itemTotal = item.precio * item.cantidad;
            totalSum += itemTotal;
            totalQuantity += item.cantidad;

            itemDiv.innerHTML = `
                <img src="${item.img_url || 'https://via.placeholder.com/150'}" alt="${item.nombre}" width="150" />
                <div class="cart-item-details">
                    <h3>${item.nombre}</h3>
                    <p>${item.descripcion || ''}</p>
                    <p><strong>Cantidad:</strong> ${item.cantidad}</p>
                    <p>Precio unitario: $${formatPrice(item.precio)}</p>
                    <p>Subtotal: $${formatPrice(itemTotal)}</p>
                    <button class="remove-btn" data-item-id="${item.id}">Eliminar</button>
                </div>
            `;
            cartItemsDiv.appendChild(itemDiv);
        });

        // Add event listeners for remove buttons
        const removeButtons = document.querySelectorAll(".remove-btn");
        removeButtons.forEach(button => {
            button.addEventListener("click", async (event) => {
                const itemId = event.target.getAttribute("data-item-id");
                if (!itemId) return;
                const token = getToken();
                if (!token) {
                    alert("Debe iniciar sesión para eliminar productos del carrito.");
                    return;
                }
                try {
                    const response = await fetch(`${API_BASE_URL}/cart/remove/${itemId}`, {
                        method: "DELETE",
                        headers: {
                            "Authorization": `Bearer ${token}`
                        }
                    });
                    if (response.ok) {
                        alert("Producto eliminado del carrito.");
                        await loadCart();
                    } else {
                        alert("Error al eliminar el producto del carrito.");
                    }
                } catch (error) {
                    console.error("Error removing item from cart:", error);
                }
            });
        });

        const cartSummaryDiv = document.getElementById("cart-summary");
        cartSummaryDiv.innerHTML = "";
        const totalDiv = document.createElement("div");
        totalDiv.className = "cart-total";
        totalDiv.innerHTML = `
            <h3>Resumen de la compra</h3>
            <p><strong>Cantidad total de productos:</strong> ${totalQuantity}</p>
            <p><strong>Total de la compra:</strong> $${totalSum.toFixed(2)}</p>
        `;
        cartSummaryDiv.appendChild(totalDiv);

    } catch (error) {
        console.error("Error loading cart:", error);
    }
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData.toString()
        });
        if (response.ok) {
            const data = await response.json();
            setToken(data.access_token);
            alert("Inicio de sesión exitoso.");
            window.location.href = "index.html";
        } else {
            const data = await response.json();
            alert("Error en login: " + (data.detail || response.statusText));
        }
    } catch (error) {
        console.error("Login error:", error);
    }
}

// Handle register form submission
async function handleRegister(event) {
    event.preventDefault();
    const nombre = document.getElementById("register-name").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre, email, password })
        });
        if (response.ok) {
            alert("Registro exitoso. Por favor, inicie sesión.");
            window.location.href = "login.html";
        } else {
            const data = await response.json();
            alert("Error en registro: " + (data.detail || response.statusText));
        }
    } catch (error) {
        console.error("Register error:", error);
    }
}

// Attach event listeners if forms exist
document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }
    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", handleRegister);
    }
    loadMotos();
    loadAccesorios();
    loadCart();

    // Add event listener for refresh catalog button
    const refreshBtn = document.getElementById("refresh-catalog-btn");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", async () => {
            showMessage("Espere, se está actualizando el catálogo...");
            try {
                const response = await fetch(`${API_BASE_URL}/scrape`);
                if (response.ok) {
                    const data = await response.json();
                    showMessage(data.message);
                    await loadMotos();
                } else {
                    showMessage("Error al actualizar el catálogo.");
                }
            } catch (error) {
                console.error("Error updating catalog:", error);
                showMessage("Error al actualizar el catálogo.");
            }
            setTimeout(() => {
                hideMessage();
            }, 3000);
        });
    }
});
