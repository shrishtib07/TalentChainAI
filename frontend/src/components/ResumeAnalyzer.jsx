import React, { useState } from "react";
import axios from "axios";

const ResumeAnalyzer = () => {
  const [file, setFile] = useState(null);
  const [skills, setSkills] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      setError("Please upload a PDF resume.");
      return;
    }

    setError("");
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/v1/resume/analyze",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setSkills(response.data.skills || []);
    } catch (err) {
      console.error(err);
      setError("⚠️ Could not connect to backend or invalid PDF.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4 text-gray-800">
        Resume Analyzer
      </h2>
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />
      <br />
      <button
        onClick={handleUpload}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        disabled={loading}
      >
        {loading ? "Analyzing..." : "Upload & Analyze"}
      </button>

      {error && (
        <div className="mt-4 text-red-500 font-semibold">{error}</div>
      )}

      {skills.length > 0 && (
        <div className="mt-4 p-4 bg-gray-100 rounded border">
          <strong>Extracted Skills:</strong>
          <ul className="list-disc ml-5 mt-2 text-gray-700">
            {skills.map((skill, i) => (
              <li key={i}>{skill}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResumeAnalyzer;
