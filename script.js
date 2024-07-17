function toggleChatbot() {
    var chatbot = document.getElementById("chatbot");
    if (chatbot.style.display === "none" || chatbot.style.display === "") {
        chatbot.style.display = "block";
    } else {
        chatbot.style.display = "none";
    }
}