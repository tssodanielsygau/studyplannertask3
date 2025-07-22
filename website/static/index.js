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

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("event-form");
  const grid = document.querySelector(".events-grid");
  const modal = document.getElementById("event-modal");

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
        const addCard = document.querySelector(".event-card[onclick]");
        grid.insertBefore(newCard, addCard);

        // ✅ Fix layout/snap
        const carousel = document.getElementById('carousel');
        carousel.style.scrollSnapType = 'none';
        void carousel.offsetWidth;
        carousel.style.scrollSnapType = 'x mandatory';

        // ✅ Optional: smooth scroll to new card
        newCard.scrollIntoView({ behavior: 'smooth', inline: 'start' });

        form.reset();
        closeEventModal();
      } else {
        alert("Error adding event.");
      }
    });
  });
});

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

function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
    headers: { "Content-Type": "application/json" }
  }).then(response => response.json())
    .then(data => {
      if (data.success) {
        const noteElement = document.getElementById(`note-${noteId}`);
        if (noteElement) noteElement.remove();
      } else {
        alert("Failed to delete note.");
      }
    });
}
document.addEventListener("DOMContentLoaded", function () {
  const noteForm = document.getElementById("note-form");
  const noteInput = document.getElementById("note-input");
  const notesList = document.getElementById("notes");

  noteForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const note = noteInput.value.trim();
    if (note.length < 1) {
      alert("Note is too short.");
      return;
    }

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
        newNote.innerHTML = `
          <span>${note}</span>
          <button onclick="deleteNote(${data.note_id})"
                  style="background: none; border: none; color: var(--text-secondary); font-size: 20px; cursor: pointer;">&times;</button>
        `;
        notesList.prepend(newNote);
        noteInput.value = "";
      } else {
        alert("Error adding note.");
      }
    });
  });
});

function toggleDescription(id) {
  const desc = document.getElementById(`desc-${id}`);
  const btn = event.target;
  desc.classList.toggle('clamp');
  btn.textContent = desc.classList.contains('clamp') ? 'Read more' : 'Show less';
}

function scrollCarousel(direction) {
  const container = document.getElementById('carousel');
  const cardWidth = 280 + 16; // card width + gap
  container.scrollBy({
    left: direction * cardWidth * 4, // scroll 4 cards at a time
    behavior: 'smooth'
  });
}
