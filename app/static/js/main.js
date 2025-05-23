document.addEventListener('DOMContentLoaded', () => {
  const socket = io();

  const form = document.getElementById('updateForm');
  const jsonOutput = document.getElementById('jsonOutput');
  const tableContainer = document.getElementById('tableContainer');

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const row = parseInt(document.getElementById('row').value);
    const col = parseInt(document.getElementById('col').value);
    const value = document.getElementById('value').value;

    socket.emit('update_table', {
      name: name,
      row: row,
      col: col,
      value: value
    });
  });

  socket.on('table_updated', function (data) {
    jsonOutput.textContent = JSON.stringify(data, null, 2);
    renderTable(data);
  });

function renderTable(data) {
  if (typeof data === 'string') {
  data = JSON.parse(data);
}

  const tableContainer = document.getElementById('tableContainer');
  if (!tableContainer || !data || !Array.isArray(data.columns) || !Array.isArray(data.rows)) {
    tableContainer.innerHTML = '<p>Error: Invalid table format</p>';
    return;
  }

  let html = '<table border="1" cellpadding="5" cellspacing="0"><thead><tr>';
  data.columns.forEach(col => {
    html += `<th>${col}</th>`;
  });
  html += '</tr></thead><tbody>';

  data.rows.forEach(row => {
    html += '<tr>';
    row.forEach(cell => {
      html += `<td>${cell}</td>`;
    });
    html += '</tr>';
  });

  html += '</tbody></table>';
  tableContainer.innerHTML = html;
}

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

document.getElementById('micButton').addEventListener('click', async () => {
  const status = document.getElementById('micStatus');

  if (!isRecording) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);

      audioChunks = [];
      mediaRecorder.ondataavailable = event => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.start();
      isRecording = true;
      status.textContent = 'Запись... Нажмите ещё раз для остановки и отправки';
    } catch (err) {
      console.error('Ошибка доступа к микрофону:', err);
      status.textContent = 'Ошибка доступа к микрофону';
    }
  } else {
    mediaRecorder.stop();
    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('command', blob, 'recording.webm');

      try {
        status.textContent = 'Отправка...';
        const response = await fetch('/new_command', {
          method: 'POST',
          body: formData
        });

        const result = await response.json();
        status.textContent = 'Ответ сервера: ' + JSON.stringify(result);
      } catch (err) {
        console.error('Ошибка при отправке аудио:', err);
        status.textContent = 'Ошибка при отправке аудио';
      }

      isRecording = false;
    };
  }
});

});
