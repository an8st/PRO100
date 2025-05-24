document.addEventListener('DOMContentLoaded', () => {
  const socket = io();
  let socketId; // Добавляем переменную для хранения ID сессии
  let table = '0';
  // Сохраняем ID сессии при подключении
  socket.on('connect', () => {
    socketId = socket.id;
    console.log('Connected with session ID:', socketId);
  });


  const jsonOutput = document.getElementById('jsonOutput');
  const tableContainer = document.getElementById('tableContainer');

  socket.on('table_updated', function (data) {
    jsonOutput.textContent = JSON.stringify(data, null, 2);
    renderTable(data);
  });

  function renderTable(data) {
    if (typeof data === 'string') {
      data = JSON.parse(data);
    }
    table = data.name;
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
        formData.append('table', table)

        try {
          status.textContent = 'Отправка...';
          const response = await fetch('/new_command', {
            method: 'POST',
            body: formData
          });

          const result = await response.json();  // первый уровень
          console.log(result);
          const inner = JSON.parse(result.result);
          console.log(inner);
          renderTable(inner)

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
