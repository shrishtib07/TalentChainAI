import React, { useState } from "react";
import axios from "axios";

export default function EvaluateAnswer() {
  const [skill, setSkill] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleEvaluate = async () => {
    setResult(null);
    setError("");
    try {
      const res = await axios.post("http://172.24.67.69:8000/api/v1/assessment/evaluate", 
        {
        skill,
        question,
        answer,
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError("⚠️ Could not connect to backend.");
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-3">Evaluate Candidate Answer</h2>
      <input
        type="text"
        value={skill}
        onChange={(e) => setSkill(e.target.value)}
        placeholder="Skill (e.g. Python)"
        className="border p-2 rounded w-full mb-3"
      />
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Enter the question"
        className="border p-2 rounded w-full mb-3"
      />
      <textarea
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        placeholder="Enter the candidate's answer"
        className="border p-2 rounded w-full mb-3"
      />
      <button
        onClick={handleEvaluate}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Evaluate
      </button>

      {error && <p className="text-red-500 mt-3">{error}</p>}

      {result && (
        <div className="mt-4 bg-gray-100 p-4 rounded">
          <strong>Score:</strong> {result.score}
          <br />
          <strong>Level:</strong> {result.level}
          <br />
          <strong>Feedback:</strong> {result.feedback}
        </div>
      )}
    </div>
  );
}
