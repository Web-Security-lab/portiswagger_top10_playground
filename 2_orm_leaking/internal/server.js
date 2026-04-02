const express = require('express');
const app = express();
const PORT = process.env.PORT || 5000;
const FLAG = process.env.FLAG || 'WSL{orm_filter_oracle}';

app.get('/flag', (req, res) => {
  res.json({ flag: FLAG });
});

app.get('/health', (req, res) => {
  res.json({ ok: true });
});

app.listen(PORT, () => {
  console.log(`[+] internal note service listening on ${PORT}`);
});
