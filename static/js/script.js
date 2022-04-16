const flashMessages = document.querySelectorAll(".flash-message");

for (let i = 0; i < flashMessages.length; i++) {
  const flashMessage = flashMessages[i];
  setTimeout(() => {
    flashMessage.classList.add("hidden");
  }, 5000);
}
