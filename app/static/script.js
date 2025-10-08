document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll(".minux").forEach(function(minuxBtn) {
        minuxBtn.addEventListener("click", function() {
            var parent = minuxBtn.closest('#customer-list-container'); 
            var currentHeight = parent.offsetHeight;  
            if (currentHeight === 42) {
                parent.style.height = 'auto';  
            } else {
                parent.style.height = '42px'; 
            }
        });
    });
});

function toggleChatWindow(conversationId) {
    const chatWindow = document.getElementById(`chat-window-${conversationId}`);
    chatWindow.classList.toggle('collapsed'); // Thêm hoặc xóa class 'collapsed'
}
