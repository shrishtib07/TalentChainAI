document.addEventListener('DOMContentLoaded', () => {
    const roleInput = document.getElementById('roleInput');
    const generateButton = document.getElementById('generateButton');
    const generateResponse = document.getElementById('generateResponse');

    generateButton.addEventListener('click', async () => {
        const role = roleInput.value;
        if (!role) {
            generateResponse.textContent = 'Please enter a role first.';
            return;
        }

        generateResponse.textContent = 'Asking the AI...';

        try {
            // This is the JavaScript "fetch" call to your FastAPI backend
            const response = await fetch('http://127.0.0.1:8000/api/v1/assessment/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ role: role }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            
            // Display the AI's question on the page
            generateResponse.textContent = data.question;

        } catch (error) {
            console.error('Error fetching data:', error);
            generateResponse.textContent = `Error: ${error.message}. Is your backend server running?`;
        }
    });
});