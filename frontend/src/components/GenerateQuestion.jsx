import React, { useState } from "react";
import axios from "axios";

const GenerateQuestion = () => {
  const [jobRole, setJobRole] = useState("");
  const [question, setQuestion] = useState("");
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!jobRole) {
      setError("Please enter a job role.");
      return;
    }

    try {
      setError("");
      setQuestion("Generating question...");
      const response = await axios.post(
        "http://127.0.0.1:8000/api/v1/assessment/generate",
        { role: jobRole },
        { headers: { "Content-Type": "application/json" } }
      );
      setQuestion(response.data.question);
    } catch (err) {
      console.error(err);
      setError("⚠️ Could not connect to backend. Please check FastAPI.");
      setQuestion("");
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4 text-gray-800">
        Generate Assessment Question
      </h2>
      <input
        type="text"
        placeholder="Enter Job Role (e.g., Python Developer)"
        value={jobRole}
        onChange={(e) => setJobRole(e.target.value)}
        className="w-full border p-2 rounded mb-4"
      />
      <button
        onClick={handleGenerate}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Generate
      </button>

      {question && (
        <div className="mt-4 p-4 bg-gray-100 rounded border">
          <strong>Generated Question:</strong>
          <p className="mt-2 text-gray-700">{question}</p>
        </div>
      )}

      {error && (
        <div className="mt-4 text-red-500 font-semibold">{error}</div>
      )}
    </div>
  );
};

export default GenerateQuestion;
