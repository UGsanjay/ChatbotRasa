class MenuChatBot {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.isLoading = false;
        this.cart = [];
        this.isConnected = false;
        this.currentOrder = null;
        this.init();
    }

    generateSessionId() {
        return 'web_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    init() {
        this.bindEvents();
        this.checkServerConnection();
        this.setupAutoScroll();
        this.updateCartUI();
        this.showWelcomeMessage();
    }

    showWelcomeMessage() {
        const welcomeMessages = [
            "🍽️ Halo! Selamat datang di ChatBot Menu Makanan! Saya siap membantu Anda mencari makanan lezat!",
            "👋 Hai! Mau cari menu apa hari ini? Saya punya banyak rekomendasi makanan enak dari database MySQL!",
            "🌟 Selamat datang! Ceritakan selera Anda, saya akan carikan menu yang pas!",
            "😊 Halo! Lagi lapar ya? Yuk chat dengan saya untuk mencari menu favorit!"
        ];
        
        const randomWelcome = welcomeMessages[Math.floor(Math.random() * welcomeMessages.length)];
        
        setTimeout(() => {
            this.addMessage(randomWelcome, 'bot');
            
            setTimeout(() => {
                this.addMessage(
                    "💡 **Tips:** Coba ketik seperti:\n" +
                    "• \"ada ikan?\" - untuk menu ikan\n" +
                    "• \"yang pedas\" - untuk makanan pedas\n" +
                    "• \"menu ayam bakar\" - untuk ayam bakar\n" +
                    "• \"random menu\" - untuk surprise!\n" +
                    "• \"ingest data\" - untuk load database", 
                    'bot'
                );
            }, 1500);
        }, 500);
    }

    bindEvents() {
        document.getElementById('sendButton').addEventListener('click', () => this.sendMessage());
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        document.getElementById('messageInput').addEventListener('input', (e) => {
            const sendButton = document.getElementById('sendButton');
            const hasText = e.target.value.trim().length > 0;
            sendButton.disabled = !hasText || this.isLoading;
            
            const charCount = e.target.value.length;
            if (charCount > 400) {
                e.target.style.borderColor = '#ff9800';
            } else {
                e.target.style.borderColor = '';
            }
        });

        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const text = e.target.dataset.text;
                document.getElementById('messageInput').value = text;
                this.sendMessage();
            });
        });

        this.rotateSuggestions();

        document.getElementById('clearChat').addEventListener('click', () => {
            if (confirm('Apakah Anda yakin ingin menghapus semua percakapan?')) {
                this.clearChat();
            }
        });

        document.getElementById('cartButton').addEventListener('click', () => {
            this.openCartPage();
        });

        const closeCartBtn = document.getElementById('closeCart');
        if (closeCartBtn) {
            closeCartBtn.addEventListener('click', () => {
                this.closeCartPage();
            });
        }

        const clearCartBtn = document.getElementById('clearCartBtn');
        if (clearCartBtn) {
            clearCartBtn.addEventListener('click', () => {
                this.clearCart();
            });
        }

        const checkoutBtn = document.getElementById('checkoutBtn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => {
                this.initiateCheckout();
            });
        }

        const closeModalBtn = document.getElementById('closeModal');
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', () => {
                this.closeModal();
            });
        }

        const menuModal = document.getElementById('menuModal');
        if (menuModal) {
            menuModal.addEventListener('click', (e) => {
                if (e.target.id === 'menuModal') this.closeModal();
            });
        }

        const cartPage = document.getElementById('cartPage');
        if (cartPage) {
            cartPage.addEventListener('click', (e) => {
                if (e.target.id === 'cartPage') this.closeCartPage();
            });
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
                this.closeCheckoutModal();
                this.closePaymentModal();
                this.closeCartPage();
            }
        });
    }

    rotateSuggestions() {
        const suggestionSets = [
            [
                { text: "ada ikan?", emoji: "🐟", label: "Menu Ikan" },
                { text: "yang pedas", emoji: "🌶️", label: "Menu Pedas" },
                { text: "menu sapi", emoji: "🐄", label: "Menu Sapi" },
                { text: "menu random", emoji: "🎲", label: "Surprise Me" }
            ],
            [
                { text: "makanan berkuah", emoji: "🍲", label: "Yang Berkuah" },
                { text: "seafood enak", emoji: "🦐", label: "Seafood" },
                { text: "Vegetarian", emoji: "🥦", label: "Vegetarian" },
                { text: "menu manis", emoji: "🍯", label: "Rasa Manis" }
            ],
            [
                { text: "sup hangat", emoji: "🥣", label: "Sup Hangat" },
                { text: "menu ayam", emoji: "🍗", label: "Olahan Ayam" },
                { text: "makanan padang", emoji: "🌶️", label: "Masakan Padang" },
                { text: "help", emoji: "🚨", label: "Butuh bantuan?" }
            ]
        ];

        let currentSet = 0;
        const container = document.querySelector('.quick-suggestions');

        const rotateFn = () => {
            if (!container) return;
            
            const suggestions = suggestionSets[currentSet];
            container.innerHTML = suggestions.map(suggestion => 
                `<button class="suggestion-btn" data-text="${suggestion.text}">
                    ${suggestion.emoji} ${suggestion.label}
                </button>`
            ).join('');

            container.querySelectorAll('.suggestion-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const text = e.target.dataset.text;
                    document.getElementById('messageInput').value = text;
                    this.sendMessage();
                });
            });

            currentSet = (currentSet + 1) % suggestionSets.length;
        };

        rotateFn();
        setInterval(rotateFn, 15000);
    }

    setupAutoScroll() {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        const observer = new MutationObserver(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });

        observer.observe(chatMessages, {
            childList: true,
            subtree: true
        });
    }

    async checkServerConnection() {
        try {
            const response = await fetch('/status');
            const status = await response.json();
            
            const statusDot = document.getElementById('connectionStatus');
            const statusText = document.getElementById('statusText');

            if (!statusDot || !statusText) return;

            if (status.rasaServer === 'connected') {
                statusDot.className = 'status-dot online';
                statusText.textContent = 'Terhubung';
                this.isConnected = true;
            } else {
                statusDot.className = 'status-dot offline';
                statusText.textContent = 'Rasa Server Offline';
                this.isConnected = false;
            }
        } catch (error) {
            const statusDot = document.getElementById('connectionStatus');
            const statusText = document.getElementById('statusText');
            
            if (statusDot && statusText) {
                statusDot.className = 'status-dot offline';
                statusText.textContent = 'Server Error';
            }
            this.isConnected = false;
        }
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();

        if (!message || this.isLoading) return;

        input.value = '';
        this.setLoading(true);
        this.addMessage(message, 'user');

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    sessionId: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            
            if (data.sessionId) {
                this.sessionId = data.sessionId;
            }

            if (data.responses && data.responses.length > 0) {
                for (const botResponse of data.responses) {
                    if (botResponse.text) {
                        this.addMessage(botResponse.text, 'bot');
                    }
                }
            }

            if (data.recommendedMenus && data.recommendedMenus.length > 0) {
                this.displayMenus(data.recommendedMenus);
                this.updateMenuCount(data.recommendedMenus.length);
            }

        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage(
                `❌ Maaf, terjadi kesalahan saat menghubungi server.\n\n` +
                `Error: ${error.message}\n\n` +
                `💡 Silakan coba lagi atau refresh halaman.`, 
                'bot'
            );
        } finally {
            this.setLoading(false);
        }
    }

    displayMenus(menus) {
        const menuResults = document.getElementById('menuResults');
        if (!menuResults) return;
        
        menuResults.style.opacity = '0';
        
        setTimeout(() => {
            menuResults.innerHTML = '';
            
            if (menus.length === 0) {
                menuResults.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-utensils"></i>
                        <p>Tidak ada menu yang ditemukan</p>
                        <p class="empty-subtitle">Coba kata kunci yang berbeda!</p>
                    </div>
                `;
            } else {
                menus.forEach((menu, index) => {
                    const menuItem = this.createMenuItemElement(menu, index);
                    menuResults.appendChild(menuItem);
                });
            }
            
            menuResults.style.opacity = '1';
        }, 300);
    }

    createMenuItemElement(menu, index) {
        const menuDiv = document.createElement('div');
        menuDiv.className = 'menu-item';
        menuDiv.style.animationDelay = `${index * 0.1}s`;

        const imageDisplay = menu.image ? 
            `<img src="${menu.image}" alt="${menu.title || 'Menu'}" class="menu-image" loading="lazy" 
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
             <div class="no-image-placeholder" style="display:none;">image</div>` :
            `<div class="no-image-placeholder">image</div>`;
    
        const ratingDisplay = menu.rating ? 
            `<div class="menu-rating">⭐ ${menu.rating}/5</div>` : '';
    
        const categoryDisplay = menu.category ? 
            `<div class="menu-category">${menu.category}</div>` : '';

        const numericPrice = this.parsePrice(menu.price);
        menu.numericPrice = numericPrice; 
    
        menuDiv.innerHTML = `
            <div class="menu-image-container">
                ${imageDisplay}
                ${categoryDisplay}
            </div>
            <div class="menu-content">
                <h3>${menu.title || 'Menu'}</h3>
                <div class="menu-price">${menu.price || 'Harga belum tersedia'}</div>
                ${ratingDisplay}
            </div>
            <div class="menu-actions">
                <button class="view-detail-btn" data-menu='${JSON.stringify(menu).replace(/'/g, "&#39;")}'>
                    <i class="fas fa-info-circle"></i> Detail
                </button>
                <button class="add-to-cart-btn" data-menu='${JSON.stringify(menu).replace(/'/g, "&#39;")}'>
                    <i class="fas fa-plus"></i> Tambah
                </button>
            </div>
        `;
    
        const viewDetailBtn = menuDiv.querySelector('.view-detail-btn');
        const addToCartBtn = menuDiv.querySelector('.add-to-cart-btn');
    
        if (viewDetailBtn) {
            viewDetailBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showMenuDetail(menu);
            });
        }
    
        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.addToCart(menu);
            });
        }
    
        return menuDiv;
    }

    parsePrice(priceString) {
        if (!priceString) return 0;
        
        let numStr = priceString.toString();
        
        if (numStr.includes('ribu')) {
            numStr = numStr.replace(/[^\d]/g, '');
            return parseInt(numStr) * 1000;
        } else if (numStr.includes('juta')) {
            numStr = numStr.replace(/[^\d]/g, '');
            return parseInt(numStr) * 1000000;
        } else {
            numStr = numStr.replace(/[^\d]/g, '');
            return parseInt(numStr) || 0;
        }
    }


    showMenuDetail(menu) {
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        const menuModal = document.getElementById('menuModal');
        
        if (!modalTitle || !modalContent || !menuModal) return;
        
        modalTitle.textContent = menu.title || 'Menu Detail';
        
        const imageDisplay = menu.image ? 
            `<img src="${menu.image}" alt="${menu.title || 'Menu'}" 
                 style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 1rem;"
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
             <div class="no-image-placeholder-modal" style="display:none;">image</div>` :
            `<div class="no-image-placeholder-modal">image</div>`;
        
        const ratingStars = menu.rating ? '⭐'.repeat(Math.floor(menu.rating)) : '';
        
        modalContent.innerHTML = `
            <div class="menu-detail">
                ${imageDisplay}
                
                ${menu.category ? `<div class="detail-category">📂 ${menu.category}</div>` : ''}
                
                <div class="detail-price">💰 ${menu.price || 'Harga belum tersedia'}</div>
                
                ${menu.rating ? `<div class="detail-rating">⭐ ${menu.rating}/5 ${ratingStars}</div>` : ''}
                
                ${menu.ingredients ? `
                    <h4>🥘 Bahan-bahan</h4>
                    <p>${menu.ingredients}</p>
                ` : ''}
                
                ${menu.description ? `
                    <h4>📝 Deskripsi</h4>
                    <p>${menu.description}</p>
                ` : ''}
                
                <button class="add-to-cart-btn enhanced" style="width: 100%; margin-top: 1rem;" onclick="window.menuChatBot.addToCartFromModal(${JSON.stringify(menu).replace(/"/g, '&quot;')})">
                    <i class="fas fa-shopping-cart"></i> Tambah ke Keranjang
                </button>
            </div>
        `;
        
        menuModal.classList.remove('hidden');
    }

    addToCartFromModal(menu) {
        this.addToCart(menu);
        this.closeModal();
    }

    addToCart(menu) {
        if (!menu.numericPrice) {
            menu.numericPrice = this.parsePrice(menu.price);
        }

        const existingItem = this.cart.find(item => item.id === menu.id);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.cart.push({
                ...menu,
                quantity: 1
            });
        }
        
        this.updateCartUI();
        this.showAddToCartAnimation(menu.title || 'Menu');
    }

    showAddToCartAnimation(menuTitle) {
        const notification = document.createElement('div');
        notification.className = 'cart-notification';
        notification.innerHTML = `<i class="fas fa-check"></i> ${menuTitle} ditambahkan ke keranjang!`;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 2000);
    }

    updateCartUI() {
        const cartCount = document.getElementById('cartCount');
        if (!cartCount) return;
        
        const totalItems = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        cartCount.textContent = totalItems;
        
        if (totalItems > 0) {
            cartCount.classList.add('bounce');
            setTimeout(() => cartCount.classList.remove('bounce'), 300);
        }
    }

    updateMenuCount(count) {
        const menuCount = document.getElementById('menuCount');
        if (menuCount) {
            menuCount.textContent = count;
        }
    }

    openCartPage() {
        this.renderCartItems();
        const cartPage = document.getElementById('cartPage');
        if (cartPage) {
            cartPage.classList.remove('hidden');
        }
    }

    closeCartPage() {
        const cartPage = document.getElementById('cartPage');
        if (cartPage) {
            cartPage.classList.add('hidden');
        }
    }

    renderCartItems() {
        const cartItems = document.getElementById('cartItems');
        const cartSummary = document.getElementById('cartSummary');
        
        if (!cartItems) return;
        
        if (this.cart.length === 0) {
            cartItems.innerHTML = `
                <div class="empty-cart">
                    <i class="fas fa-shopping-cart"></i>
                    <p>Keranjang belanja kosong</p>
                    <p>Tambahkan menu dari halaman utama</p>
                </div>
            `;
            if (cartSummary) {
                cartSummary.classList.add('hidden');
            }
            return;
        }

        cartItems.innerHTML = '';
        let totalPrice = 0;
        let totalItems = 0;

        this.cart.forEach(item => {
            const itemPrice = item.numericPrice || this.parsePrice(item.price);
            
            totalPrice += itemPrice * item.quantity;
            totalItems += item.quantity;

            const cartItem = document.createElement('div');
            cartItem.className = 'cart-item';
            
            const imageDisplay = item.image ? 
                `<img src="${item.image}" alt="${item.title || 'Menu'}" class="cart-item-image"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                 <div class="cart-no-image" style="display:none;">image</div>` :
                `<div class="cart-no-image">image</div>`;
            
            cartItem.innerHTML = `
                ${imageDisplay}
                <div class="cart-item-info">
                    <h4>${item.title || 'Menu'}</h4>
                    <div class="cart-item-price">${item.price || 'Harga belum tersedia'}</div>
                    ${item.category ? `<div class="cart-item-category">${item.category}</div>` : ''}
                </div>
                <div class="cart-item-controls">
                    <button class="quantity-btn" onclick="window.menuChatBot.updateQuantity(${item.id}, -1)">-</button>
                    <span class="quantity-display">${item.quantity}</span>
                    <button class="quantity-btn" onclick="window.menuChatBot.updateQuantity(${item.id}, 1)">+</button>
                    <button class="remove-btn" onclick="window.menuChatBot.removeFromCart(${item.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            cartItems.appendChild(cartItem);
        });

        const totalItemsEl = document.getElementById('totalItems');
        const totalPriceEl = document.getElementById('totalPrice');
        
        if (totalItemsEl) totalItemsEl.textContent = totalItems;
        if (totalPriceEl) totalPriceEl.textContent = this.formatPrice(totalPrice);
        if (cartSummary) cartSummary.classList.remove('hidden');
    }

    updateQuantity(menuId, change) {
        const item = this.cart.find(item => item.id === menuId);
        if (item) {
            item.quantity += change;
            if (item.quantity <= 0) {
                this.removeFromCart(menuId);
            } else {
                this.renderCartItems();
                this.updateCartUI();
            }
        }
    }

    removeFromCart(menuId) {
        this.cart = this.cart.filter(item => item.id !== menuId);
        this.renderCartItems();
        this.updateCartUI();
    }

    clearCart() {
        if (confirm('Apakah Anda yakin ingin mengosongkan keranjang?')) {
            this.cart = [];
            this.renderCartItems();
            this.updateCartUI();
        }
    }

    initiateCheckout() {
        if (this.cart.length === 0) {
            alert('Keranjang belanja kosong!');
            return;
        }

        let totalPrice = 0;
        let totalItems = 0;

        this.cart.forEach(item => {
            const itemPrice = item.numericPrice || this.parsePrice(item.price);
            totalPrice += itemPrice * item.quantity;
            totalItems += item.quantity;
        });

        this.showPaymentModal(totalPrice, totalItems);
    }

    showPaymentModal(totalPrice, totalItems) {
        if (!document.getElementById('paymentModal')) {
            this.createPaymentModal();
        }

        const modal = document.getElementById('paymentModal');
        const orderTotal = document.getElementById('orderTotal');
        const invoiceId = document.getElementById('invoiceId');

        if (!modal || !orderTotal || !invoiceId) return;

        const newInvoiceId = this.generateInvoiceId();
        
        orderTotal.textContent = this.formatPrice(totalPrice);
        invoiceId.textContent = newInvoiceId;

        this.currentOrder = {
            id: newInvoiceId,
            total: totalPrice,
            items: totalItems,
            cart: [...this.cart]
        };

        modal.classList.remove('hidden');
        this.closeCartPage();
    }

    createPaymentModal() {
        const modalHTML = `
            <div id="paymentModal" class="modal hidden">
                <div class="payment-modal-content">
                    <div class="payment-header">
                        <button id="closePaymentModal" class="back-btn">
                            <i class="fas fa-arrow-left"></i>
                        </button>
                        <h3>E-Wallet (QR Code)</h3>
                        <button class="cancel-btn" onclick="window.menuChatBot.closePaymentModal()">CANCEL</button>
                    </div>
                    
                    <div class="payment-body">
                        <div class="payment-total">
                            <span>Total</span>
                            <div id="orderTotal" class="total-amount">Rp 0</div>
                        </div>
                        
                        <div class="payment-instruction">
                            Buka aplikasi E-Wallet Anda dan Scan QR Code untuk membayar pesanan.
                        </div>
                        
                        <div class="qr-section">
                            <div class="qr-code">
                                <div class="qr-placeholder">
                                    <div class="qr-pattern"></div>
                                </div>
                                <div class="qr-logo">
                                    <span>QRIS</span>
                                    <small>QR Code Standar Pembayaran Nasional</small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="merchant-info">
                            <div class="info-row">
                                <span>Nama Merchant</span>
                                <span>Foodcourt Jaya</span>
                            </div>
                            <div class="info-row">
                                <span>Invoice ID</span>
                                <span id="invoiceId">XXXX-XXXX-XXX</span>
                            </div>
                        </div>
                        
                        <div class="payment-methods">
                            <span class="support-text">Pilih metode transaksi:</span>
                            <div class="payment-icons">
                                <div class="payment-icon ovo">OVO</div>
                                <div class="payment-icon linkaja">LinkAja</div>
                                <div class="payment-icon gopay">GoPay</div>
                                <div class="payment-icon dana">DANA</div>
                            </div>
                        </div>
                        
                        <div class="payment-note">
                            Setelah anda memindai dan mengkonfirmasi, silakan lanjutkan cek status pembayaran Anda.
                        </div>
                        
                        <button id="checkPaymentStatus" class="check-status-btn">
                            Cek Status Pembayaran
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        const closePaymentModalBtn = document.getElementById('closePaymentModal');
        if (closePaymentModalBtn) {
            closePaymentModalBtn.addEventListener('click', () => {
                this.closePaymentModal();
            });
        }

        const checkPaymentStatusBtn = document.getElementById('checkPaymentStatus');
        if (checkPaymentStatusBtn) {
            checkPaymentStatusBtn.addEventListener('click', () => {
                this.simulatePaymentSuccess();
            });
        }

        const paymentModal = document.getElementById('paymentModal');
        if (paymentModal) {
            paymentModal.addEventListener('click', (e) => {
                if (e.target.id === 'paymentModal') {
                    this.closePaymentModal();
                }
            });
        }
    }

    simulatePaymentSuccess() {
        const checkButton = document.getElementById('checkPaymentStatus');
        if (!checkButton) return;
        
        checkButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Mengecek...';
        checkButton.disabled = true;
        
        setTimeout(() => {
            this.closePaymentModal();
            this.showPaymentSuccess();
            this.clearCartAfterPayment();
        }, 2000);
    }

    clearCartAfterPayment() {
        this.cart = [];
        this.updateCartUI();
    }

    showPaymentSuccess() {
        const orderId = this.currentOrder?.id || this.generateInvoiceId();
        const totalAmount = this.currentOrder?.total || 0;
        const totalItems = this.currentOrder?.items || 0;
        
        if (!document.getElementById('checkoutModal')) {
            this.createSuccessModal();
        }
        
        const successModal = document.getElementById('checkoutModal');
        const successContent = successModal.querySelector('.modal-content');
        
        if (!successModal || !successContent) return;
        
        successContent.innerHTML = `
            <div class="modal-header">
                <h3>Pembayaran Berhasil!</h3>
                <button id="closeCheckoutModal" class="close-btn">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="payment-success">
                    <div class="success-header">
                        <i class="fas fa-check-circle success-icon"></i>
                        <h2>Pembayaran Berhasil!</h2>
                    </div>
                    
                    <div class="order-details">
                        <div class="detail-row">
                            <span>ID Pesanan:</span>
                            <span class="order-id">${orderId}</span>
                        </div>
                        <div class="detail-row">
                            <span>Total Item:</span>
                            <span>${totalItems} item</span>
                        </div>
                        <div class="detail-row">
                            <span>Total Bayar:</span>
                            <span class="total-amount">${this.formatPrice(totalAmount)}</span>
                        </div>
                        <div class="detail-row">
                            <span>Metode Bayar:</span>
                            <span>E-Wallet (QRIS)</span>
                        </div>
                        <div class="detail-row">
                            <span>Status:</span>
                            <span class="status-paid">✅ LUNAS</span>
                        </div>
                    </div>
                    
                    <div class="success-message">
                        <p>🍽️ Pesanan Anda akan segera diproses oleh dapur!</p>
                        <p>📱 Anda akan menerima notifikasi saat pesanan siap.</p>
                    </div>
                    
                    <div class="success-actions">
                        <button id="printReceipt" class="secondary-btn">
                            <i class="fas fa-print"></i> Cetak Struk
                        </button>
                        <button id="newOrder" class="primary-btn">
                            <i class="fas fa-plus"></i> Pesan Lagi
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        const printBtn = document.getElementById('printReceipt');
        const newOrderBtn = document.getElementById('newOrder');
        const closeBtn = document.getElementById('closeCheckoutModal');
        
        if (printBtn) {
            printBtn.addEventListener('click', () => {
                this.printReceipt(orderId, totalAmount, totalItems);
            });
        }
        
        if (newOrderBtn) {
            newOrderBtn.addEventListener('click', () => {
                this.returnToMainChat();
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.closeCheckoutModal();
            });
        }
        
        successModal.classList.remove('hidden');
        
        this.addMessage(
            `🎉 **Pembayaran Berhasil!**\n\n` +
            `📄 **ID Pesanan:** ${orderId}\n` +
            `💰 **Total:** ${this.formatPrice(totalAmount)}\n` +
            `📱 **Metode:** E-Wallet (QRIS)\n` +
            `📦 **Status:** Pesanan sedang diproses\n\n` +
            `Terima kasih! Pesanan Anda akan segera disiapkan.`,
            'bot'
        );
    }

    createSuccessModal() {
        const modalHTML = `
            <div id="checkoutModal" class="modal hidden">
                <div class="modal-content">
                    <!-- Content will be filled by showPaymentSuccess -->
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    printReceipt(orderId, totalAmount, totalItems) {
        const receiptContent = `
            ================================
            WARUNG KARTIKA SARI
            Jl. Raya Kuliner No. 123
            Telp: (021) 123-4567
            ================================
            
            ID Pesanan: ${orderId}
            Tanggal: ${new Date().toLocaleDateString('id-ID')}
            Waktu: ${new Date().toLocaleTimeString('id-ID')}
            
            --------------------------------
            RINCIAN PESANAN:
            --------------------------------
        `;
        
        let items = '';
        this.currentOrder?.cart?.forEach(item => {
            const itemPrice = item.numericPrice || this.parsePrice(item.price);
            const itemTotal = itemPrice * item.quantity;
            items += `${item.title || 'Menu'}\n`;
            items += `${item.quantity} x ${this.formatPrice(itemPrice)} = ${this.formatPrice(itemTotal)}\n\n`;
        });
        
        const receiptFooter = `
            --------------------------------
            Total Item: ${totalItems}
            Total Bayar: ${this.formatPrice(totalAmount)}
            Metode: E-Wallet (QRIS)
            Status: LUNAS ✅
            ================================
            
            Terima kasih atas kunjungan Anda!
            Selamat menikmati makanan 🍽️
            
            ================================
        `;
        
        const fullReceipt = receiptContent + items + receiptFooter;
        
        const printWindow = window.open('', '_blank');
        if (printWindow) {
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Struk Pembayaran - ${orderId}</title>
                        <style>
                            body { font-family: 'Courier New', monospace; margin: 20px; }
                            pre { white-space: pre-wrap; }
                        </style>
                    </head>
                    <body>
                        <pre>${fullReceipt}</pre>
                        <script>
                            window.onload = function() {
                                window.print();
                                setTimeout(() => window.close(), 1000);
                            }
                        </script>
                    </body>
                </html>
            `);
            printWindow.document.close();
        }
    }

    returnToMainChat() {
        this.closeCheckoutModal();
        this.closePaymentModal();
        
        this.addMessage(
            "🎉 Terima kasih sudah berbelanja! Mau pesan lagi?\n\n" +
            "💡 Ketik menu yang Anda inginkan atau 'menu random' untuk surprise!",
            'bot'
        );
    }

    closePaymentModal() {
        const modal = document.getElementById('paymentModal');
        if (modal) {
            modal.classList.add('hidden');
            
            const checkButton = document.getElementById('checkPaymentStatus');
            if (checkButton) {
                checkButton.innerHTML = 'Cek Status Pembayaran';
                checkButton.disabled = false;
            }
        }
    }

    closeModal() {
        const modal = document.getElementById('menuModal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    closeCheckoutModal() {
        const modal = document.getElementById('checkoutModal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    generateInvoiceId() {
        const now = new Date();
        const dateStr = now.getFullYear().toString().slice(-2) + 
                       (now.getMonth() + 1).toString().padStart(2, '0') + 
                       now.getDate().toString().padStart(2, '0');
        const timeStr = now.getHours().toString().padStart(2, '0') + 
                       now.getMinutes().toString().padStart(2, '0');
        const randomStr = Math.random().toString(36).substr(2, 4).toUpperCase();
        
        return `WKS${dateStr}${timeStr}${randomStr}`;
    }

    formatPrice(price) {
        if (typeof price !== 'number') {
            price = parseFloat(price) || 0;
        }
        return 'Rp ' + price.toLocaleString('id-ID');
    }

    addMessage(text, sender) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'bot' 
            ? '<i class="fas fa-robot"></i>' 
            : '<i class="fas fa-user"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const formattedText = this.formatMessageText(text);
        contentDiv.innerHTML = formattedText;

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 100);
    }

    formatMessageText(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/•/g, '&bull;')
            .replace(/(🍽️|🌶️|🍳|🥘|🏛️|📊|💡|😕|✅|❌|👍|🤔|🎲|📂|🛒|👨‍🍳|🔗|😔|🔍|💭|🎉|✨|🐟|🦐|🥣|🍗|🍯|🥬|📄|💰|📱|🎊|📋|💫|🌟|👋|😊)/g, '<span class="emoji">$1</span>');
    }

    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        chatMessages.innerHTML = `
            <div class="message bot-message">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <p>🔄 Chat telah dibersihkan. Selamat datang kembali!</p>
                    <p>Saya siap membantu Anda mencari menu makanan yang lezat dari database MySQL kami.</p>
                </div>
            </div>
        `;
        
        const menuResults = document.getElementById('menuResults');
        if (menuResults) {
            menuResults.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-utensils"></i>
                    <p>Belum ada menu yang ditampilkan</p>
                    <p class="empty-subtitle">Chat dengan bot untuk mencari menu!</p>
                </div>
            `;
        }
        
        this.updateMenuCount(0);
        this.sessionId = this.generateSessionId();
    }

    setLoading(loading) {
        this.isLoading = loading;
        const sendButton = document.getElementById('sendButton');
        const messageInput = document.getElementById('messageInput');
        const loadingOverlay = document.getElementById('loadingOverlay');
        
        if (sendButton) {
            sendButton.disabled = loading || (messageInput && messageInput.value.trim().length === 0);
        }
        
        if (messageInput) {
            messageInput.disabled = loading;
        }
        
        if (loadingOverlay) {
            if (loading) {
                loadingOverlay.classList.remove('hidden');
            } else {
                loadingOverlay.classList.add('hidden');
            }
        }

        if (sendButton) {
            if (loading) {
                sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            } else {
                sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.menuChatBot = new MenuChatBot();
    
    setInterval(() => {
        if (window.menuChatBot) {
            window.menuChatBot.checkServerConnection();
        }
    }, 30000);
});