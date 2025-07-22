// ---------- MODAL FUNCTIONS ----------
function openEditModal(id) {
  document.querySelectorAll('.event-modal').forEach(modal => {
    modal.style.display = 'none';
  });
  const modal = document.getElementById(`modal-${id}`);
  if (modal) modal.style.display = 'flex';
}

function closeEditModal(id) {
  const modal = document.getElementById(`modal-${id}`);
  if (modal) modal.style.display = 'none';
}

function openEventModal() {
  document.getElementById('event-modal').style.display = 'flex';
}

function closeEventModal() {
  document.getElementById('event-modal').style.display = 'none';
}

// ---------- LOCAL TIME DISPLAY ----------
function updateTime() {
  const options = {
    timeZone: "Australia/Sydney",
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
    weekday: 'long'
  };
  const now = new Date().toLocaleTimeString('en-AU', options);
  document.getElementById("local-time").innerText = now;
}
updateTime();
setInterval(updateTime, 30000);

// ---------- FLASH MESSAGE ----------
function showFlashMessage(message, category = "info") {
  const container = document.getElementById("flash-messages");
  if (!container) return;

  const flash = document.createElement("div");
  flash.className = `flash-message ${category}`;
  flash.textContent = message;
  container.appendChild(flash);
  setTimeout(() => {
    flash.style.opacity = "0";
    setTimeout(() => flash.remove(), 300);
  }, 3500);
}

// ---------- EVENT DESCRIPTION TOGGLE ----------
function toggleDescription(id) {
  const desc = document.getElementById(`desc-${id}`);
  const btn = event.target;
  desc.classList.toggle('clamp');
  btn.textContent = desc.classList.contains('clamp') ? 'Read more' : 'Show less';
}

// ---------- SCROLL EVENTS CAROUSEL ----------
function scrollCarousel(direction) {
  const container = document.getElementById('carousel');
  const cardWidth = 280 + 16;
  container.scrollBy({ left: direction * cardWidth * 4, behavior: 'smooth' });
}

// ---------- DELETE FUNCTIONS ----------
function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId }),
    headers: { "Content-Type": "application/json" }
  }).then(res => res.json()).then(data => {
    if (data.success) {
      const noteElement = document.getElementById(`note-${noteId}`);
      if (noteElement) noteElement.remove();
    } else alert("Failed to delete note.");
  });
}

function deleteReminder(reminderId) {
  fetch("/delete-reminder", {
    method: "POST",
    body: JSON.stringify({ id: reminderId }),
    headers: { "Content-Type": "application/json" }
  }).then(res => res.json()).then(data => {
    if (data.success) {
      const reminderEl = document.getElementById(`reminder-${reminderId}`);
      if (reminderEl) reminderEl.remove();
      showFlashMessage("Reminder deleted.", "success");
    } else alert(data.error || "Failed to delete reminder.");
  });
}

// ---------- FORMAT DATE ----------
function formatDate(isoDate) {
  const [year, month, day] = isoDate.split("-");
  return `${day}/${month}/${year}`;
}

