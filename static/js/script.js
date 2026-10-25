document.addEventListener("DOMContentLoaded", () => {
  /* -------------------------------------------------------------- */
  /* Countdown                                                       */
  /* -------------------------------------------------------------- */
  const countdownEl = document.getElementById("countdown");
  const targetDate = new Date(countdownEl.dataset.event).getTime();

  const dEl = document.getElementById("cd-days");
  const hEl = document.getElementById("cd-hours");
  const mEl = document.getElementById("cd-minutes");
  const sEl = document.getElementById("cd-seconds");

  function pad(n) { return String(n).padStart(2, "0"); }

  function updateCountdown() {
    const now = Date.now();
    let diff = targetDate - now;

    if (diff <= 0) {
      dEl.textContent = hEl.textContent = mEl.textContent = sEl.textContent = "00";
      return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
    const minutes = Math.floor((diff / (1000 * 60)) % 60);
    const seconds = Math.floor((diff / 1000) % 60);

    dEl.textContent = pad(days);
    hEl.textContent = pad(hours);
    mEl.textContent = pad(minutes);
    sEl.textContent = pad(seconds);
  }

  updateCountdown();
  setInterval(updateCountdown, 1000);

  /* -------------------------------------------------------------- */
  /* Mobile nav toggle                                                */
  /* -------------------------------------------------------------- */
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");

  navToggle.addEventListener("click", () => {
    navLinks.classList.toggle("open");
  });

  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => navLinks.classList.remove("open"));
  });

  /* -------------------------------------------------------------- */
  /* Scroll-spy: highlight the active nav link per visible section   */
  /* -------------------------------------------------------------- */
  const sections = document.querySelectorAll("main section[id]");
  const navItems = document.querySelectorAll(".nav-link");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute("id");
          navItems.forEach((link) => {
            link.classList.toggle("active", link.dataset.section === id);
          });
        }
      });
    },
    { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
  );

  sections.forEach((section) => observer.observe(section));

  /* -------------------------------------------------------------- */
  /* Registration form (AJAX, no page reload)                        */
  /* -------------------------------------------------------------- */
  const form = document.getElementById("registerForm");
  const errorEl = document.getElementById("formError");
  const confirmation = document.getElementById("confirmation");
  const confirmationText = document.getElementById("confirmationText");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";

    const payload = {
      full_name: document.getElementById("full_name").value,
      institution: document.getElementById("institution").value,
      email: document.getElementById("email").value,
      phone: document.getElementById("phone").value,
      workshop: document.getElementById("workshop").value,
    };

    const submitBtn = form.querySelector("button[type=submit]");
    submitBtn.disabled = true;
    submitBtn.textContent = "جارٍ الإرسال...";

    try {
      const res = await fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!res.ok || !data.ok) {
        errorEl.textContent = data.error || "حدث خطأ أثناء التسجيل. حاول مرة أخرى.";
        submitBtn.disabled = false;
        submitBtn.textContent = "تأكيد التسجيل";
        return;
      }

      confirmationText.textContent = data.message;
      confirmation.hidden = false;
      form.hidden = true;
    } catch (err) {
      errorEl.textContent = "تعذّر الاتصال بالخادم. تحقق من تشغيل التطبيق.";
      submitBtn.disabled = false;
      submitBtn.textContent = "تأكيد التسجيل";
    }
  });
});
