// Main UI scripts: Mobile navbar, Alerts, LLM Loading states, Confirmation dialogs
document.addEventListener("DOMContentLoaded", function () {
  // 1. Mobile menu toggle
  const navToggle = document.querySelector(".nav-toggle");
  const navLinks = document.querySelector(".nav-links");
  if (navToggle && navLinks) {
    navToggle.addEventListener("click", function () {
      navLinks.classList.toggle("show");
    });
  }

  // 2. Dismissible alert banners
  document.querySelectorAll(".alert-close").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const alert = btn.closest(".alert");
      if (alert) alert.remove();
    });
  });

  // 3. Destructive confirmation dialogs
  document.querySelectorAll("[data-confirm]").forEach(function (el) {
    el.addEventListener("submit", function (e) {
      const msg = el.getAttribute("data-confirm") || "Are you sure you want to proceed?";
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });

  // 4. Visible loading state on LLM buttons ("Generating...")
  document.querySelectorAll("form.llm-trigger").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      const submitBtn = form.querySelector("button[type='submit'], input[type='submit']");
      if (submitBtn) {
        submitBtn.disabled = true;
        const originalText = submitBtn.innerText || submitBtn.value;
        const loadingText = submitBtn.getAttribute("data-loading-text") || "Generating with AI...";
        if (submitBtn.tagName === "INPUT") {
          submitBtn.value = loadingText;
        } else {
          submitBtn.innerText = loadingText;
        }
        submitBtn.classList.add("loading");
      }
    });
  });

  // 5. Character counter for notes textarea
  const noteTextarea = document.getElementById("note-content-input");
  const charCounter = document.getElementById("char-counter");
  if (noteTextarea && charCounter) {
    const updateCount = function () {
      const len = noteTextarea.value.trim().length;
      charCounter.innerText = `${len.toLocaleString()} characters`;
      if (len < 200 || len > 50000) {
        charCounter.style.color = "#ef4444";
      } else {
        charCounter.style.color = "#10b981";
      }
    };
    noteTextarea.addEventListener("input", updateCount);
    updateCount();
  }
});
