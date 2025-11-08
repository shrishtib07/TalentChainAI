document.addEventListener('DOMContentLoaded', () => {

    // --- Section 1: Generate Question (Existing Code) ---
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
            const response = await fetch('http://127.0.0.1:8000/api/v1/assessment/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ role: role }),
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || `HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            generateResponse.textContent = data.question;

        } catch (error) {
            console.error('Error fetching data:', error);
            generateResponse.textContent = `Error: ${error.message}. Is your backend server running?`;
        }
    });

    // --- ------------------------------------------ ---
    // --- Section 2: Analyze Resume (New Code) ---
    // --- ------------------------------------------ ---
    const resumeInput = document.getElementById('resumeInput');
    const analyzeButton = document.getElementById('analyzeButton');
    const analyzeResponse = document.getElementById('analyzeResponse');

    analyzeButton.addEventListener('click', async () => {
        const file = resumeInput.files[0];
        
        // --- Client-side validation ---
        if (!file) {
            analyzeResponse.textContent = 'Please select a PDF file first.';
            return;
        }
        if (file.type !== 'application/pdf') {
            analyzeResponse.textContent = 'Error: Please upload a PDF file.';
            return;
        }

        analyzeResponse.textContent = 'Analyzing resume...';

        // 1. Create FormData to send the file
        const formData = new FormData();
        formData.append('file', file); // 'file' MUST match the backend parameter name: File(...)

        try {
            // 2. Send the FormData to the new endpoint
            const response = await fetch('http://127.0.0.1:8000/api/v1/resume/analyze', {
                method: 'POST',
                body: formData,
                // NOTE: DO NOT set 'Content-Type' header. 
                // The browser does it automatically for FormData.
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || `HTTP error! Status: ${response.status}`);
            }

            // 3. Display the JSON response
            const data = await response.json(); // e.g., {"skills": ["Python", "SQL"]}
            
            if (data.skills && data.skills.length > 0) {
                // Format the skills list into a nice string
                analyzeResponse.textContent = `Skills found: ${data.skills.join(', ')}`;
            } else {
                analyzeResponse.textContent = 'No specific technical skills found.';
            }

        } catch (error) {
            console.error('Error analyzing resume:', error);
            analyzeResponse.textContent = `Error: ${error.message}. Is your backend server running?`;
        }
    });

});