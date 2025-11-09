import { useState } from "react";

export default function App() {
  const [tab, setTab] = useState("generate");
  const [role, setRole] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState("");

  const handleGenerate = async () => {
    setError("");
    setLoading(true);
    setQuestion("");

    try {
      const response = await fetch("http://127.0.0.1:8000/generate-question", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role }),
      });

      if (!response.ok) throw new Error("Backend not reachable");
      const data = await response.json();
      setQuestion(data.question || "No question returned.");
    } catch {
      setError("⚠️ Could not connect to backend. Please check FastAPI server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-blue-100 flex flex-col items-center justify-center p-6">
      <h1 className="text-4xl md:text-5xl font-extrabold text-blue-700 mb-10 drop-shadow-md text-center">
        TalentChain AI Frontend
      </h1>

      {/* Navigation Buttons */}
      <div className="flex flex-wrap gap-3 mb-10">
        {["generate", "evaluate", "resume"].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-6 py-2.5 rounded-xl font-medium transition-all duration-300 shadow-md ${
              tab === t
                ? "bg-blue-600 text-white scale-105"
                : "bg-white text-gray-700 hover:bg-blue-50 border border-gray-300"
            }`}
          >
            {t === "generate"
              ? "Generate Question"
              : t === "evaluate"
              ? "Evaluate Answer"
              : "Resume Analyzer"}
          </button>
        ))}
      </div>

      {/* Card */}
      <div className="w-full max-w-xl bg-white/90 rounded-2xl shadow-xl p-8 border border-gray-100 backdrop-blur-lg">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
          {tab === "generate"
            ? "Generate Assessment Question"
            : tab === "evaluate"
            ? "Evaluate Candidate Answer"
            : "Analyze Resume"}
        </h2>

        {tab === "generate" && (
          <>
            <div className="flex gap-3 mb-5">
              <input
                type="text"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                placeholder="Enter role (e.g. Python Developer)"
                className="flex-1 border border-gray-300 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleGenerate}
                disabled={loading}
                className={`px-5 py-2 rounded-xl text-white font-medium transition-all duration-300 ${
                  loading
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-700 shadow-md"
                }`}
              >
                {loading ? "Generating..." : "Generate"}
              </button>
            </div>

            {error && (
              <p className="text-red-500 font-medium bg-red-50 border border-red-200 p-3 rounded-lg text-sm">
                {error}
              </p>
            )}

            {question && (
              <div className="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-100 text-gray-800 shadow-inner">
                <p className="font-semibold mb-1 text-blue-800">
                  Generated Question:
                </p>
                <p>{question}</p>
              </div>
            )}
          </>
        )}
      </div>

      <footer className="mt-10 text-gray-500 text-sm">
        © {new Date().getFullYear()} TalentChain AI — Crafted with 💙 using
        React & FastAPI
      </footer>
    </div>
  );
}
