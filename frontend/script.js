document.addEventListener('DOMContentLoaded', () => {
    
    let currentTestId = null;

    // --- Section 1 Elements ---
    const roleInput = document.getElementById('roleInput');
    const generateButton = document.getElementById('generateButton');
    const generateResponse = document.getElementById('generateResponse');
    
    // --- Section 2 Elements ---
    const resumeInput = document.getElementById('resumeInput');
    const analyzeButton = document.getElementById('analyzeButton');
    const analyzeErrorResponse = document.getElementById('analyzeErrorResponse');
    const testContainer = document.getElementById('test-container');
    const mcqContainer = document.getElementById('mcq-container');
    const codingContainer = document.getElementById('coding-container');
    const submitButton = document.getElementById('submit-test-btn');
    
    // --- Results Elements ---
    const finalResultsContainer = document.getElementById('final-results-container');
    const finalResultsDisplay = document.getElementById('final-results-display'); // Changed from -json

    // --- Section 1 Listener ---
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

    // --- Section 2 Listener: Analyze & Generate ---
    analyzeButton.addEventListener('click', async () => {
        const file = resumeInput.files[0];
        if (!file) {
            analyzeErrorResponse.textContent = 'Please select a PDF file first.';
            return;
        }
        
        analyzeErrorResponse.textContent = 'Step 1/2: Analyzing resume...';
        testContainer.style.display = 'none';
        finalResultsContainer.style.display = 'none';
        mcqContainer.innerHTML = '';
        codingContainer.innerHTML = '';

        const formData = new FormData();
        formData.append('file', file);

        try {
            // STEP 1: Analyze
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

            // STEP 2: Generate
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

            // STEP 3: Render
            analyzeErrorResponse.textContent = ''; 
            currentTestId = questionsData.test_id; 
            renderTest(questionsData);
            testContainer.style.display = 'block';

        } catch (error) {
            console.error('Error in analysis/generation chain:', error);
            analyzeErrorResponse.textContent = `Error: ${error.message}.`;
        }
    });

    /**
     * Renders the test questions
     */
    function renderTest(testData) {
        let mcqHtml = '<h3>Multiple Choice Questions:</h3>';
        testData.mcqs.forEach((mcq, index) => {
            mcqHtml += `
                <div class="mcq-question" data-question-text="${mcq.question}">
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

        let codingHtml = '<h3>Coding Questions:</h3>';
        testData.coding_questions.forEach((question, index) => {
            codingHtml += `
                <div class="coding-question" data-question-text="${question}">
                    <h4>${index + 1}. ${question}</h4>
                    <textarea class="code-editor" placeholder="Write your code here..."></textarea>
                </div>
            `;
        });
        codingContainer.innerHTML = codingHtml;
    }

    // --- Section 3 Listener: Submit Test ---
    submitButton.addEventListener('click', async () => {
        if (!currentTestId) {
            alert("No test ID found. Please generate a test first.");
            return;
        }

        testContainer.style.display = 'none';
        analyzeErrorResponse.textContent = 'Grading in progress, please wait...';

        // 1. Scrape MCQ Answers
        const mcqAnswers = [];
        document.querySelectorAll('.mcq-question').forEach((el, index) => {
            const questionText = el.dataset.questionText;
            const selectedOption = el.querySelector(`input[name="mcq-${index}"]:checked`);
            mcqAnswers.push({
                question: questionText,
                answer: selectedOption ? selectedOption.value : "No Answer"
            });
        });

        // 2. Scrape Coding Answers
        const codingAnswers = [];
        document.querySelectorAll('.coding-question').forEach(el => {
            codingAnswers.push(el.querySelector('.code-editor').value);
        });

        const submission = {
            test_id: currentTestId,
            mcq_answers: mcqAnswers,
            coding_answers: codingAnswers
        };

        try {
            // 4. Send to the /submit endpoint
            const response = await fetch('http://127.0.0.1:8000/api/v1/assessment/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(submission)
            });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(`Submission Failed: ${errData.detail}`);
            }
            const resultsData = await response.json();

            // 5. === THIS IS THE UPDATED PART ===
            analyzeErrorResponse.textContent = ''; // Clear loading
            renderResults(resultsData); // Call the new render function
            finalResultsContainer.style.display = 'block';
            currentTestId = null; 

        } catch (error) {
            console.error('Error submitting test:', error);
            analyzeErrorResponse.textContent = `Error: ${error.message}.`;
        }
    });

    /**
     * NEW FUNCTION: Renders the final, styled results
     */
    function renderResults(resultsData) {
        let html = '';

        // 1. Render MCQ Score
        html += `<h3>Final MCQ Score: ${resultsData.mcq_score}</h3>`;
        html += `<h4>MCQ Breakdown:</h4>`;

        // 2. Loop over MCQ results
        resultsData.mcq_results.forEach(mcq => {
            html += `<div class="result-block">`;
            html += `<p class="question">${mcq.question}</p>`;
            
            if (mcq.is_correct) {
                html += `<p class="correct-answer">✓ Your Answer: ${mcq.your_answer}</p>`;
            } else {
                html += `<p class="incorrect-answer">✗ Your Answer: ${mcq.your_answer}</p>`;
                html += `<p class="correct-answer">Correct Answer: ${mcq.correct_answer}</p>`;
            }
            html += `</div>`;
        });

        // 3. Loop over Coding results
        html += `<h4>AI Coding Feedback:</h4>`;
        resultsData.coding_results.forEach((code_result, index) => {
            html += `<div class="result-block">`;
            html += `<p class="question">Coding Question ${index + 1}:</p>`;
            html += `<p>Score: ${code_result.score} / 100</p>`;
            html += `<p>Level: ${code_result.level}</p>`;
            html += `<p class="feedback">Feedback: ${code_result.feedback}</p>`;
            html += `</div>`;
        });

        // 4. Set the final HTML
        finalResultsDisplay.innerHTML = html;
    }

});