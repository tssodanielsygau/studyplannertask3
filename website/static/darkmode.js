document.addEventListener("DOMContentLoaded", () => {
  const themeSwitch = document.getElementById('theme-switch');

  const enableDarkmode = () => {
    document.body.classList.add('darkmode');
    localStorage.setItem('darkmode', 'enabled');
  };

  const disableDarkmode = () => {
    document.body.classList.remove('darkmode');
    localStorage.setItem('darkmode', 'disabled');
  };

  // Load stored preference
  if (localStorage.getItem('darkmode') === 'enabled') {
    enableDarkmode();
  }

  // Toggle on click
  if (themeSwitch) {
    themeSwitch.addEventListener('click', () => {
      const darkmode = localStorage.getItem('darkmode');
      darkmode !== 'enabled' ? enableDarkmode() : disableDarkmode();
    });
  }
});
