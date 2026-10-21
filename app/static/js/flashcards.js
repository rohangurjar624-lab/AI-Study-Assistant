// Flashcard reveal and grading keyboard shortcuts
document.addEventListener("DOMContentLoaded", function () {
  const cardBox = document.getElementById("flashcard-box");
  const revealBtn = document.getElementById("reveal-answer-btn");
  const answerSection = document.getElementById("flashcard-answer-section");
  const gradeSection = document.getElementById("grade-buttons-section");

  if (!cardBox || !revealBtn) return;

  function reveal() {
    if (answerSection) answerSection.style.display = "block";
    if (gradeSection) gradeSection.style.display = "grid";
    revealBtn.style.display = "none";
  }

  revealBtn.addEventListener("click", reveal);
  cardBox.addEventListener("click", reveal);

  // Keyboard accessibility
  document.addEventListener("keydown", function (e) {
    if (e.code === "Space" && answerSection && answerSection.style.display !== "block") {
      e.preventDefault();
      reveal();
    } else if (answerSection && answerSection.style.display === "block") {
      const key = parseInt(e.key, 10);
      if (!isNaN(key) && key >= 0 && key <= 5) {
        const btn = document.querySelector(`.btn-grade-${key}`);
        if (btn) {
          e.preventDefault();
          btn.click();
        }
      }
    }
  });
});
