(function() {
    const chatFrame = document.createElement('iframe');
    chatFrame.src = "https://chatbot.inanhonglen.com/chat";
    chatFrame.style.position = "fixed";
    chatFrame.style.bottom = "20px";
    chatFrame.style.right = "20px";
    chatFrame.style.width = "350px";
    chatFrame.style.height = "430px";
    chatFrame.style.border = "none";
    chatFrame.style.borderRadius = "10px";
    chatFrame.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
    chatFrame.style.overflow = "hidden";
    chatFrame.style.maxWidth = "100%";
   
    // Tạo nút Icon chat
    const toggleButton = document.createElement('button');
    toggleButton.innerText = "🗨️";
    toggleButton.style.position = "fixed";
    toggleButton.style.bottom = "20px";
    toggleButton.style.right = "20px";
    toggleButton.style.zIndex = "1000"; 
    toggleButton.style.backgroundColor = "#0078d7";
    toggleButton.style.color = "white";
    toggleButton.style.border = "none";
    toggleButton.style.borderRadius = "50%";
    toggleButton.style.width = "50px";
    toggleButton.style.height = "50px";
    toggleButton.style.fontSize = "24px";
    toggleButton.style.cursor = "pointer";
   
    // Lắng nghe sự kiện để mở khung chat khi bấm vào icon
    toggleButton.addEventListener("click", () => {
        toggleButton.style.display = "none";
        closeButton.style.display = "block";
        chatFrame.style.display = "block";
    });

    // Tạo nút đóng ngay trong widget.js
    const closeButton = document.createElement('button');
    closeButton.innerText = "X";
    closeButton.style.position = "fixed";
    closeButton.style.bottom = "430px";
    closeButton.style.right = "10px";
    closeButton.style.backgroundColor = "red";
    closeButton.style.color = "white";
    closeButton.style.border = "none";
    closeButton.style.borderRadius = "50%";
    closeButton.style.width = "30px";
    closeButton.style.height = "30px";
    closeButton.style.cursor = "pointer";

    closeButton.addEventListener("click", () => {
        chatFrame.style.display = "none";
        closeButton.style.display = "none";
        toggleButton.style.display = "block";
    });

    document.body.appendChild(chatFrame);
    document.body.appendChild(toggleButton);
    document.body.appendChild(closeButton);

    //chatFrame.contentWindow.document.body.appendChild(closeButton);

    // Ban đầu ẩn chatFrame, chỉ hiển thị icon
    chatFrame.style.display = "none";
    closeButton.style.display = "none";
})();