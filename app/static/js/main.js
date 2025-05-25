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

  let html = `
    <style>
      .custom-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 16px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      }

      .custom-table th, .custom-table td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: center;
      }

      .custom-table th {
        background-color: #f4f4f4;
        font-weight: bold;
      }

      .custom-table tr:nth-child(even) {
        background-color: #fafafa;
      }

      .custom-table tr:hover {
        background-color: #f1f1f1;
      }
    </style>
    <table class="custom-table">
      <thead>
        <tr>
          ${data.columns.map(col => `<th>${col}</th>`).join('')}
        </tr>
      </thead>
      <tbody>
        ${data.rows.map(row => `
          <tr>
            ${row.map(cell => `<td>${cell}</td>`).join('')}
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

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

          let parsedResult;

try {
  parsedResult = typeof result === 'string' ? JSON.parse(result) : result;

  if (parsedResult && typeof parsedResult === 'object' && parsedResult.result) {
    status.textContent = 'Ответ сервера: ок';
  } else {
    status.textContent = 'Ответ сервера: ' + JSON.stringify(result);
  }
} catch (e) {
  // В случае ошибки парсинга
  status.textContent = 'Ответ сервера: ' + result;
}

        } catch (err) {
          console.error('Ошибка при отправке аудио:', err);
          status.textContent = 'Ошибка при отправке аудио';
        }

        isRecording = false;
      };
    }
  });

});
