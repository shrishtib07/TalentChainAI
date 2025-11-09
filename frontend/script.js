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
    const analyzeErrorResponse = document.getElementById('analyzeErrorResponse');
    
    const testContainer = document.getElementById('test-container');
    const mcqContainer = document.getElementById('mcq-container');
    const codingContainer = document.getElementById('coding-container');

    analyzeButton.addEventListener('click', async () => {
        const file = resumeInput.files[0];
        if (!file) {
            analyzeErrorResponse.textContent = 'Please select a PDF file first.';
            return;
        }
        
        // Clear old results and show "loading"
        analyzeErrorResponse.textContent = 'Step 1/2: Analyzing resume...';
        testContainer.style.display = 'none';
        mcqContainer.innerHTML = '';
        codingContainer.innerHTML = '';

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

            const skillsData = await analyzeRes.json();
            const skills = skillsData.skills;

            if (!skills || skills.length === 0) {
                analyzeErrorResponse.textContent = 'No technical skills found in resume.';
                return;
            }

            analyzeErrorResponse.textContent = `Step 2/2: Found skills (${skills.join(', ')}). Generating test...`;

            // --- STEP 2: Call /generate_from_skills endpoint ---
            const questionsRes = await fetch('http://127.0.0.1:8000/api/v1/assessment/generate_from_skills', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ skills: skills }),
            });

            if (!questionsRes.ok) {
                const errData = await questionsRes.json();
                throw new Error(`Question Generation Failed: ${errData.detail}`);
            }

            const questionsData = await questionsRes.json();

            // --- STEP 3: Render the test on the page ---
            analyzeErrorResponse.textContent = ''; // Clear errors
            renderTest(questionsData); // Call the new render function
            testContainer.style.display = 'block'; // Show the test

        } catch (error) {
            console.error('Error in analysis/generation chain:', error);
            analyzeErrorResponse.textContent = `Error: ${error.message}. Is your backend server running?`;
        }
    });

    /**
     * NEW FUNCTION: Renders the test from the JSON data.
     */
    function renderTest(testData) {
        // 1. Render MCQs
        let mcqHtml = '<h3>Multiple Choice Questions:</h3>';
        testData.mcqs.forEach((mcq, index) => {
            mcqHtml += `
                <div class="mcq-question">
                    <h4>${index + 1}. ${mcq.question}</h4>
                    ${mcq.options.map((option, i) => `
                        <label class="mcq-option">
                            <input type="radio" name="mcq-${index}" value="${option}">
                            ${option}
                        </label>
                    `).join('')}
                </div>
            `;
        });
        mcqContainer.innerHTML = mcqHtml;

        // 2. Render Coding Questions
        let codingHtml = '<h3>Coding Questions:</h3>';
        testData.coding_questions.forEach((question, index) => {
            codingHtml += `
                <div class="coding-question">
                    <h4>${index + 1}. ${question}</h4>
                    <textarea class="code-editor" placeholder="Write your code here..."></textarea>
                </div>
            `;
        });
        codingContainer.innerHTML = codingHtml;
    }
});