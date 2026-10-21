// Quiz timer tracking
document.addEventListener("DOMContentLoaded", function () {
  const timerDisplay = document.getElementById("quiz-timer-display");
  const durationInput = document.getElementById("duration-seconds-input");

  if (!timerDisplay || !durationInput) return;

  let seconds = 0;
  const timerInterval = setInterval(function () {
    seconds++;
    durationInput.value = seconds;

    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    timerDisplay.innerText = `⏱ ${mins < 10 ? "0" : ""}${mins}:${secs < 10 ? "0" : ""}${secs}`;
  }, 1000);

  // Clear interval on form submission
  const quizForm = document.getElementById("quiz-form");
  if (quizForm) {
    quizForm.addEventListener("submit", function () {
      clearInterval(timerInterval);
    });
  }
});
