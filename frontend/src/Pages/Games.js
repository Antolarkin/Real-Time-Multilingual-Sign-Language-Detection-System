import React, { useState } from "react";
import {
  CheckCircle,
  XCircle,
  Trophy,
  RotateCcw,
  Star,
  Clock,
  Target,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import "../css/Quiz.css";
import A from "../Assets/isl_dataset/a.jpg"
import B from "../Assets/isl_dataset/b.jpg";
import C from "../Assets/isl_dataset/c.jpg";
import D from "../Assets/isl_dataset/d.jpg";


const Games = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [gameStarted, setGameStarted] = useState(false);

const questions = [
  {
    id: 1,
    question: "Which sign represents the letter 'A'?",
    options: [
      {
        id: "a",
        image: A,
        label: "Option A",
      },
      {
        id: "b",
        image: B,
        label: "Option B",
      },
      {
        id: "c",
        image: C,
        label: "Option C",
      },
      {
        id: "d",
        image: D,
        label: "Option D",
      },
    ],
    correct: "a",
  },
  {
    id: 2,
    question: "Which sign represents the letter 'B'?",
    options: [
      {
        id: "b",
        image: B,
        label: "Option B",
      },
      {
        id: "c",
        image: C,
        label: "Option C",
      },
      {
        id: "a",
        image: A,
        label: "Option A",
      },
      {
        id: "d",
        image: D,
        label: "Option D",
      },
      {
        id: "c",
        image: C,
        label: "Option C",
      },
    ],
    correct: "b",
  },
  {
    id: 3,
    question: "Which sign represents the letter 'C'?",
    options: [
      {
        id: "c",
        image: C,
        label: "Option C",
      },
      {
        id: "a",
        image: A,
        label: "Option A",
      },
      {
        id: "b",
        image: B,
        label: "Option B",
      },

      {
        id: "d",
        image: D,
        label: "Option D",
      },
    ],
    correct: "c",
  },
  {
    id: 4,
    question: "Which sign represents the letter 'D'?",
    options: [
      {
        id: "a",
        image: A,
        label: "Option A",
      },
      {
        id: "d",
        image: D,
        label: "Option D",
      },
      {
        id: "b",
        image: B,
        label: "Option B",
      },
      {
        id: "c",
        image: C,
        label: "Option C",
      },
    ],
    correct: "d",
  },
  {
    id: 5,
    question: "Which sign represents the letter 'E'?",
    options: [
      {
        id: "b",
        image: B,
        label: "Option B",
      },
      {
        id: "c",
        image: C,
        label: "Option C",
      },
      {
        id: "a",
        image: A,
        label: "Option A",
      },
      {
        id: "d",
        image: D,
        label: "Option D",
      },
    ],
    correct: "a",
  },
];

  const handleAnswerSelect = (questionId, answerId) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: answerId,
    }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = () => {
    setShowResults(true);
  };

  const calculateScore = () => {
    let correct = 0;
    questions.forEach((question) => {
      if (selectedAnswers[question.id] === question.correct) {
        correct++;
      }
    });
    return correct;
  };

  const resetGame = () => {
    setCurrentQuestion(0);
    setSelectedAnswers({});
    setShowResults(false);
    setGameStarted(false);
  };

  const getScoreColor = (score) => {
    if (score >= 4) return "quiz-result-correct";
    if (score >= 3) return "text-amber-600";
    return "quiz-result-incorrect";
  };

  const getScoreMessage = (score) => {
    if (score >= 4) return "Outstanding! 🌟";
    if (score >= 3) return "Great job! 👏";
    return "Keep practicing! 💪";
  };

  if (!gameStarted) {
    return (
      <div className="quiz-container">
        <div className="quiz-card">
          <div>
            <div className="quiz-icon-container quiz-icon-primary">
              <Target size={40} />
            </div>
            <h1 className="quiz-header">Sign Language Quiz</h1>
            <p className="quiz-text">
              Test your knowledge with {questions.length} challenging questions!
            </p>
          </div>

          <div className="quiz-feature-list">
            <div className="quiz-feature-item">
              <Clock size={20} />
              <span>{questions.length} Questions</span>
            </div>
            <div className="quiz-feature-item">
              <Star size={20} />
              <span>Image-based MCQs</span>
            </div>
            <div className="quiz-feature-item">
              <Trophy size={20} />
              <span>Instant Results</span>
            </div>
          </div>

          <button
            onClick={() => setGameStarted(true)}
            className="quiz-button"
            style={{ width: "100%" }}
          >
            Start Quiz
          </button>
        </div>
      </div>
    );
  }

  if (showResults) {
    const score = calculateScore();
    const percentage = (score / questions.length) * 100;

    return (
      <div className="quiz-container">
        <div className="quiz-card">
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <div className="quiz-icon-container quiz-icon-success">
              <Trophy size={40} />
            </div>
            <h2 className="quiz-header">Quiz Complete!</h2>
            <div className={`quiz-score-large ${getScoreColor(score)}`}>
              {score}/{questions.length}
            </div>
            <div className="quiz-score-percentage">
              {percentage.toFixed(0)}%
            </div>
            <div className="quiz-score-message">{getScoreMessage(score)}</div>
          </div>

          <div className="quiz-results-container quiz-scrollable">
            {questions.map((question, index) => {
              const userAnswer = selectedAnswers[question.id];
              const isCorrect = userAnswer === question.correct;
              const correctOption = question.options.find(
                (opt) => opt.id === question.correct
              );
              const selectedOption = question.options.find(
                (opt) => opt.id === userAnswer
              );

              return (
                <div key={question.id} className="quiz-result-item">
                  <div
                    style={{
                      display: "flex",
                      alignItems: "flex-start",
                      gap: "1rem",
                    }}
                  >
                    <div style={{ flexShrink: 0 }}>
                      {isCorrect ? (
                        <CheckCircle
                          className="quiz-result-correct"
                          size={24}
                        />
                      ) : (
                        <XCircle className="quiz-result-incorrect" size={24} />
                      )}
                    </div>
                    <div style={{ flex: 1 }}>
                      <h3
                        style={{
                          fontWeight: 600,
                          color: "#1e293b",
                          marginBottom: "0.75rem",
                        }}
                      >
                        {index + 1}. {question.question}
                      </h3>
                      <div className="quiz-answer-grid">
                        {question.options.map((option) => {
                          const isUserSelection = option.id === userAnswer;
                          const isCorrectAnswer =
                            option.id === question.correct;

                          let optionClass = "quiz-answer-option";
                          if (isCorrectAnswer) {
                            optionClass += " quiz-answer-correct";
                          } else if (isUserSelection && !isCorrect) {
                            optionClass += " quiz-answer-incorrect";
                          }

                          return (
                            <div key={option.id} className={optionClass}>
                              <img
                                src={option.image}
                                alt={option.label}
                                style={{
                                  width: "100%",
                                  height: "6rem",
                                  objectFit: "cover",
                                  borderRadius: "0.375rem",
                                }}
                              />
                              {isCorrectAnswer && (
                                <CheckCircle
                                  style={{
                                    position: "absolute",
                                    top: "-0.5rem",
                                    right: "-0.5rem",
                                    width: "1.25rem",
                                    height: "1.25rem",
                                    color: "#059669",
                                    backgroundColor: "white",
                                    borderRadius: "50%",
                                  }}
                                />
                              )}
                              {isUserSelection && !isCorrect && (
                                <XCircle
                                  style={{
                                    position: "absolute",
                                    top: "-0.5rem",
                                    right: "-0.5rem",
                                    width: "1.25rem",
                                    height: "1.25rem",
                                    color: "#dc2626",
                                    backgroundColor: "white",
                                    borderRadius: "50%",
                                  }}
                                />
                              )}
                            </div>
                          );
                        })}
                      </div>
                      <div className="quiz-answer-feedback">
                        <span style={{ color: "#64748b" }}>
                          Correct answer:{" "}
                        </span>
                        <span style={{ fontWeight: 600, color: "#059669" }}>
                          {correctOption?.label}
                        </span>
                        {selectedOption && !isCorrect && (
                          <>
                            <span
                              style={{ color: "#64748b", marginLeft: "1rem" }}
                            >
                              Your answer:{" "}
                            </span>
                            <span style={{ fontWeight: 600, color: "#dc2626" }}>
                              {selectedOption.label}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ textAlign: "center" }}>
            <button onClick={resetGame} className="quiz-button">
              <RotateCcw size={20} />
              <span>Play Again</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  const progress = ((currentQuestion + 1) / questions.length) * 100;
  const question = questions[currentQuestion];
  const selectedAnswer = selectedAnswers[question.id];

  return (
    <div className="quiz-container">
      <div style={{ maxWidth: "64rem", width: "100%" }}>
        <div className="quiz-card">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "1rem",
            }}
          >
            <h1
              className="quiz-header"
              style={{ fontSize: "1.5rem", margin: 0 }}
            >
              Sign Language Quiz
            </h1>
            <div
              style={{
                fontSize: "1.125rem",
                fontWeight: 600,
                color: "#64748b",
              }}
            >
              {currentQuestion + 1} / {questions.length}
            </div>
          </div>

          <div className="progress-container">
            <div
              className="progress-bar"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        <div className="quiz-card">
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <h2
              className="quiz-header"
              style={{ fontSize: "1.5rem", marginBottom: "1rem" }}
            >
              {question.question}
            </h2>
            <p className="quiz-text">Select the correct sign image</p>
          </div>

          <div className="quiz-options-grid">
            {question.options.map((option) => (
              <div
                key={option.id}
                onClick={() => handleAnswerSelect(question.id, option.id)}
                className={`option-card ${
                  selectedAnswer === option.id ? "selected" : ""
                }`}
              >
                <div style={{ position: "relative" }}>
                  <img
                    src={option.image}
                    alt={option.label}
                    className="quiz-image"
                  />
                  {selectedAnswer === option.id && (
                    <div
                      style={{
                        position: "absolute",
                        inset: 0,
                        backgroundColor: "rgba(79, 70, 229, 0.1)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <div
                        style={{
                          width: "2.5rem",
                          height: "2.5rem",
                          backgroundColor: "#4f46e5",
                          borderRadius: "50%",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        <CheckCircle size={24} color="white" />
                      </div>
                    </div>
                  )}
                </div>
                <div style={{ padding: "1rem", textAlign: "center" }}>
                  <span style={{ fontWeight: 600, color: "#374151" }}>
                    {option.label}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="quiz-navigation">
            <button
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
              className={`quiz-button quiz-button-secondary ${
                currentQuestion === 0 ? "disabled" : ""
              }`}
              style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
            >
              <ChevronLeft size={20} />
              <span>Previous</span>
            </button>

            <div className="quiz-status">
              {selectedAnswer ? "Answer selected ✓" : "Select an answer"}
            </div>

            {currentQuestion === questions.length - 1 ? (
              <button
                onClick={handleSubmit}
                disabled={
                  Object.keys(selectedAnswers).length < questions.length
                }
                className={`quiz-button quiz-button-success ${
                  Object.keys(selectedAnswers).length < questions.length
                    ? "disabled"
                    : ""
                }`}
              >
                Submit Quiz
              </button>
            ) : (
              <button
                onClick={handleNext}
                disabled={!selectedAnswer}
                className={`quiz-button ${!selectedAnswer ? "disabled" : ""}`}
                style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
              >
                <span>Next</span>
                <ChevronRight size={20} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Games;
