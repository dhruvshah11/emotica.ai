
// Initialize webcam
const video = document.getElementById('videoElement');
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(error => {
        console.error('Error accessing webcam:', error);
    });

const chatbox = document.getElementById('chatbox');
const userInput = document.getElementById('user_input');
const sendButton = document.getElementById('send_button');


function appendMessage(message, sender) {
const messageDiv = document.createElement('div');
messageDiv.classList.add('message', `${sender}-message`);
messageDiv.textContent = message;
chatbox.appendChild(messageDiv);
chatbox.scrollTop = chatbox.scrollHeight;
}



function sendMessage() {
const userMessage = userInput.value;
appendMessage(userMessage, 'user'); // Append user message
userInput.value = ''; // Clear input field

// Capture webcam frame
const canvas = document.createElement('canvas');
canvas.width = video.videoWidth;
canvas.height = video.videoHeight;
canvas.getContext('2d').drawImage(video, 0, 0);
const imageData = canvas.toDataURL('image/jpeg'); // Or 'image/png'

fetch('/get_emotion', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: userMessage, image_data: imageData }) // Include image data
})

.then(response => response.json())
.then(data => {
    const botMessage = data.advice ;  // Access advice directly
    appendMessage(botMessage, 'bot'); // Append bot's advice

})
.catch(error => console.error('Error:', error));
}




sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', function (event) {
if (event.key === 'Enter') {
sendMessage();
}
});