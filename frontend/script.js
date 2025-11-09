document.addEventListener('DOMContentLoaded', () => {

    // --- Section 1: Generate Question (Existing Code) ---
    const roleInput = document.getElementById('roleInput');
    const generateButton = document.getElementById('generateButton');
    const generateResponse = document.getElementById('generateResponse');

    generateButton.addEventListener('click', async () => {
        // ... (This function's code is unchanged) ...
        const role = roleInput.value;
        if (!role) {
            generateResponse.textContent = 'Please enter a role first.';
            return;
        }
        generateResponse.textContent = 'Asking the AI...';
        try {
            const response = await fetch('http://127.0.0.1:8000/api/v1/assessment/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
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
            generateResponse.textContent = `Error: ${error.message}.`;
        }
    });

    // --- ------------------------------------------ ---
    // --- Section 2: Analyze Resume & Generate Test (UPDATED) ---
    // --- ------------------------------------------ ---
    const resumeInput = document.getElementById('resumeInput');
    const analyzeButton = document.getElementById('analyzeButton');
    const analyzeResponse = document.getElementById('analyzeResponse');

    analyzeButton.addEventListener('click', async () => {
        const file = resumeInput.files[0];
        if (!file) {
            analyzeResponse.textContent = 'Please select a PDF file first.';
            return;
        }

        analyzeResponse.textContent = 'Step 1/2: Analyzing resume...';
        const formData = new FormData();
        formData.append('file', file);

        try {
            // --- STEP 1: Call /analyze endpoint ---
            const analyzeRes = await fetch('http://127.0.0.1:8000/api/v1/resume/analyze', {
                method: 'POST',
                body: formData,
            });

            if (!analyzeRes.ok) {
                const errData = await analyzeRes.json();
                throw new Error(`Resume Analysis Failed: ${errData.detail}`);
            }

            const skillsData = await analyzeRes.json(); // e.g., {"skills": ["Python", "SQL"]}
            const skills = skillsData.skills;

            if (!skills || skills.length === 0) {
                analyzeResponse.textContent = 'No technical skills found in resume.';
                return;
            }

            analyzeResponse.textContent = `Step 2/2: Found skills (${skills.join(', ')}). Generating test...`;

            // --- STEP 2: Call /generate_from_skills endpoint ---
            const questionsRes = await fetch('http://127.0.0.1:8000/api/v1/assessment/generate_from_skills', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ skills: skills }), // Send the skills we just got
            });

            if (!questionsRes.ok) {
                const errData = await questionsRes.json();
                throw new Error(`Question Generation Failed: ${errData.detail}`);
            }

            const questionsData = await questionsRes.json();

            // 3. Display the final, formatted JSON
            // (JSON.stringify with 'null, 2' formats it nicely)
            analyzeResponse.textContent = JSON.stringify(questionsData, null, 2);

        } catch (error) {
            console.error('Error in analysis/generation chain:', error);
            analyzeResponse.textContent = `Error: ${error.message}. Is your backend server running?`;
        }
    });
});