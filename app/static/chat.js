(function() {

    // Lấy cookie
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    // Tạo UUID nếu chưa có
    function generateUUID() {
        return crypto.randomUUID();
    }

    let uid = getCookie("uid");
    if (!uid) {
        uid = generateUUID();
        document.cookie = `uid=${uid}; path=/; max-age=${365*24*3600}`; // lưu 1 năm
    }

    // ---- Tracking gửi về Flask server ----
    fetch("http://localhost:8000/track", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            url: window.location.href,
            ref: document.referrer,
            ua: navigator.userAgent,
            ts: Date.now(),
            uid: uid
        })
    });


    // ---- Tạo iframe chat ----
    const chatFrame = document.createElement('iframe');
    chatFrame.src = "http://localhost:8000/";
    chatFrame.className = "chat-widget-frame";
    chatFrame.style.position = "fixed";
    chatFrame.style.bottom = "20px";
    chatFrame.style.right = "0px";
    chatFrame.style.width = "400px";
    chatFrame.style.height = "500px";
    chatFrame.style.border = "none";
    chatFrame.style.borderRadius = "10px";
    chatFrame.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
    chatFrame.style.overflow = "hidden";
    chatFrame.style.maxWidth = "100%";
    chatFrame.style.maxHeight = "90%";
    chatFrame.style.zIndex = 9999;


    // ---- Icon mở chat ----
    const toggleButton = document.createElement('button');
    toggleButton.innerText = "🗨️";
    toggleButton.style.position = "fixed";
    toggleButton.style.bottom = "20px";
    toggleButton.style.right = "20px";
    toggleButton.style.backgroundColor = "#0078d7";
    toggleButton.style.color = "white";
    toggleButton.style.border = "none";
    toggleButton.style.borderRadius = "50%";
    toggleButton.style.width = "50px";
    toggleButton.style.height = "50px";
    toggleButton.style.fontSize = "24px";
    toggleButton.style.cursor = "pointer";
    toggleButton.style.zIndex = 9999;
    toggleButton.style.padding = "0 0.5rem";
    toggleButton.style.minHeight = "50px";
    toggleButton.style.lineHeight = "1";


    // ---- Nút đóng chat ----
    const closeButton = document.createElement('button');
    closeButton.innerText = "X";
    closeButton.style.position = "fixed";
    closeButton.style.bottom = "475px";
    closeButton.style.right = "-10px";
    closeButton.style.backgroundColor = "red";
    closeButton.style.color = "white";
    closeButton.style.border = "none";
    closeButton.style.borderRadius = "50%";
    closeButton.style.width = "38px";
    closeButton.style.height = "30px";
    closeButton.style.cursor = "pointer";
    closeButton.style.zIndex = 9999;
    closeButton.style.padding = 0;


    // ---- Sự kiện ----
    toggleButton.addEventListener("click", () => {
        toggleButton.style.display = "none";
        closeButton.style.display = "block";
        chatFrame.style.display = "block";
    });

    closeButton.addEventListener("click", () => {
        chatFrame.style.display = "none";
        closeButton.style.display = "none";
        toggleButton.style.display = "block";
    });


    // ---- Thêm vào DOM ----
    document.body.appendChild(chatFrame);
    document.body.appendChild(toggleButton);
    document.body.appendChild(closeButton);


    // ---- Mặc định ẩn ----
    chatFrame.style.display = "none";
    closeButton.style.display = "none";


    // ---- Style mobile ----
    function applyMobileStyle() {
        if (window.innerWidth <= 768) {
            chatFrame.style.right = "0";
            chatFrame.style.left = "0";
            chatFrame.style.width = "100%";
            chatFrame.style.height = "80%";
        }
    }

    applyMobileStyle();
    window.addEventListener("resize", applyMobileStyle);

})();
