document.addEventListener('DOMContentLoaded', () => {
  const socket = io();

  const form = document.getElementById('updateForm');
  const jsonOutput = document.getElementById('jsonOutput');

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
  });
});