// ---------- DOM READY ----------
document.addEventListener("DOMContentLoaded", function () {
  // Add Event
  const form = document.getElementById("event-form");
  const grid = document.querySelector(".events-grid");

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const data = new FormData(form);
      const payload = Object.fromEntries(data.entries());

      fetch("/", {
        method: "POST",
        body: new URLSearchParams(payload),
        headers: { "X-Requested-With": "XMLHttpRequest" }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.html) {
          const div = document.createElement("div");
          div.innerHTML = data.html;
          const newCard = div.firstElementChild;
          newCard.style.minWidth = "260px";
          newCard.style.flex = "0 0 auto";
          const addCard = document.querySelector(".event-card[onclick]");
          grid.insertBefore(newCard, addCard);
          form.reset();
          closeEventModal();
          setTimeout(() => newCard.scrollIntoView({ behavior: "smooth", inline: "start" }), 100);
          if (data.message) showFlashMessage(data.message, 'success');
        } else alert("Error adding event.");
      });
    });
  }

  // Add Note
  const noteForm = document.getElementById("note-form");
  const noteInput = document.getElementById("note-input");
  const notesList = document.getElementById("notes");

  if (noteForm) {
    noteForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const note = noteInput.value.trim();
      if (note.length < 1) return alert("Note is too short.");

      fetch("/", {
        method: "POST",
        body: JSON.stringify({ note }),
        headers: { "Content-Type": "application/json" }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.note_id) {
          const newNote = document.createElement("li");
          newNote.id = `note-${data.note_id}`;
          newNote.style = "margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;";
          newNote.innerHTML = `<span>${note}</span><button onclick="deleteNote(${data.note_id})" style="background: none; border: none; color: var(--text-secondary); font-size: 20px; cursor: pointer;">&times;</button>`;
          notesList.prepend(newNote);
          noteInput.value = "";
          showFlashMessage("Note added!", "success");
        } else alert("Error adding note.");
      });
    });
  }

  // Add Reminder
  const reminderForm = document.getElementById("reminder-form");
  const reminderList = document.getElementById("reminder-list");

  if (reminderForm) {
    reminderForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const contentInput = reminderForm.querySelector('input[name="reminder_content"]');
      const dueInput = reminderForm.querySelector('input[name="reminder_due"]');
      const content = contentInput.value.trim();
      const due_date = dueInput.value;

      if (!content || !due_date) return alert("Both content and due date are required.");

      fetch("/add-reminder", {
        method: "POST",
        body: JSON.stringify({ content, due_date }),
        headers: { "Content-Type": "application/json" }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const newReminder = document.createElement("li");
          newReminder.id = `reminder-${data.id}`;
          newReminder.style = "display: flex; justify-content: space-between; align-items: center; border: 1px solid var(--border-color); border-radius: 8px; padding: 0.75rem 1rem; background-color: var(--bg-secondary); color: var(--text-primary);";
          newReminder.innerHTML = `<div><div style="font-size: 1rem; font-weight: 500;">${data.content}</div><div style="font-size: 0.85rem; color: var(--text-secondary);">Due: ${formatDate(data.due)} — <span>${data.days_left} days left</span></div></div><button onclick="deleteReminder(${data.id})" style="background: none; border: none; color: var(--text-secondary); font-size: 1.2rem; cursor: pointer;">&times;</button>`;
          reminderList.appendChild(newReminder);
          contentInput.value = "";
          dueInput.value = "";
          showFlashMessage("Reminder added!", "success");
        } else alert(data.error || "Error adding reminder.");
      });
    });
  }

  // Pomodoro Controls
  document.getElementById("start-btn").addEventListener("click", startTimer);
  document.getElementById("reset-btn").addEventListener("click", resetTimer);

  document.querySelectorAll(".control-group")[0].querySelectorAll("button").forEach((btn, i) => {
    btn.addEventListener("click", () => adjustTime("study", i === 0 ? -1 : 1));
  });

  document.querySelectorAll(".control-group")[1].querySelectorAll("button").forEach((btn, i) => {
    btn.addEventListener("click", () => adjustTime("break", i === 0 ? -1 : 1));
  });

  updateDisplay();
});

// ---------- POMODORO TIMER ----------
let timerInterval;
let isSession = true;
let timeLeft = getStudyTime() * 60;

function updateDisplay() {
  const minutes = Math.floor(timeLeft / 60).toString().padStart(2, '0');
  const seconds = (timeLeft % 60).toString().padStart(2, '0');
  document.getElementById("time-left").textContent = `${minutes}:${seconds}`;
  document.getElementById("session-type").textContent = isSession ? "Study" : "Break";
}

function startTimer() {
  const startBtn = document.getElementById("start-btn");
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
    startBtn.textContent = "Start";
    return;
  }
  startBtn.textContent = "Stop";
  timerInterval = setInterval(() => {
    if (timeLeft > 0) {
      timeLeft--;
      updateDisplay();
    } else {
      clearInterval(timerInterval);
      timerInterval = null;
      isSession = !isSession;
      timeLeft = (isSession ? getStudyTime() : getBreakTime()) * 60;
      updateDisplay();
      startTimer();
    }
  }, 1000);
}

function resetTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
  document.getElementById("start-btn").textContent = "Start";
  isSession = true;
  timeLeft = getStudyTime() * 60;
  updateDisplay();
}

function getStudyTime() {
  return parseInt(document.getElementById("study-time").textContent);
}

function getBreakTime() {
  return parseInt(document.getElementById("break-time").textContent);
}

function adjustTime(type, delta) {
  const el = document.getElementById(`${type}-time`);
  let value = parseInt(el.textContent);
  value = Math.max(1, value + delta);
  el.textContent = value;
  if ((type === 'study' && isSession) || (type === 'break' && !isSession)) {
    timeLeft = value * 60;
    updateDisplay();
  }
}
