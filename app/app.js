const express = require('express');
const app = express();
const port = process.env.PORT || 8080;

const message = process.env.MESSAGE || 'Hello, World!';

app.get('/', (req, res) => {
  res.send(message);
});

app.listen(port, () => {
  console.log(`App listening on port ${port}`);
});
