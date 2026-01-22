document.addEventListener("DOMContentLoaded", () => {
  // Highlight active navigation link
  const sidebarLinks = document.querySelectorAll(".nav a");
  const path = window.location.pathname;

  sidebarLinks.forEach((link) => {
    const href = link.getAttribute("href");
    if (href && (path === href || path.startsWith(href + "/"))) {
      link.classList.add("active");
    }
  });

  // Mark all present button functionality
  const bulkPresent = document.querySelector("#mark-all-present");
  if (bulkPresent) {
    bulkPresent.addEventListener("click", () => {
      document.querySelectorAll(".attendance-row input[type=radio][value=present]").forEach((el) => {
        el.checked = true;
      });
      document.querySelectorAll(".class-card input[type=radio][value=present]").forEach((el) => {
        el.checked = true;
      });
    });
  }
});


